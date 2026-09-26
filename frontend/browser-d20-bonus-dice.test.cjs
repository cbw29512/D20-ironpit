"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action" ? state.bonus_action_available : state.action_available,
  spend: (state, cost) => {
    if (cost === "bonus_action") state.bonus_action_available = false;
    else state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
const rolls = [6];
window.IRON_PIT_DICE = { roll: () => rolls.shift() };
vm.runInThisContext(fs.readFileSync("frontend/browser-d20-bonus-dice.js", "utf8"));

const source = {
  combatant_id: "bard", side: "heroes", position_ft: 0,
  state: {
    template: { name: "Bard" }, resources: { "bardic-inspiration": 3 },
    bonus_action_available: true, action_available: true, is_alive: true, is_dead: false,
    active_d20_bonus_dice: [],
  },
};
const target = {
  combatant_id: "ally", side: "heroes", position_ft: 20,
  state: {
    template: { name: "Ally" }, resources: {}, bonus_action_available: true,
    action_available: true, is_alive: true, is_dead: false, active_d20_bonus_dice: [],
  },
};
const action = {
  id: "bardic-inspiration", name: "Bardic Inspiration", actionCost: "bonus_action",
  range: 60, targetMode: "other_ally", resourceId: "bardic-inspiration", resourceCost: 1,
  diceCount: 1, diceSize: 8, testKinds: ["attack", "saving_throw", "ability_check"],
  durationRounds: 100, animation: "inspiration",
};

const B = window.IRON_PIT_BROWSER_D20_BONUS_DICE;
const event = B.resolveGrant(1, 1, source, target, action);
assert.equal(event.feature_id, "bardic-inspiration");
assert.equal(source.state.resources["bardic-inspiration"], 2);
assert.equal(source.state.bonus_action_available, false);
assert.equal(target.state.active_d20_bonus_dice.length, 1);

const grant = B.eligible(target.state, "attack", 1)[0];
assert.equal(grant.dice_size, 8);
const revised = B.consume(target.state, grant, {
  notation: "1d20 + 5", rolls: [10], selected_roll: 10, modifier: 5, total: 15,
});
assert.equal(revised.total, 21);
assert.equal(target.state.active_d20_bonus_dice.length, 0);

source.state.bonus_action_available = true;
B.resolveGrant(2, 2, source, target, action);
assert.deepEqual(B.expire(target.state, 101), []);
assert.deepEqual(B.expire(target.state, 102), ["bardic-inspiration"]);

console.log("Browser d20 bonus-die lifecycle regressions passed.");
