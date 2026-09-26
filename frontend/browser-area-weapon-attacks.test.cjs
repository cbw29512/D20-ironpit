"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

let actionSpendCount = 0;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state, cost) => {
    assert.equal(cost, "action");
    state.action_available = false;
    actionSpendCount += 1;
  },
};
window.IRON_PIT_BROWSER_AREA_TARGETING = {
  legalPlacements: () => [{
    targetIds: ["target-1", "target-2", "target-3"],
    friendlyIds: [],
    origin: [40, 30],
    direction: null,
  }],
};
window.IRON_PIT_BROWSER_STATE = { distance: () => 35 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false };

const attackTargets = [];
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence, _round, _member, target, attack, _distance, options) => {
    assert.equal(options.spendAction, false);
    assert.equal(options.featureId, "volley");
    attackTargets.push(target.combatant_id);
    return {
      sequence,
      event_type: "attack",
      target_id: target.combatant_id,
      weapon_id: attack.id,
      feature_id: options.featureId,
    };
  },
};
window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH = {
  chain: (sequence, _round, _member, event) => ({ events: [event], sequence }),
};

load("browser-area-weapon-attacks.js");

const attack = { id: "rowan-2014-longbow", kind: "ranged", normal: 150, long: 600 };
const member = {
  combatant_id: "rowan",
  side: "heroes",
  state: {
    action_available: true,
    is_dead: false,
    turn_terminated: false,
    template: {
      attacks: [attack],
      attack_action: { slots: [{}, {}] },
      area_weapon_attack_actions: [{
        id: "volley",
        name: "Volley",
        attackId: attack.id,
        range: 600,
        area: { shape: "radius", origin: "point", radius_ft: 10 },
      }],
    },
  },
};
const monsters = ["target-1", "target-2", "target-3"].map((id) => ({
  combatant_id: id,
  side: "monsters",
  state: { is_alive: true, is_dead: false, template: {} },
}));
const setup = { heroes: [member], monsters, map_definition: { width_squares: 20, height_squares: 12 } };
const runtime = window.IRON_PIT_BROWSER_AREA_WEAPON_ATTACKS;

const choice = runtime.choose(member, setup);
assert.ok(choice);
assert.equal(choice.action.id, "volley");
assert.deepEqual(choice.placement.targetIds, ["target-1", "target-2", "target-3"]);

member.state.action_available = false;
assert.equal(runtime.choose(member, setup), null);
assert.ok(runtime.choose(member, setup, false), "Action Surge legality may be proved before restoring the Action");
member.state.action_available = true;

const resolved = runtime.resolve(1, 1, member, setup, choice);
assert.equal(actionSpendCount, 1);
assert.equal(member.state.action_available, false);
assert.deepEqual(attackTargets, ["target-1", "target-2", "target-3"]);
assert.equal(resolved.events.length, 3);
assert.equal(resolved.sequence, 4);
assert.ok(resolved.events.every((event) => event.feature_id === "volley"));

member.state.action_available = true;
member.state.template.attack_action = { slots: [{}, {}, {}] };
assert.equal(runtime.choose(member, setup), null, "area attack should not replace an equal-size normal Attack action");

console.log("Browser area weapon attack regressions passed.");
