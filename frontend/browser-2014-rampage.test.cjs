const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = global;
let spent = null;
const target = { combatant_id: "hero-2", state: {} };
const bite = { id: "bite", name: "Bite", kind: "melee" };
const member = {
  combatant_id: "hyena", side: "monsters",
  state: {
    bonus_action_available: true,
    template: { name: "Giant Hyena", traits: ["rampage"], attacks: [bite], speed_ft: 50 },
  },
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
  spend: (state, cost) => { assert.equal(cost, "bonus_action"); state.bonus_action_available = false; spent = cost; },
};
window.IRON_PIT_BROWSER_FORMATION = {
  chooseAttack: () => ({ target, attack: bite, distance: 5 }),
  targetOrder: () => [target],
};
window.IRON_PIT_BROWSER_STATE = { distance: () => 5 };
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = { moveToward: () => { throw new Error("movement should not be needed"); } };
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, round, actor, resolvedTarget, attack, distance, extra) => ({
    sequence, round_number: round, event_type: "attack", actor_id: actor.combatant_id,
    target_id: resolvedTarget.combatant_id, weapon_id: attack.id, feature_id: extra.featureId,
  }),
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-rampage.js"), "utf8"));

const prior = [{
  event_type: "attack", actor_id: "hyena", weapon_id: "bite", hp_before: 4, hp_after: 0,
}];
assert.equal(window.IRON_PIT_BROWSER_RAMPAGE.triggered(prior, member), true);
const result = window.IRON_PIT_BROWSER_RAMPAGE.resolve(2, 1, member, { heroes: [target], monsters: [member] }, prior, "1:hyena");
assert.equal(spent, "bonus_action");
assert.equal(result.sequence, 3);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "rampage");
assert.equal(result.events[0].weapon_id, "bite");
assert.equal(result.events[0].target_id, "hero-2");
console.log("2014 browser Rampage regression passed.");
