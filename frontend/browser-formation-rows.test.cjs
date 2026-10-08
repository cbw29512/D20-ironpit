"use strict";

require("./browser-grid-geometry.test.cjs");

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-state.js", "browser-formation.js", "browser-formation-rows.js"]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const R = window.IRON_PIT_BROWSER_FORMATION_ROWS;

const scimitar = { id: "scimitar", name: "Scimitar", kind: "melee", reach: 5 };
const shortbow = { id: "shortbow", name: "Shortbow", kind: "ranged", long: 80, normal: 80 };
const mixed = {
  id: "mixed", name: "Mixed", kind: "monster", ruleset: "2014", size: "small", max_hp: 7,
  primary_attack_id: "scimitar", attacks: [scimitar, shortbow], traits: [], resources: {},
};
const melee = {
  id: "melee", name: "Melee", kind: "character", ruleset: "2014", size: "medium", max_hp: 12,
  primary_attack_id: "scimitar", attacks: [scimitar], traits: [], resources: {},
};

const member = (id, side, template) => ({
  combatant_id: id, side, state: S.buildState(structuredClone(template)),
});

const first = member("monster-1", "monsters", mixed);
const second = member("monster-2", "monsters", mixed);
R.assignFormationRows([first, second]);
assert.equal(first.state.formation_row, "front");
assert.equal(second.state.formation_row, "back");
assert.equal(first.state.initial_formation_row, "front");
assert.equal(second.state.initial_formation_row, "back");
assert.equal(R.isBackline(first), false);
assert.equal(R.isBackline(second), true);

const front = member("hero-front", "heroes", melee);
const reserve = member("hero-back", "heroes", melee);
R.assignFormationRows([front]);
reserve.state.formation_row = "back";
reserve.state.initial_formation_row = "back";
front.state.current_hp = 0;
front.state.is_alive = false;
front.state.is_dead = true;
const promoted = R.syncFormationRows({ heroes: [front, reserve], monsters: [] });
assert.equal(promoted[0].combatant_id, "hero-back");
assert.equal(reserve.state.formation_row, "front");

const stillBack = member("ranged-back", "monsters", mixed);
stillBack.state.formation_row = "back";
stillBack.state.initial_formation_row = "back";
first.state.current_hp = 0;
first.state.is_alive = false;
first.state.is_dead = true;
assert.deepEqual(R.syncFormationRows({ heroes: [], monsters: [first, stillBack] }).map((m) => m.combatant_id), ["ranged-back"]);
assert.equal(stillBack.state.formation_row, "front");
assert.equal(stillBack.state.initial_formation_row, "back");

console.log("Browser formation-row assignment and universal backline promotion passed.");
