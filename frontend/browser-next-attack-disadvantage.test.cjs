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

{
  const attacker = member("attacker", "heroes", 0), target = member("target", "monsters", 5);
  const attack = attacker.state.template.attacks.find((item) => item.id === attacker.state.template.primary_attack_id);
  M.applyEffect(attacker.state, "generic-source", "generic-rider", {
    kind: "next-attack-disadvantage", expiresAtEndOfTargetTurn: true,
  }, 0, "hit");
  assert.equal(M.nextAttackDisadvantage(attacker.state), 1);

  dice([18, 2]);
  const first = A.resolveAttack(1, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(first.attack_roll.mode, "disadvantage");
  assert.equal(first.attack_roll.selected_roll, 2);
  assert.equal(M.nextAttackDisadvantage(attacker.state), 0);

  dice([10]);
  const second = A.resolveAttack(2, 1, attacker, target, attack, 5, { spendAction: false });
  assert.equal(second.attack_roll.mode, "normal");
}

assert.throws(() => M.validate({
  id: "bad", source_id: "source", source_effect_id: "effect", kind: "next-attack-disadvantage",
  flat_bonus: 1, dice_count: 0, dice_size: 0, damage_type: null,
}));

console.log("Browser source-neutral next-attack Disadvantage regressions passed.");
