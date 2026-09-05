"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-tactical-master.js", "browser-state.js", "browser-rage.js", "browser-rolls.js",
  "browser-undead-fortitude.js", "browser-zero-hp.js", "browser-attack.js",
]) load(file);

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_ATTACK;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  const rolls = [...values];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      if (!rolls.length) throw new Error("fixed dice exhausted");
      const value = rolls.shift();
      if (value < 1 || value > sides) throw new Error(`invalid d${sides}: ${value}`);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

function member(id, side, position) {
  const template = structuredClone(base);
  template.id = id; template.name = id; template.armor_class = 30;
  return { combatant_id: id, side, position_ft: position, state: S.buildState(template) };
}

const nextAttack = (expires = 2) => ({
  id: "caster:guiding-bolt:target:advantage", source_id: "caster", source_effect_id: "guiding-bolt",
  kind: "attacks-against-advantage", flat_bonus: 0, dice_count: 0, dice_size: 0,
  damage_type: null, target_id: "target", concentration_required: false,
  consume_on_attack_against: true, expires_source_turn_end_round: expires,
});

{
  const attacker = member("attacker", "heroes", 0), target = member("target", "monsters", 5);
  const attack = attacker.state.template.attacks.find((item) => item.id === attacker.state.template.primary_attack_id);
  M.add(target.state, nextAttack());
  dice([5, 15]);
  const first = A.resolveAttack(1, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(first.attack_roll.mode, "advantage");
  assert.equal(target.state.active_modifiers.length, 0);
  dice([10]);
  const second = A.resolveAttack(2, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(second.attack_roll.mode, "normal");
}

{
  const attacker = member("attacker", "heroes", 0), target = member("target", "monsters", 5);
  const ranged = attacker.state.template.attacks.find((item) => item.kind === "ranged");
  M.add(target.state, nextAttack());
  dice([10]);
  const event = A.resolveAttack(1, 1, attacker, target, ranged, 5, { spendAction: false });
  assert.equal(event.attack_roll.mode, "normal");
  assert.equal(target.state.active_modifiers.length, 0);
}

{
  const target = member("target", "monsters", 5);
  M.add(target.state, nextAttack(2));
  assert.equal(M.expireSourceTurn([target.state], "caster", 1), 0);
  assert.equal(target.state.active_modifiers.length, 1);
  assert.equal(M.expireSourceTurn([target.state], "caster", 2), 1);
  assert.equal(target.state.active_modifiers.length, 0);
}

{
  const target = member("target", "monsters", 5);
  M.applyHitEffects(target.state, "worg", {
    id: "srd-worg-bite", onHitModifiers: [{
      kind: "attacks-against-advantage", consumeOnAttackAgainst: true, expiresAtStartOfSourceTurn: true,
    }],
  });
  assert.equal(M.attacksAgainstAdvantage(target.state), 1);
  assert.equal(M.expireSourceTurnStart([target.state], "other"), 0);
  assert.equal(M.expireSourceTurnStart([target.state], "worg"), 1);
  assert.equal(target.state.active_modifiers.length, 0);
}

{
  const attacker = member("attacker", "heroes", 0), target = member("target", "monsters", 5);
  const attack = attacker.state.template.attacks.find((item) => item.id === attacker.state.template.primary_attack_id);
  M.applyHitEffects(attacker.state, "ettin", {
    id: "srd-ettin-morningstar", onHitModifiers: [{ kind: "next-attack-disadvantage", expiresAtEndOfTargetTurn: true }],
  });
  assert.equal(M.nextAttackDisadvantage(attacker.state), 1);
  dice([5, 15]);
  const event = A.resolveAttack(1, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(event.attack_roll.mode, "disadvantage");
  assert.equal(M.nextAttackDisadvantage(attacker.state), 0);
}

{
  const attacker = member("sahuagin", "monsters", 0), target = member("target", "heroes", 5);
  attacker.state.template.attack_roll_advantage_triggers = ["target_missing_hit_points"];
  let sources = A.conditionSources(attacker.state, target.state, 5, target.combatant_id);
  assert.deepEqual(sources, { advantage: 0, disadvantage: 0 });
  target.state.current_hp -= 1;
  sources = A.conditionSources(attacker.state, target.state, 5, target.combatant_id);
  assert.deepEqual(sources, { advantage: 1, disadvantage: 0 });
  assert.ok(target.state.current_hp * 2 > target.state.template.max_hp, "missing HP must not be confused with Bloodied");
  attacker.state.active_effect_ids.push("poisoned");
  sources = A.conditionSources(attacker.state, target.state, 5, target.combatant_id);
  assert.deepEqual(sources, { advantage: 1, disadvantage: 1 });
}

assert.throws(() => M.validate({
  id: "bad", source_id: "caster", source_effect_id: "bad", kind: "speed",
  flat_bonus: 5, dice_count: 0, dice_size: 0, damage_type: null,
  consume_on_attack_against: true,
}));

console.log("Browser next-attack Advantage/Disadvantage, missing-HP Advantage, and expiry regressions passed.");
