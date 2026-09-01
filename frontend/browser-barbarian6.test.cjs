"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-action-economy.js", "browser-condition-rules.js",
  "browser-condition-immunity.js", "browser-timed-conditions.js", "browser-state.js", "browser-rage.js",
]) load(file);

const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l6"]);
assert.ok(template, "Barbarian 6 must be generated as a browser-ready hero");
assert.equal(template.level, 6);
assert.equal(template.armor_class, 14);
assert.equal(template.max_hp, 65);
assert.equal(template.speed_ft, 40);
assert.equal(template.resources.rage, 4);
assert.equal(template.resources["adrenaline-rush"], 3);
assert.equal(template.fast_movement_bonus_ft, 10);
assert.equal(template.mindless_rage, true);
assert.equal(template.frenzy, true);
assert.equal(template.reckless_attack, true);
assert.equal(template.danger_sense, true);
assert.equal(template.attack_action.slots.length, 2);

const state = window.IRON_PIT_BROWSER_STATE.buildState(template);
const member = { combatant_id: "hero-1:rokhan-stonefury-l6", side: "heroes", position_ft: 5, state };
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "charmed", "source-1", { sourceEffectId: "charm-test" }), "charmed");
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "frightened", "source-2", { sourceEffectId: "fear-test" }), "frightened");
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "poisoned", "source-3", { sourceEffectId: "poison-test" }), "poisoned");
window.IRON_PIT_BROWSER_STATE.beginTurn(state);

const event = window.IRON_PIT_BROWSER_RAGE.enter(1, 1, member);
assert.ok(event);
assert.deepEqual(event.removed_condition_ids, ["charmed", "frightened"]);
assert.match(event.description, /Mindless Rage ends charmed, frightened/);
assert.ok(state.active_effect_ids.includes("rage"));
assert.ok(state.active_effect_ids.includes("poisoned"));
assert.ok(!state.active_effect_ids.includes("charmed"));
assert.ok(!state.active_effect_ids.includes("frightened"));
assert.deepEqual(state.timed_effects.map((effect) => effect.effect_id), ["poisoned"]);
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "charmed", "source-4"), null);
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "frightened", "source-5"), null);
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "poisoned", "source-6"), "poisoned");

state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "rage");
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "charmed", "source-7"), "charmed");
assert.equal(window.IRON_PIT_BROWSER_TIMED.apply(state, "frightened", "source-8"), "frightened");

console.log("Browser Barbarian 6 Mindless Rage regressions passed.");
