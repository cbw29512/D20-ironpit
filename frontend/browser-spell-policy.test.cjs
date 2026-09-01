"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-zero-hp.js", "browser-attack.js", "browser-saves.js", "browser-spellcasting.js", "browser-spell-area.js",
  "browser-spell-policy.js", "browser-spell-resolution.js",
]) load(file);

const queuedDice = (values, fallback = 1) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};
const S = window.IRON_PIT_BROWSER_STATE;
const P = window.IRON_PIT_BROWSER_SPELL_POLICY;
const X = window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
const spell = (id, level, areaRadius = null, upcast = 0) => ({
  id, name: id, level, actionCost: "action", range: 150, areaRadius,
  saveAbility: "dexterity", dc: 12, damageDiceCount: 1, damageDiceSize: 6,
  damageBonus: 0, damageType: "fire", successDamage: "half", upcastDicePerLevel: upcast,
  concentration: false, animation: "spell-save",
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
  assert.equal(choice.action.id, "lower-bolt");
}

{
  const c = caster([spell("fireball", 3, 20)], { 3: 1 });
  const monsters = Array.from({ length: 3 }, (_, i) => member(`monster-${i}`, "monsters", 5));
  const setup = { heroes: [c], monsters };
  const choice = P.choose(c, setup, "1:caster");
  window.IRON_PIT_DICE = queuedDice([1, 6, 1, 6, 1, 6, 1, 6]);
  const result = X.resolve(1, 1, c, setup, choice, "1:caster");
  assert.equal(result.events.length, 5);
  assert.match(result.events[0].description, /3 enemies and 1 unprotected allies/);
  assert.deepEqual(new Set(result.events.slice(1).map((event) => event.target_id)), new Set(["caster", "monster-0", "monster-1", "monster-2"]));
  assert.equal(c.state.resources["spell-slot-3"], 0);
  assert.equal(c.state.action_available, false);
}

{
  const c = caster([spell("fireball", 3, 20, 1), spell("spark", 0)], { 4: 1 });
  const monsters = Array.from({ length: 3 }, (_, i) => member(`monster-${i}`, "monsters", 30));
  const setup = { heroes: [c], monsters };
  assert.equal(P.choose(c, setup, "1:caster").slotLevel, 4);
  window.IRON_PIT_BROWSER_SPELLCASTING.markSlotSpellCast(c.state, "1:caster");
  const choice = P.choose(c, setup, "1:caster");
  assert.equal(choice.action.id, "spark");
  assert.equal(choice.slotLevel, 0);
}

console.log("Browser spell priority and friendly-fire regressions passed.");
