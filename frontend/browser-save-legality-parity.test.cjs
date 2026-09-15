"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

window.IRON_PIT_BROWSER_STATE = { sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  autoFailStrDex: () => false,
  incapacitated: () => false,
  has: () => false,
};
window.IRON_PIT_BROWSER_TIMED = { affectedByAction: () => false };
load("browser-saves.js");

const saves = window.IRON_PIT_BROWSER_SAVES;
const actor = { combatant_id: "actor", state: {} };
const target = {
  combatant_id: "target",
  state: {
    template: { size: "medium" },
    grapple_sources: [{ source_id: "other" }],
  },
};
const action = {
  id: "grapple-save",
  name: "Grapple Save",
  range: 5,
  requiredTargetGrappledBySelf: true,
};

assert.equal(saves.legalAction(action, target, 5, actor), false);
target.state.grapple_sources = [{ source_id: "actor" }];
assert.equal(saves.legalAction(action, target, 5, actor), true);
assert.equal(saves.legalAction(action, target, 5), false);

console.log("Browser grapple-owned save legality regressions passed.");
