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

load("browser-state.js");
load("browser-damaging-action-riders.js");

const template = {
  name: "Cleric",
  max_hp: 73,
  traits: [],
  ability_scores: { wisdom: 20 },
  damaging_action_temporary_hp_rider: {
    source_id: "improved-blessed-strikes",
    source_name: "Improved Blessed Strikes",
    action_ids: ["sacred-flame"],
    ability: "wisdom",
    multiplier: 2,
    range_ft: 60,
    target_mode: "self_or_ally",
  },
};
const state = (name, hp, maxHp = 73, temporaryHp = 0) => ({
  template: { ...template, name, max_hp: maxHp },
  current_hp: hp,
  max_hp_bonus: 0,
  temporary_hp: temporaryHp,
  is_dead: false,
});
const cleric = { combatant_id: "cleric", side: "heroes", position_ft: 0, state: state("Cleric", 73) };
const wounded = { combatant_id: "ally", side: "heroes", position_ft: 40, state: state("Ally", 10, 60) };
const far = { combatant_id: "far", side: "heroes", position_ft: 65, state: state("Far Ally", 1, 60) };
const enemy = { combatant_id: "enemy", side: "monsters", position_ft: 30, state: state("Enemy", 20, 20) };
const setup = { heroes: [cleric, wounded, far], monsters: [enemy] };
const damageEvents = [{ damage_components: [{ applied_total: 4 }] }];

const event = window.IRON_PIT_BROWSER_DAMAGING_ACTION_RIDERS.resolve(
  5, 2, cleric, setup, "sacred-flame", damageEvents,
);
assert.ok(event);
assert.equal(event.target_id, "ally");
assert.equal(wounded.state.temporary_hp, 10);
assert.equal(far.state.temporary_hp, 0);
assert.equal(event.feature_id, "improved-blessed-strikes");

assert.equal(
  window.IRON_PIT_BROWSER_DAMAGING_ACTION_RIDERS.resolve(
    6, 2, cleric, setup, "sacred-flame", [{ damage_components: [{ applied_total: 0 }] }],
  ),
  null,
);

wounded.state.temporary_hp = 10;
cleric.state.temporary_hp = 10;
assert.equal(
  window.IRON_PIT_BROWSER_DAMAGING_ACTION_RIDERS.resolve(
    7, 2, cleric, setup, "sacred-flame", damageEvents,
  ),
  null,
);

console.log("Browser generic damaging-action Temporary HP rider regressions passed.");
