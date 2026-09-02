"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
global.document = { getElementById: () => null };
global.matchMedia = () => ({ matches: true });
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8"), { filename: "battlefield-replay.js" });

const replay = window.IRON_PIT_BATTLEFIELD_REPLAY;
assert.equal(replay.conditionLabel("frightened"), "😱 FEAR");
assert.equal(replay.conditionLabel("poisoned"), "POISONED");
assert.equal(replay.concentrationLabel("bless"), "✨ CONCENTRATING · BLESS");
assert.equal(replay.concentrationLabel(null), "");

const lanes = replay.classifyStatusLanes({
  active_buff_effect_ids: ["bless"],
  active_effect_ids: ["rage", "poisoned"],
  timed_effects: [{ effect_id: "weapon-mastery-sap" }],
  active_modifiers: [
    { source_effect_id: "weapon-mastery-vex", kind: "next-attack-against-advantage", flat_bonus: 0 },
    { source_effect_id: "guiding-bolt", kind: "attacks-against-advantage", flat_bonus: 0 },
  ],
  concentration: { effect_id: "shield-of-faith" },
});
assert.deepEqual(lanes.buffs, ["bless", "rage", "weapon-mastery-vex"]);
assert.deepEqual(lanes.debuffs, ["guiding-bolt", "poisoned", "weapon-mastery-sap"]);

const view = fs.readFileSync(path.join(__dirname, "battlefield-view.js"), "utf8");
const buffLane = view.indexOf("card-status-buffs");
const debuffLane = view.indexOf("card-status-debuffs");
assert.ok(buffLane >= 0 && debuffLane > buffLane, "Buff lane must render to the left of the debuff lane.");
assert.match(view, />BUFFS</);
assert.match(view, />DEBUFFS</);

const css = fs.readFileSync(path.join(__dirname, "condition-badges.css"), "utf8");
assert.match(css, /\.card-buffs\{justify-content:flex-start\}/);
assert.match(css, /\.card-debuffs\{justify-content:flex-end\}/);
assert.match(css, /\.card-status-buffs\{text-align:left/);
assert.match(css, /\.card-status-debuffs\{text-align:right/);
assert.match(css, /\.condition-frightened/);
assert.match(css, /condition-pulse/);

console.log("Battle card buff-left/debuff-right and fear UI regressions passed.");
