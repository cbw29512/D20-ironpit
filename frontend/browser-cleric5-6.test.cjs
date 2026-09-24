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

for (const file of [
  "browser-heroes.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-state.js", "browser-spellcasting.js", "browser-healing-policy.js", "browser-healing.js", "browser-group-healing.js",
]) load(file);

const H = window.IRON_PIT_BROWSER_HEROES;
const S = window.IRON_PIT_BROWSER_STATE;
const HEAL = window.IRON_PIT_BROWSER_HEALING;
const level5 = H["seraphine-dawnshield-l5"];
const level6 = H["seraphine-dawnshield-l6"];

assert.ok(level5);
assert.ok(level6);
assert.equal(level5.turning_failure_damage.source_id, "sear-undead");
assert.equal(level5.turning_failure_damage.ability, "wisdom");
assert.equal(level5.turning_failure_damage.dice_size, 8);
assert.equal(level5.turning_failure_damage.damage_type, "radiant");
assert.equal(level6.slot_healing_other_self_rider.source_id, "blessed-healer");
assert.equal(level6.slot_healing_other_self_rider.flat_bonus, 2);
assert.equal(level6.slot_healing_other_self_rider.per_slot_level, 1);

const mass = level6.healingActions.find((item) => item.id === "mass-healing-word");
assert.ok(mass);
assert.equal(mass.maxTargets, 6);
assert.equal(mass.resourceId, "spell-slot-3");

const member = (template, id, side = "heroes", position = 0) => ({
  combatant_id: id, side, position_ft: position,
  state: S.buildState(structuredClone(template)),
});
const cleric = member(level6, "cleric");
const ally1 = member(H["seraphine-dawnshield-l4"], "ally1", "heroes", 5);
const ally2 = member(H["seraphine-dawnshield-l4"], "ally2", "heroes", 10);
ally1.state.current_hp = 1;
ally2.state.current_hp = 2;
cleric.state.current_hp = 10;
const setup = { heroes: [cleric, ally1, ally2], monsters: [] };

let dice = [4, 4, 3, 3];
window.IRON_PIT_DICE = { roll: () => dice.shift() };
const targets = HEAL.groupTargets(cleric, setup, mass, "1:cleric");
assert.deepEqual(targets.map((item) => item.combatant_id), ["ally1", "ally2"]);
const result = HEAL.resolveGroup(1, 1, cleric, targets, mass, "1:cleric");
assert.equal(result.events.length, 3);
assert.equal(result.events.at(-1).feature_id, "blessed-healer");
assert.equal(cleric.state.current_hp, 15);
assert.equal(cleric.state.resources["spell-slot-3"], 2);
assert.equal(cleric.state.bonus_action_available, false);
assert.equal(cleric.state.action_available, true);

// Isolate the universal turning resolver: same rider data, no Cleric-name branch.
window.IRON_PIT_BROWSER_SAVES = {
  resolveSavingThrow: () => ({
    roll: { notation: "1d20", rolls: [1], modifier: 0, selected_roll: 1, total: 1, revisions: [] },
    succeeded: false,
  }),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (_state, amount) => amount,
  applyDamage: (state, amount) => { state.current_hp = Math.max(0, state.current_hp - amount); },
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
window.IRON_PIT_BROWSER_TIMED = {
  apply: (state, condition) => {
    if (!state.active_effect_ids.includes(condition)) state.active_effect_ids.push(condition);
    return condition;
  },
};
window.IRON_PIT_DICE = { roll: () => 1 };
load("browser-turn-creature-effects.js");

const source = member(level5, "source");
const undead = {
  combatant_id: "undead", side: "monsters", position_ft: 10,
  state: {
    template: { name: "Undead Test" },
    current_hp: 20, is_dead: false, active_effect_ids: [],
  },
};
const turned = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS.resolve(
  1, 1, source, [undead], 15, "turn-undead", "turned-undead", 1, "Turn Undead",
);
assert.equal(turned.events[0].damage_roll.total, 4);
assert.equal(undead.state.current_hp, 16);
assert.ok(undead.state.active_effect_ids.includes("turned-undead"));

console.log("Browser Cleric 5-6 universal Sear/healing regressions passed.");
