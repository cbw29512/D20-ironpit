"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-modifiers.js",
  "browser-brutal-strike.js",
]) load(file);

const M = window.IRON_PIT_BROWSER_MODIFIERS;
const B = window.IRON_PIT_BROWSER_BRUTAL_STRIKE;

function state() {
  return { active_modifiers: [], feature_last_turn_keys: {}, template: { speed_ft: 30 }, current_hp: 10 };
}

{
  const target = state();
  assert.equal(B.staggering(target, "source"), true);
  assert.equal(target.active_modifiers.filter((item) => item.kind === "saving-throw-disadvantage").length, 1);
  assert.equal(target.active_modifiers.filter((item) => item.kind === "opportunity-attack-suppressed").length, 1);
  assert.equal(M.expireSourceTurnStart([target], "source"), 2);
  assert.equal(target.active_modifiers.length, 0);
}

{
  const target = state();
  assert.equal(B.sundering(target, "source"), true);
  assert.equal(M.nextIncomingAttackRollFlat(target, "source"), 0);
  assert.equal(M.nextIncomingAttackRollFlat(target, "ally"), 5);
  assert.equal(M.expireSourceTurnStart([target], "source"), 1);
  assert.equal(M.nextIncomingAttackRollFlat(target, "ally"), 0);
}

console.log("Browser advanced Brutal Strike effect regressions passed.");


{
  const attacker = { combatant_id: "source", state: state() }, target = { combatant_id: "target", state: state() };
  attacker.state.template.brutal_strike_effect_ids = ["forceful-blow", "hamstring-blow", "staggering-blow", "sundering-blow"];
  attacker.state.template.brutal_strike_max_effects = 1;
  attacker.state.feature_last_turn_keys["brutal-strike-hit"] = "1:source";
  assert.deepEqual(B.selectEffects(attacker.state, ["staggering-blow"]), ["staggering-blow"]);
  assert.throws(() => B.selectEffects(attacker.state, ["staggering-blow", "sundering-blow"]), /at most 1/);
  assert.deepEqual(B.applyEffects(attacker, target, null, "1:source", ["staggering-blow"]), ["staggering-blow"]);
  assert.equal(target.state.active_modifiers.filter((item) => item.kind === "saving-throw-disadvantage").length, 1);
  assert.equal(target.state.active_modifiers.filter((item) => item.kind === "opportunity-attack-suppressed").length, 1);
}

{
  const level17 = state();
  level17.template.brutal_strike_effect_ids = ["forceful-blow", "hamstring-blow", "staggering-blow", "sundering-blow"];
  level17.template.brutal_strike_max_effects = 2;
  assert.deepEqual(B.selectEffects(level17, ["staggering-blow", "sundering-blow"]), ["staggering-blow", "sundering-blow"]);
  assert.throws(() => B.selectEffects(level17, ["staggering-blow", "staggering-blow"]), /must be different/);
}
