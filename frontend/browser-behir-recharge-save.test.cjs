"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
const report = JSON.parse(fs.readFileSync(
  path.join(__dirname, "..", "docs", "generated", "RECHARGE_SAVE_HALF_DAMAGE_BINDINGS_2014.json"),
  "utf8",
));
const row = report.bindings.find((item) => item.card_id === "behir");
assert.ok(row && row.python_wired && row.browser_wired);

window.IRON_PIT_BROWSER_GRID_GEOMETRY = { occupiedCells: (position) => [[position.x, position.y]] };
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => Boolean(state[`${cost}_available`]),
  spend: (state, cost) => { state[`${cost}_available`] = false; },
};
const affected = [];
window.IRON_PIT_BROWSER_SAVES = {
  legalAction: () => true,
  resolveAction: (sequence, round, actor, target, action, distance, options) => {
    affected.push(target.combatant_id);
    return { sequence, round_number: round, event_type: "saving_throw", actor_id: actor.combatant_id,
      target_id: target.combatant_id, resource_remaining: options.resourceRemaining };
  },
};
window.IRON_PIT_DICE = { rollMany: () => Array(12).fill(5), roll: () => 5 };
load("browser-area-shapes.js");
load("browser-area-targeting.js");
load("browser-area-save-choice.js");\nload("browser-area-save-actions.js");
load("browser-recharge.js");

const member = (id, side, x, y) => ({
  combatant_id: id, side, position_ft: x * 5,
  state: { position: { x, y }, is_alive: true, is_dead: false, current_hp: 100,
    action_available: true, bonus_action_available: true, resources: {},
    template: { size: "huge", max_hp: 100, saving_throw_actions: [], recharge_rules: [] } },
});
const actor = member("monster:behir", "monsters", 1, 1);
const first = member("hero:first", "heroes", 2, 1);
const second = member("hero:second", "heroes", 4, 1);
const p = row.parameters;
actor.state.template.saving_throw_actions = [{
  id: "lightning-breath", name: "Lightning Breath", saveAbility: p.save_ability, dc: p.dc,
  range: p.range_ft, area: p.area, damageDiceCount: 12, damageDiceSize: 10,
  damageType: p.damage_type, successDamage: p.success_damage,
  resourceId: "lightning-breath", resourceCost: 1,
}];
actor.state.template.recharge_rules = [{ resourceId: "lightning-breath", minimumRoll: p.recharge_minimum, dieSize: 6 }];
actor.state.resources["lightning-breath"] = 1;
const setup = { heroes: [first, second], monsters: [actor], map_definition: { width_squares: 10, height_squares: 10 } };
const selected = window.IRON_PIT_BROWSER_AREA_SAVES.choose(actor, setup);
assert.ok(selected);
window.IRON_PIT_BROWSER_AREA_SAVES.resolve(1, 1, actor, setup, selected);
assert.deepEqual(new Set(affected), new Set(["hero:first", "hero:second"]));
assert.equal(actor.state.resources["lightning-breath"], 0);
actor.state.action_available = true;
const recharge = window.IRON_PIT_BROWSER_RECHARGE.resolveStartOfTurn(3, 2, actor);
assert.equal(recharge.events[0].recharge_succeeded, true);
assert.equal(actor.state.resources["lightning-breath"], 1);

console.log("Behir source-bound Recharge line-save browser parity passed.");
