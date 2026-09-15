"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_SOURCE_BOUND_EFFECTS = { endDamageSensitive: () => {} };
window.IRON_PIT_BROWSER_CONCENTRATION = { resolveDamage: () => {} };
window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = { resolve: () => false };
load("browser-regeneration.js");
load("browser-state.js");
load("browser-zero-hp.js");

const S = window.IRON_PIT_BROWSER_STATE;
const Z = window.IRON_PIT_BROWSER_ZERO_HP;
const R = window.IRON_PIT_BROWSER_REGENERATION;
const template = {
  id: "srd-troll-limb", name: "Troll Limb", kind: "monster", size: "small", max_hp: 14,
  speed_ft: 20, traits: [], resources: {}, damage_resistances: [], damage_vulnerabilities: [],
  damage_immunities: [], condition_immunities: [],
  regeneration: { hitPoints: 5, suppressedByDamageTypes: ["acid", "fire"], diesAtStartTurnIfZeroAndSuppressed: true },
};

{
  const state = S.buildState(structuredClone(template));
  assert.equal(Z.applyDamage(state, 14, false, ["slashing"]), "damaged");
  assert.equal(state.current_hp, 0); assert.equal(state.is_dead, false);
  assert.deepEqual(R.startTurn(state), { healed: 5, died: false });
  assert.equal(state.current_hp, 5); assert.equal(state.is_alive, true);
}

{
  const state = S.buildState(structuredClone(template));
  assert.equal(Z.applyDamage(state, 14, false, ["fire"]), "damaged");
  assert.deepEqual(R.startTurn(state), { healed: 0, died: true });
  assert.equal(state.current_hp, 0); assert.equal(state.is_dead, true); assert.equal(state.is_alive, false);
}

{
  const state = S.buildState(structuredClone(template));
  Z.applyDamage(state, 4, false, ["acid"]);
  assert.deepEqual(R.startTurn(state), { healed: 0, died: false });
  assert.deepEqual(R.startTurn(state), { healed: 4, died: false });
  assert.equal(state.current_hp, 14);
}

console.log("Browser regeneration regressions passed.");
