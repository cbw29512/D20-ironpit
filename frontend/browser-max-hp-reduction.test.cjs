const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-state.js");
window.IRON_PIT_BROWSER_SAVES = { resolveSavingThrow: () => ({ roll: { total: 1 }, succeeded: false }) };
load("browser-on-hit-saves.js");

const template = {
  id: "target", name: "Target", kind: "character", max_hp: 20, armor_class: 12, speed_ft: 30,
  movement_modes: { walk_ft: 30, fly_ft: 0, climb_ft: 0, swim_ft: 0, burrow_ft: 0 },
  primary_attack_id: "sword", attacks: [{ id: "sword" }], condition_immunities: [], resources: {},
};
const target = { combatant_id: "target-1", side: "heroes", state: window.IRON_PIT_BROWSER_STATE.buildState(template) };
const attack = { id: "life-drain", onHitSaveEffect: {
  saveAbility: "constitution", dc: 14, maxHpReductionEqualsDamageTaken: true, zeroMaxHpKills: true,
} };

try {
  const result = window.IRON_PIT_BROWSER_ON_HIT_SAVES.resolve(target, attack, "specter", 1, null, 7);
  assert.equal(result.saveSucceeded, false);
  assert.equal(result.maxHpReduction, 7);
  assert.equal(target.state.max_hp_reduction, 7);
  assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(target.state), 13);

  window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow = () => ({ roll: { total: 1 }, succeeded: false });
  const lethal = window.IRON_PIT_BROWSER_ON_HIT_SAVES.resolve(target, attack, "specter", 2, null, 13);
  assert.equal(lethal.maxHpReduction, 13);
  assert.equal(window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(target.state), 0);
  assert.equal(target.state.is_dead, true);
  assert.equal(target.state.is_alive, false);
  console.log("browser max HP reduction parity tests passed");
} catch (error) {
  console.error("browser max HP reduction parity tests failed", error);
  process.exitCode = 1;
}
