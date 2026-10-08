"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-attack.js"), "utf8"), { filename: "browser-attack.js" });
const source = window.IRON_PIT_BROWSER_ATTACK.firstTurnTargetAdvantageSources;
const attacker = { template: { advantage_against_unacted_targets: true } };
const target = { turns_started: 0 };
assert.equal(source(attacker, target), 1, "before first turn");
target.turns_started = 1;
assert.equal(source(attacker, target), 0, "after first turn");
target.turns_started = 0;
attacker.template.advantage_against_unacted_targets = false;
assert.equal(source(attacker, target), 0, "ability not granted");
console.log("Generic first-turn Advantage browser checks passed.");
