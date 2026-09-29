"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_DICE = {
  values: [3, 18],
  roll: function () { return this.values.shift(); },
  rollMany: function (count) { return Array.from({ length: count }, () => this.roll()); },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
vm.runInThisContext(fs.readFileSync("frontend/browser-rolls.js", "utf8"));
vm.runInThisContext(fs.readFileSync("frontend/browser-failed-save-reroll.js", "utf8"));

const source = {
  combatant_id: "bard-7",
  side: "heroes",
  position_ft: 0,
  state: {
    template: {
      name: "Lyra",
      failed_save_reroll_grants: [{
        source_id: "countercharm",
        source_name: "Countercharm",
        resource_id: null,
        resource_cost: 1,
        action_cost: "reaction",
        target_mode: "self_or_ally",
        range_ft: 30,
        required_effect_tags: ["charmed", "frightened"],
        reroll_mode: "advantage",
      }],
    },
    resources: {},
    reaction_available: true,
  },
};
const target = {
  combatant_id: "ally",
  side: "heroes",
  position_ft: 25,
  state: {
    template: { name: "Ally", failed_save_reroll_grants: [] },
    resources: {},
    reaction_available: true,
  },
};
const enemy = {
  combatant_id: "enemy",
  side: "monsters",
  position_ft: 50,
  state: {
    template: { name: "Enemy", failed_save_reroll_grants: [] },
    resources: {},
    reaction_available: true,
  },
};
const setup = { heroes: [source, target], monsters: [enemy] };
const original = {
  notation: "1d20",
  rolls: [1],
  selected_roll: 1,
  modifier: 5,
  mode: "normal",
  total: 6,
  revisions: [],
};

const F = window.IRON_PIT_BROWSER_FAILED_SAVE_REROLL;
const result = F.apply(target.state, original, {
  effectTags: ["charmed"],
  encounterRoller: target,
  setup,
});
assert.equal(result.featureId, "countercharm");
assert.equal(result.roll.mode, "normal");
assert.equal(result.roll.selected_roll, 18);
assert.deepEqual(result.roll.rolls, [3, 18]);
assert.equal(result.roll.total, 23);
assert.equal(source.state.reaction_available, false);

source.state.reaction_available = true;
window.IRON_PIT_DICE.values = [];
const ignored = F.apply(target.state, original, {
  effectTags: ["poison"],
  encounterRoller: target,
  setup,
});
assert.equal(ignored.featureId, null);
assert.equal(source.state.reaction_available, true);
assert.deepEqual(ignored.roll, original);

console.log("Browser failed-save reroll Countercharm regressions passed.");
