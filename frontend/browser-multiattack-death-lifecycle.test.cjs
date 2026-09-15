const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = global;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

const attacker = {
  combatant_id: "attacker",
  state: {
    action_available: true,
    is_dead: false,
    is_unconscious: false,
    turn_terminated: false,
    template: {
      attack_action: {
        id: "test-multiattack", isAttackAction: false,
        slots: [{ attackIds: ["test"] }, { attackIds: ["test"] }],
      },
    },
  },
};
const target = {
  combatant_id: "target",
  state: { is_dead: false, template: { death_trigger_effects: [{ id: "burst" }] } },
};
const setup = { heroes: [attacker], monsters: [target] };
const attack = { id: "test", kind: "melee", light: false };
let attackCalls = 0, deathCalls = 0;

window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_DICE = { roll: () => 1 };
window.IRON_PIT_BROWSER_STATE = {
  packTactics: () => false,
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_AURAS = { attackAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_CHARGE = { openingFeature: () => null };
window.IRON_PIT_BROWSER_RESOURCES = { available: () => true };
window.IRON_PIT_BROWSER_FORCED_MOVEMENT_ACTION = { legalTargets: () => [], resolve: () => ({ events: [], sequence: 1 }) };
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => false };
window.IRON_PIT_BROWSER_LIGHT_ATTACK = { resolve: (sequence) => ({ events: [], sequence }) };
window.IRON_PIT_BROWSER_WEAPON_MASTERY = {
  resolveCleave: () => { throw new Error("cleave ran after attacker died"); },
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: () => [target],
  chooseAttack: () => ({ target, attack, distance: 5 }),
  isBackline: () => false,
  alliedFrontlineActive: () => false,
  hasFrontlineTarget: () => false,
  hasBacklineTarget: () => false,
  flexibleSlotHasBoth: () => false,
};
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack: (sequence) => {
    attackCalls += 1;
    target.state.is_dead = true;
    return { sequence, event_type: "attack", target_id: target.combatant_id, is_dead: true };
  },
};
window.IRON_PIT_BROWSER_DEATH_TRIGGERS = {
  afterEvent: (sequence) => {
    deathCalls += 1;
    attacker.state.is_dead = true;
    return { events: [{ sequence, event_type: "saving_throw" }], sequence: sequence + 1 };
  },
};

load("browser-multiattack.js");
const result = window.IRON_PIT_BROWSER_MULTIATTACK.resolveAttackAction(1, 1, attacker, setup);

assert.deepEqual(result.events.map((event) => event.event_type), ["attack", "saving_throw"]);
assert.equal(attackCalls, 1);
assert.equal(deathCalls, 1);
assert.equal(result.sequence, 3);
assert.equal(attacker.state.is_dead, true);
console.log("browser multiattack death lifecycle parity: ok");
