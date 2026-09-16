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
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-fixed.js",
  "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-weapon-mastery.js",
  "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-zero-hp.js",
  "browser-graze.js", "browser-vex.js", "browser-attack.js", "browser-reactions.js",
  "browser-dodge.js", "browser-saves.js", "browser-condition-lifecycle.js", "browser-charge.js",
  "browser-light-weapons.js", "browser-light-attack.js", "browser-standard-attack-action.js",
  "browser-multiattack.js", "browser-healing.js", "browser-spellcasting.js", "browser-condition-removal.js",
  "browser-support.js", "browser-formation.js", "browser-arena-map.js", "browser-grid-geometry.js",
  "browser-grid-movement-support.js", "browser-grid-path-search-support.js", "browser-grid-path-search.js",
  "browser-grid-movement.js", "browser-grid-reaction-support.js", "browser-reaction-movement.js",
  "browser-offensive-ranges.js", "browser-offensive-movement.js", "browser-grid-placement.js",
  "browser-turn.js", "browser-initiative.js", "browser-ruleset-rosters.js", "browser-engine.js",
]) load(file);

const { resolveRuleset, selectedRuleset } = window.IRON_PIT_BROWSER_ENGINE;
const member = (ruleset) => ({ state: { template: ruleset ? { ruleset } : {} } });

assert.equal(selectedRuleset({}), "2024");
assert.equal(selectedRuleset({ ruleset: "2024" }), "2024");
assert.equal(selectedRuleset({ ruleset: "2014" }), "2014");
assert.throws(() => selectedRuleset({ ruleset: "2013" }), /Unsupported browser ruleset/);
assert.throws(() => resolveRuleset([member(), member("2024")]), /explicit ruleset identity/);
assert.equal(resolveRuleset([member("2014"), member("2014")]), "2014");
assert.equal(resolveRuleset([member("2024"), member("2024")]), "2024");
assert.throws(
  () => resolveRuleset([member("2014"), member("2024")]),
  /Mixed rulesets are not allowed/,
);

console.log("Browser ruleset-isolation regressions passed.");
require("./browser-ruleset-data.test.cjs");
require("./browser-2014-mvp.test.cjs");
require("./browser-2014-charge.test.cjs");