"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: () => true,
  effectiveMaxHp: (state) => state.max_hp,
};

let saveSucceeds = true;
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: (_state, ability, dc, options) => {
    assert.equal(ability, "strength");
    assert.equal(dc, 18);
    assert.equal(options.againstCondition, "prone");
    return {
      roll: { rolls: [saveSucceeds ? 16 : 8], modifier: 5, total: saveSucceeds ? 21 : 13 },
      succeeded: saveSucceeds,
    };
  },
};

load("browser-on-hit-save-conditions.js");
load("browser-on-hit-saves.js");

function target() {
  return {
    combatant_id: "pregen-2",
    state: {
      template: {
        name: "Pregen 2",
        creature_type: "humanoid",
        creature_subtypes: [],
      },
      current_hp: 30,
      max_hp: 30,
      is_alive: true,
      is_dead: false,
      active_effect_ids: [],
    },
  };
}

const smackDown = {
  id: "smack-down",
  name: "Smack Down",
  onHitSaveEffect: {
    conditionId: "prone",
    saveAbility: "strength",
    dc: 18,
  },
};

saveSucceeds = true;
const savedTarget = target();
const saved = window.IRON_PIT_BROWSER_ON_HIT_SAVES.resolve(savedTarget, smackDown);
assert.equal(saved.saveAbility, "strength");
assert.equal(saved.saveDc, 18);
assert.equal(saved.saveSucceeded, true);
assert.deepEqual(saved.appliedConditions, []);
assert.equal(savedTarget.state.active_effect_ids.includes("prone"), false);

saveSucceeds = false;
const failedTarget = target();
const failed = window.IRON_PIT_BROWSER_ON_HIT_SAVES.resolve(failedTarget, smackDown);
assert.equal(failed.saveSucceeded, false);
assert.deepEqual(failed.appliedConditions, ["prone"]);
assert.equal(failedTarget.state.active_effect_ids.includes("prone"), true);

// The engine resolves the same universal effect regardless of the source name.
const renamedAbility = { ...smackDown, id: "tail-sweep", name: "Tail Sweep" };
const renamedTarget = target();
const renamed = window.IRON_PIT_BROWSER_ON_HIT_SAVES.resolve(renamedTarget, renamedAbility);
assert.deepEqual(renamed.appliedConditions, ["prone"]);
assert.equal(renamedTarget.state.active_effect_ids.includes("prone"), true);

console.log("Named abilities resolve through the generic condition/save contract.");
