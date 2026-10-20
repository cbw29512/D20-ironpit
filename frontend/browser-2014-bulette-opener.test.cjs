"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);

window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
  occupiedCells: (point) => [[point.x, point.y]],
};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state) => state.action_available,
  spend: (state) => { state.action_available = false; },
};
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => true,
  resolveAction: (seq, round, actor, target, action, distance, options) => ({
    sequence: seq, round_number: round, event_type: "saving_throw",
    target_id: target.combatant_id, actor_id: actor.combatant_id,
    feature_id: action.id, applied_condition_ids: [],
    damage_components: options.sharedDamageRolls.map((rolls, i) =>
      ({ damage_type: action.damageComponents[i].damageType, rolls: [...rolls] })),
    save_ability: action.saveAbility,
  }),
};
const rolls = [];
window.IRON_PIT_DICE = {
  rollMany: (count, size) => {
    rolls.push([count, size]);
    return Array.from({ length: count }, () => 3);
  },
};
load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-actions.js");
load("browser-charge.js");

function member(id, side, x, y) {
  return {
    combatant_id: id, side, position_ft: x * 5,
    state: {
      position: { x, y }, is_alive: true, is_dead: false,
      current_hp: 100, current_round: 1, initiative_total: 10,
      action_available: true, resources: {}, grapple_sources: [],
      template: { size: "medium", max_hp: 100, saving_throw_actions: [] },
    },
  };
}
const source = member("jumper", "monsters", 1, 1);
const first = member("first", "heroes", 4, 1);
const second = member("second", "heroes", 5, 2);
const outside = member("outside", "heroes", 8, 4);
const teammate = member("teammate", "monsters", 4, 2);
source.state.initiative_total = 20;
const action = {
  id: "arbitrary-opening-area", name: "Source-neutral Impact",
  openingInitiativeOnly: true, actionCost: "action", range: 30,
  area: { shape: "square", origin: "point", length_ft: 10 },
  saveAbility: "strength", saveAbilityChoices: ["strength", "dexterity"],
  dc: 16, successDamage: "half",
  damageComponents: [
    { diceCount: 3, diceSize: 6, damageBonus: 4, damageType: "bludgeoning" },
    { diceCount: 3, diceSize: 6, damageBonus: 4, damageType: "slashing" },
  ],
  failedSaveTimedEffect: { effectId: "prone" },
};
source.state.template.saving_throw_actions = [action];
const setup = {
  heroes: [first, second, outside], monsters: [source],
  map_definition: { width_squares: 12, height_squares: 12, cell_size_ft: 5 },
};
const api = window.IRON_PIT_BROWSER_AREA_SAVES;
assert.equal(api.choose(source, setup), null, "Opening action is excluded from normal Actions");
const winner = api.choose(source, setup, "action", true);
assert.ok(winner, "Strict winner has a valid opening area Action");
assert.deepEqual(new Set(winner.placement.targetIds), new Set(["first", "second"]));
assert.equal(winner.placement.direction, null);
const result = api.resolve(1, 1, source, setup, winner);
assert.deepEqual(result.events.map((row) => row.target_id), ["first", "second"]);
assert.deepEqual(rolls, [[3, 6], [3, 6]], "One roll per type, shared across affected targets");
assert.ok(result.events.every((row) =>
  row.damage_components[0].damage_type === "bludgeoning"
  && row.damage_components[1].damage_type === "slashing"));
assert.equal(source.state.action_available, false, "The opener consumes the Action, no Bite");
assert.equal(action.saveAbility, "strength", "Source card is unchanged");

source.state.action_available = true;
source.state.initiative_total = 10; // tie
assert.equal(api.choose(source, setup, "action", true), null);
assert.throws(() => api.resolve(3, 1, source, setup, winner), /winning initiative/);
source.state.initiative_total = 20;
source.state.current_round = 2;
assert.equal(api.choose(source, setup, "action", true), null);
console.log("Generic opening-only square area Action honors initiative, save card, and target damage.");
