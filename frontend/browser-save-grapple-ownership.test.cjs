"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-condition-rules.js", "browser-state.js", "browser-timed-conditions.js",
  "browser-rolls.js", "browser-saves.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const V = window.IRON_PIT_BROWSER_SAVES;
const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const member = (id, side) => ({ combatant_id: id, side, position_ft: 0, state: S.buildState(structuredClone(template)) });

const actor = member("chuul-a", "monsters");
const other = member("chuul-b", "monsters");
const target = member("hero-a", "heroes");
const action = {
  id: "srd-chuul-paralyzing-tentacles",
  name: "Paralyzing Tentacles",
  range: 10,
  requiredTargetGrappledBySelf: true,
};

target.state.grapple_sources = [{ source_id: other.combatant_id, escape_dc: 14, range_ft: 10, restrains: false, linked_conditions: [] }];
assert.equal(V.legalAction(action, target, 10, actor), false,
  "a save requiring self-owned grapple must reject another creature's grapple");

target.state.grapple_sources = [{ source_id: actor.combatant_id, escape_dc: 14, range_ft: 10, restrains: false, linked_conditions: [] }];
assert.equal(V.legalAction(action, target, 10, actor), true,
  "a save requiring self-owned grapple must accept the acting creature's grapple");
assert.equal(V.legalAction(action, target, 15, actor), false, "range remains independently enforced");

console.log("Browser grapple-owned save legality regression passed.");
