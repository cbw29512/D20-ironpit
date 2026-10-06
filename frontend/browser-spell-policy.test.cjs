"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
// Exercise the production typed-defense resolver rather than an attack-backed stub.
for (const file of [
  "browser-damage-defense-rules.js",
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-modifier-validation.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-zero-hp.js", "browser-ability-hooks.js", "browser-attack-outcome.js", "browser-attack.js", "browser-saving-throws.js", "browser-saves.js", "browser-offense-value.js", "browser-spellcasting.js", "browser-spell-area.js",
  "browser-spell-policy-support.js", "browser-spell-policy.js", "browser-spell-resolution-effects.js", "browser-spell-resolution.js",
]) load(file);

const queuedDice = (values, fallback = 1) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_SPELL_POLICY;
const X = window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
const C = window.IRON_PIT_BROWSER_SPELLCASTING;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const spell = (id, level, areaRadius = null, range = 150, upcastDicePerLevel = 0) => ({
  id, name: id, level, actionCost: "action", range, areaRadius,
  saveAbility: "dexterity", dc: 12, damageDiceCount: 1, damageDiceSize: 6,
  damageBonus: 0, damageType: "fire", successDamage: "half",
  upcastDicePerLevel, concentration: false, animation: "spell-save",
});
const member = (id, side, position, template = base) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
function caster(spells, slots) {
  const template = structuredClone(base);
  template.spell_save_actions = spells;
  template.resources = Object.fromEntries(Object.entries(slots).map(([level, uses]) => [`spell-slot-${level}`, uses]));
  return member("caster", "heroes", 0, template);
}

{
  const c = caster([spell("fireball", 3, 20), spell("lower-bolt", 2)], { 3: 1, 2: 2 });
  const monsters = Array.from({ length: 4 }, (_, i) => member(`monster-${i}`, "monsters", 30));
  const choice = P.choose(c, { heroes: [c], monsters }, "1:caster");
  assert.equal(choice.action.id, "fireball");
  assert.equal(choice.slotLevel, 3);
  assert.equal(choice.targetIds.length, 4);
}

{
  const c = caster([spell("fireball", 3, 10), spell("lower-bolt", 2)], { 3: 1, 2: 1 });
  const ally = member("ally", "heroes", 0);
  const monsters = [member("monster-0", "monsters", 5), member("monster-1", "monsters", 5)];
  const choice = P.choose(c, { heroes: [c, ally], monsters }, "1:caster");
  assert.equal(choice.action.id, "fireball");
  assert.equal(choice.placement.friendlyIds.length, 0);
}

{
  const c = caster([spell("burst", 3, 10, 5), spell("lower-bolt", 2)], { 3: 1, 2: 1 });
  const ally = member("ally", "heroes", 0);
  const monsters = [member("monster-0", "monsters", 5), member("monster-1", "monsters", 5)];
  const choice = P.choose(c, { heroes: [c, ally], monsters }, "1:caster");
  assert.equal(choice.action.id, "lower-bolt");
}

{
  const c = caster([spell("fireball", 3, 20)], { 3: 1 });
  const monsters = Array.from({ length: 3 }, (_, i) => member(`monster-${i}`, "monsters", 5));
  const setup = { heroes: [c], monsters };
  const choice = P.choose(c, setup, "1:caster");
  window.IRON_PIT_DICE = queuedDice([1, 6, 1, 6, 1, 6]);
  const result = X.resolve(1, 1, c, setup, choice, "1:caster");
  assert.equal(result.events.length, 4);
  assert.match(result.events[0].description, /3 enemies, 0 unprotected allies, and 0 protected allies/);
  assert.deepEqual(new Set(result.events.slice(1).map((event) => event.target_id)), new Set(["monster-0", "monster-1", "monster-2"]));
  assert.equal(c.state.resources["spell-slot-3"], 0);
  assert.equal(c.state.action_available, false);
}

{
  const c = caster([spell("fireball", 3, 20), spell("spark", 0)], { 4: 1 });
  const monsters = Array.from({ length: 3 }, (_, i) => member(`monster-${i}`, "monsters", 30));
  const setup = { heroes: [c], monsters };
  const choice = P.choose(c, setup, "1:caster");
  assert.equal(choice.action.id, "spark");
  assert.equal(choice.slotLevel, 0);
  assert.equal(c.state.resources["spell-slot-4"], 1);
}

{
  const c = caster([spell("scaling-flame", 3, null, 150, 1)], { 3: 1, 4: 1 });
  const target = member("monster-0", "monsters", 30);
  target.state.template.saving_throw_bonuses.dexterity = 0;
  const setup = { heroes: [c], monsters: [target] };
  const choice = P.choose(c, setup, "1:caster");
  assert.equal(choice.action.id, "scaling-flame");
  assert.equal(choice.slotLevel, 4);
  window.IRON_PIT_DICE = queuedDice([1, 6, 5]);
  const result = X.resolve(1, 1, c, setup, choice, "1:caster");
  const saveEvent = result.events.find((event) => event.event_type === "saving_throw");
  assert.deepEqual(saveEvent.damage_components[0].rolls, [6, 5]);
  assert.equal(saveEvent.damage_roll.total, 11);
  assert.equal(c.state.resources["spell-slot-4"], 0);
  assert.equal(c.state.resources["spell-slot-3"], 1);
}

{
  const c = caster([spell("fireball", 3, 20)], { 3: 3 });
  const target = member("monster-overchannel", "monsters", 30);
  const setup = { heroes: [c], monsters: [target] };
  const grant = {
    source_id: "overchannel", source_name: "Overchannel",
    eligible_spell_ids: ["fireball"],
    minimum_spell_level: 1, maximum_spell_level: 5, safe_uses: 1,
    self_damage_dice_size: 12,
    initial_self_damage_dice_per_spell_level: 2,
    self_damage_increment_per_spell_level: 1,
    self_damage_type: "necrotic",
    ignores_resistance_and_immunity: true,
  };
  c.state.template.spell_damage_maximizer = grant;

  assert.equal(C.safeDamageMaximizer(c.state, "fireball", 3), grant);
  let result = C.resolveDamageMaximizerAfterCast(1, 1, c, setup, grant, 3);
  assert.equal(result.events.length, 0);
  assert.equal(c.state.feature_use_counts.overchannel, 1);
  assert.equal(C.safeDamageMaximizer(c.state, "fireball", 3), null);

  c.state.template.damage_immunities = ["necrotic"];
  c.state.current_hp = 50;
  const hpBeforeSecond = c.state.current_hp;
  window.IRON_PIT_DICE = queuedDice(Array(6).fill(1));
  result = C.resolveDamageMaximizerAfterCast(1, 1, c, setup, grant, 3);
  assert.equal(result.events[0].damage_roll.notation, "6d12");
  assert.equal(c.state.current_hp, hpBeforeSecond - 6);

  const hpBeforeThird = c.state.current_hp;
  window.IRON_PIT_DICE = queuedDice(Array(9).fill(1));
  result = C.resolveDamageMaximizerAfterCast(2, 1, c, setup, grant, 3);
  assert.equal(result.events[0].damage_roll.notation, "9d12");
  assert.equal(c.state.current_hp, hpBeforeThird - 9);
}

{
  const control = {
    id: "hold-person", name: "Hold Person", level: 2, actionCost: "action", range: 60,
    saveAbility: "wisdom", dc: 13, damageDiceCount: 0, damageType: null, concentration: true,
    durationMinutes: 1, animation: "spell-save",
  };
  const damage = spell("magic-bolt", 0);
  damage.damageDiceCount = 1;
  damage.damageDiceSize = 10;
  damage.damageType = "force";
  damage.successDamage = "none";
  const c = caster([control, damage], { 2: 1 });
  const choice = P.choose(c, { heroes: [c], monsters: [member("monster-0", "monsters", 30)] }, "1:caster");
  assert.equal(choice.action.id, "magic-bolt");
}

console.log("Browser spell priority, ally-safe AoE, and declared save-spell upcasting regressions passed.");
