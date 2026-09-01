"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
global.document = { getElementById: () => null };
global.matchMedia = () => ({ matches: true });
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8"), { filename: "battlefield-replay.js" });

assert.equal(window.IRON_PIT_BATTLEFIELD_REPLAY.conditionLabel("frightened"), "😱 FEAR");
assert.equal(window.IRON_PIT_BATTLEFIELD_REPLAY.conditionLabel("poisoned"), "POISONED");
console.log("Fear condition icon label regression passed.");
