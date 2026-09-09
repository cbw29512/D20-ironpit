"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "action" && state.action_available,
  spend: (state, cost) => {
    if (cost !== "action" || !state.action_available) throw new Error("Action unavailable");
    state.action_available = false;
  },
};
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => Boolean(state.is_unconscious) };
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: (state) => Boolean(state.speed_zero) };
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: (state) => state.template.speed_ft };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_ROLLS = {
  modeFromSources: (advantage, disadvantage) => {
    if (Boolean(advantage) === Boolean(disadvantage)) return "normal";
    return advantage ? "advantage" : "disadvantage";
  },
};

load("browser-dodge.js");
load("browser-saves.js");

const actor = {
  combatant_id: "monster-1:test",
  state: {
    action_available: true,
    is_unconscious: false,
    speed_zero: false,
    active_effect_ids: [],
    template: { name: "Test Monster", speed_ft: 30 },
  },
};

const dodge = window.IRON_PIT_BROWSER_DODGE;
const saves = window.IRON_PIT_BROWSER_SAVES;
const event = dodge.take(1, 1, actor);

assert.equal(actor.state.action_available, false);
assert.equal(event.feature_id, "dodge");
assert.equal(dodge.benefitsActive(actor.state), true);
assert.equal(dodge.dexSaveAdvantageSources(actor.state, "dexterity"), 1);
assert.equal(dodge.dexSaveAdvantageSources(actor.state, "constitution"), 0);
assert.equal(saves.saveMode(actor.state, "dexterity"), "advantage");
assert.equal(saves.saveMode(actor.state, "constitution"), "normal");

actor.state.speed_zero = true;
assert.equal(dodge.benefitsActive(actor.state), false);
assert.equal(saves.saveMode(actor.state, "dexterity"), "normal");

console.log("Browser Dodge parity regressions passed.");
