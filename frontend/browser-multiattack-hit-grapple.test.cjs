"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs"), path = require("node:path"), vm = require("node:vm");
global.window = globalThis;
const load = name => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name});
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
let rolls = [];
window.IRON_PIT_DICE = {
  rollMany(count, size) {
    assert.equal(size, 8);
    return Array.from({length: count}, () => rolls.shift());
  },
};
let dispatches = 0;
window.IRON_PIT_BROWSER_ATTACK = {
  applyDamage(state, amount) {
    dispatches += 1;
    state.current_hp = Math.max(0, state.current_hp - amount);
  },
};
window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
  resolveDamage: (_state, total, type) => {
    assert.equal(type, "bludgeoning");
    return {applied: total};
  },
};
let saveSuccess = true;
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: () => ({
    roll: {total: saveSuccess ? 20 : 1}, succeeded: saveSuccess,
  }),
};
load("browser-grapple.js");
load("browser-multiattack-hit-grapple.js");
load("browser-source-turn-relation-damage.js");
const slam = "2014-renamed-slam";
const hit = window.IRON_PIT_BROWSER_MULTIATTACK_HIT_GRAPPLE;
const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
const damage = window.IRON_PIT_BROWSER_SOURCE_TURN_RELATION_DAMAGE;
const rule = {
  sourceName: "Renamed Engulf", attackId: slam, requiredHits: 2,
  maxTargetSize: "medium", grappleEscapeDc: 14, grappleRangeFt: 5,
  ownershipMarkerId: "engulfed",
  linkedConditionIds: ["blinded", "unable-to-breathe", "engulfed"],
  maxActiveTargets: 1, movesWithSource: true,
};
const owner = {
  combatant_id: "owner", side: "monsters", position_ft: 0,
  state: {template: {
    name: "Mound", attack_action: {hitGrapple: rule},
    source_turn_relation_damages: [{
      source_name: "Renamed Engulf",
      target_relation: "creatures_grappled_by_source",
      dice_count: 2, dice_size: 8, damage_bonus: 4,
      damage_type: "bludgeoning", save_ability: "constitution",
      save_dc: 14, required_grapple_condition_id: "engulfed",
    }],
  }, is_alive: true, is_dead: false, current_hp: 100,
    grapple_sources: [], active_effect_ids: [], timed_effects: [],
    grapple_owned_effect_ids: []},
};
const makeTarget = id => ({
  combatant_id: id, side: "heroes", position_ft: 5,
  state: {template: {name: id, size: "medium"},
    is_alive: true, is_dead: false, current_hp: 100,
    grapple_sources: [], active_effect_ids: [], timed_effects: [],
    grapple_owned_effect_ids: [], swallowed: null},
});
const first = makeTarget("first"), second = makeTarget("second");
const setup = {heroes: [first, second], monsters: [owner]};
assert.equal(hit.resolve(1, 1, owner, setup, [{attackId: slam, targetId: "first"}]).events.length, 0);
assert.equal(hit.resolve(1, 1, owner, setup, [
  {attackId: slam, targetId: "first"}, {attackId: slam, targetId: "second"},
]).events.length, 0);
const triggered = hit.resolve(1, 1, owner, setup, [
  {attackId: slam, targetId: "first"}, {attackId: slam, targetId: "first"},
]);
assert.equal(triggered.events[0].feature_id, "Renamed Engulf");
assert.equal(triggered.sequence, 2);
assert.deepEqual(new Set(first.state.active_effect_ids),
  new Set(["grappled", "restrained", "blinded", "unable-to-breathe", "engulfed"]));
assert.equal(first.state.swallowed, null);
assert.equal(hit.resolve(2, 1, owner, setup, [
  {attackId: slam, targetId: "second"}, {attackId: slam, targetId: "second"},
]).events.length, 0);
let saved = damage.resolve(2, 2, owner, setup);
assert.equal(saved.events[0].save_succeeded, true);
assert.equal(saved.events[0].damage_components.length, 0);
assert.equal(dispatches, 0);
saveSuccess = false;
rolls = [8, 8];
const failed = damage.resolve(3, 3, owner, setup);
assert.equal(failed.events[0].save_succeeded, false);
assert.equal(failed.events[0].damage_components[0].total, 20);
assert.equal(first.state.current_hp, 80);
assert.equal(dispatches, 1);
owner.position_ft = 50;
grapple.cleanup(setup);
assert.equal(first.state.grapple_sources.length, 1);
grapple.release(first.state, "owner");
assert.equal(first.state.active_effect_ids.includes("engulfed"), false);
assert.equal(first.state.active_effect_ids.includes("blinded"), false);
assert.equal(first.state.active_effect_ids.includes("restrained"), false);
assert.equal(first.state.active_effect_ids.includes("unable-to-breathe"), false);
assert.equal(damage.resolve(4, 4, owner, setup).events.length, 0);
for (const page of ["index.html", "../index.html"]) {
  assert.ok(fs.readFileSync(path.join(__dirname, page), "utf8")
    .includes('src="browser-multiattack-hit-grapple.js"'));
}
console.log("Multiattack hit-grapple and Engulf-shaped browser parity passed.");
