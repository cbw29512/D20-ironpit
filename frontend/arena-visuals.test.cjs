"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = __dirname;
const css = fs.readFileSync(path.join(root, "battlefield.css"), "utf8");
const replay = fs.readFileSync(path.join(root, "battlefield-replay.js"), "utf8");
const view = fs.readFileSync(path.join(root, "battlefield-view.js"), "utf8");

assert.match(view, /IRON_PIT_COMBATANT_ART/, "Cards must prefer registered artwork when available.");
assert.match(view, /IRON_PIT_FIGURE_PORTRAITS/, "Cards must retain an illustrated fallback when custom art is absent.");
assert.match(css, /height:118px/, "Combatant portrait should be a prominent card panel rather than a tiny icon.");
assert.match(css, /THE IRON PIT/, "Portrait panel should carry arena identity.");
assert.match(css, /fx-melee/, "Melee actions need a card-local motion state.");
assert.match(css, /fx-ranged/, "Ranged actions need a card-local motion state.");
assert.match(css, /fx-hit/, "Hits need a target recoil state.");
assert.match(css, /condition-prone/, "Prone must have a persistent visual pose.");
assert.match(replay, /event\.event_type === "movement"/, "Movement events must drive card-local motion.");
assert.match(replay, /isRangedEvent/, "Attack animation selection must be data-driven rather than monster-specific.");
assert.match(replay, /syncConditionPose/, "Universal conditions must drive persistent card poses.");
assert.match(css, /prefers-reduced-motion:reduce/, "Arena animation must respect reduced-motion accessibility.");

console.log("Iron Pit arena card art and motion contract passed.");
