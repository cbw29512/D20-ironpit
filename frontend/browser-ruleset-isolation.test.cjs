"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-engine.js"), "utf8"), { filename: "browser-engine.js" });

const resolveRuleset = window.IRON_PIT_BROWSER_ENGINE.resolveRuleset;
const member = (ruleset) => ({ state: { template: ruleset ? { ruleset } : {} } });

assert.equal(resolveRuleset([member(), member("2024")]), "2024");
assert.equal(resolveRuleset([member("2014"), member("2014")]), "2014");
assert.throws(
  () => resolveRuleset([member("2014"), member("2024")]),
  /Mixed rulesets are not allowed/,
);

console.log("Browser ruleset-isolation regressions passed.");
