"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js", "browser-saves.js", "browser-concentration.js",
]) load(file);
const M = window.IRON_PIT_BROWSER_MODIFIERS, S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK, V = window.IRON_PIT_BROWSER_SAVES, C = window.IRON_PIT_BROWSER_CONCENTRATION;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = { roll: (sides) => {
    if (!rolls.length) throw new Error("fixed dice exhausted");
    const value = rolls.shift(); if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`); return value;
  }, rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)) };
}
function member(id, side = "heroes") {
  const template = structuredClone(base); template.id = id; template.name = id; template.armor_class = 12;
  template.saving_throw_bonuses = { ...(template.saving_throw_bonuses || {}), constitution: 0 };
  return { combatant_id: id, side, position_ft: side === "heroes" ? 0 : 5, state: S.buildState(template) };
}
const modifier = (id, source, effect, kind, extra = {}) => ({ id, source_id: source, source_effect_id: effect, kind,
  flat_bonus: 0, dice_count: 0, dice_size: 0, damage_type: null, target_id: null, concentration_required: false, ...extra });
const attack = { id: "test-blade", name: "Test Blade", kind: "melee", reach: 5, bonus: 0,
  diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "slashing", onHitDamage: [], conditionalDamage: null };

{
  const attacker = member("attacker"), target = member("target", "monsters");
  M.add(target.state, modifier("shield", "caster", "shield-of-faith", "armor-class", { flat_bonus: 2, concentration_required: true }));
  dice([13]);
  assert.equal(A.resolveAttack(1, 1, attacker, target, attack, 5).hit, false);
  assert.equal(M.effectiveArmorClass(target.state), 14);
}

{
  const attacker = member("attacker"), target = member("target", "monsters");
  M.add(attacker.state, modifier("bless-attack", "attacker", "bless", "attack-roll-bonus-die", { dice_count: 1, dice_size: 4, concentration_required: true }));
  dice([10, 2, 1]);
  const event = A.resolveAttack(1, 1, attacker, target, attack, 5);
  assert.equal(event.hit, true); assert.equal(event.attack_roll.total, 12); assert.equal(event.attack_roll.notation, "1d20 + 1d4");
}

{
  const target = member("target");
  M.add(target.state, modifier("bless-save", "target", "bless", "saving-throw-bonus-die", { dice_count: 1, dice_size: 4, concentration_required: true }));
  dice([8, 2]);
  const result = V.resolveSavingThrow(target.state, "constitution", 10);
  assert.equal(result.succeeded, true); assert.equal(result.roll.total, 10);
}

{
  const target = member("target");
  M.add(target.state, modifier("slow", "enemy", "slow", "speed", { flat_bonus: -10 }));
  target.state.active_effect_ids.push("prone"); S.beginTurn(target.state);
  assert.equal(M.effectiveSpeed(target.state), 20); assert.equal(target.state.movement_remaining_ft, 10);
}

{
  const caster = member("caster"), ally = member("ally"), all = [caster.state, ally.state];
  C.start(caster.state, "caster", "bless", 1, all);
  M.add(ally.state, modifier("ally-bless", "caster", "bless", "saving-throw-bonus-die", { dice_count: 1, dice_size: 4, concentration_required: true }));
  C.start(caster.state, "caster", "shield-of-faith", 2, all);
  assert.equal(ally.state.active_modifiers.length, 0); assert.equal(caster.state.concentration.effect_id, "shield-of-faith");
}

{
  const caster = member("caster"), ally = member("ally"), all = [caster.state, ally.state];
  C.start(caster.state, "caster", "bless", 1, all);
  M.add(ally.state, modifier("ally-bless", "caster", "bless", "saving-throw-bonus-die", { dice_count: 1, dice_size: 4, concentration_required: true }));
  caster.state.temporary_hp = 20; dice([1]);
  A.applyDamage(caster.state, 10, false, ["fire"], all);
  assert.equal(caster.state.current_hp, caster.state.template.max_hp); assert.equal(caster.state.temporary_hp, 10);
  assert.equal(caster.state.concentration, null); assert.equal(ally.state.active_modifiers.length, 0);
}

assert.equal(C.concentrationDc(19), 10);
assert.equal(C.concentrationDc(20), 10);
assert.equal(C.concentrationDc(61), 30);
assert.throws(() => M.add(member("x").state, modifier("bad", "x", "bad", "armor-class", { dice_count: 1, dice_size: 4 })));

console.log("Browser universal modifier and 2024 Concentration regressions passed.");
