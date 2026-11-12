"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
for (const file of [
  "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-timed-conditions.js",
  "browser-condition-removal-policy.js", "browser-condition-removal.js",
  "browser-healing-resolution.js",
]) load(file);

const target = {
  combatant_id: "renamed-target",
  state: {
    active_effect_ids: ["renamed-disease", "curse-symptom"],
    active_curses: ["first-curse", "second-curse"],
    timed_effects: [
      {
        effect_id: "renamed-disease", source_id: "disease-source",
        removal_effect_tag: "disease", minimum_removal_spell_level: 9,
        owned_curse_ids: [],
      },
      {
        effect_id: "curse-symptom", source_id: "curse-source",
        removal_effect_tag: null, owned_curse_ids: ["first-curse", "second-curse"],
      },
    ],
    reaction_available: true,
    grapple_sources: [],
    template: { innate_condition_ids: [] },
  },
};
const renamedHealingTouch = {
  id: "renamed-healing-touch", removableConditions: [],
  removalEffectTags: ["disease"], removesAllCurses: true,
};

const removed = window.IRON_PIT_BROWSER_HEALING_RESOLUTION.applyRiders(
  target, renamedHealingTouch,
);
assert.deepEqual(removed, ["renamed-disease", "curse"]);
assert.deepEqual(target.state.active_curses, []);
assert.deepEqual(target.state.timed_effects, []);
assert.deepEqual(target.state.active_effect_ids, []);

console.log("Browser generic healing restoration riders passed.");
