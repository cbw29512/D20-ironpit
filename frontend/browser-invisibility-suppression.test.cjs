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

window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
load("browser-effective-senses.js");
load("browser-condition-rules.js");

const C = window.IRON_PIT_BROWSER_CONDITION_RULES;
const observer = { active_effect_ids: [], timed_effects: [], active_modifiers: [] };
const target = { active_effect_ids: ["invisible"], timed_effects: [], active_modifiers: [] };

assert.equal(C.canSee(observer, target), false);
assert.equal(C.invisibilitySuppressed(target), false);

target.active_modifiers.push({
  id: "caster:faerie-fire:target:1",
  source_id: "caster",
  source_effect_id: "faerie-fire",
  kind: "invisibility-benefits-suppressed",
});

assert.equal(C.invisibilitySuppressed(target), true);
assert.equal(C.canSee(observer, target), true);

const seer = {
  active_effect_ids: [],
  timed_effects: [],
  active_modifiers: [],
  template: { blindsight_ft: 0, truesight_ft: 60, size: "medium" },
};
const hidden = {
  active_effect_ids: ["invisible"],
  timed_effects: [],
  active_modifiers: [],
  template: { blindsight_ft: 0, truesight_ft: 0, size: "medium" },
};
assert.equal(C.canSee(seer, hidden, 60), true);
assert.equal(C.canSee(seer, hidden, 65), false);
assert.equal(C.canSee(seer, hidden), false);

const blindedSeer = {
  ...seer,
  active_effect_ids: ["blinded"],
};
assert.equal(C.canSee(blindedSeer, hidden, 5), false);

const blindsightObserver = {
  active_effect_ids: ["blinded"],
  timed_effects: [],
  active_modifiers: [],
  template: { blindsight_ft: 10, truesight_ft: 0, size: "medium" },
};
assert.equal(C.canSee(blindsightObserver, hidden, 10), true);
assert.equal(C.canSee(blindsightObserver, hidden, 15), false);
assert.equal(C.effectiveSenseRangeFt(seer, "truesight"), 60);
assert.equal(C.senseIsSuppressed(seer, "truesight"), false);

const hearing = {
  active_effect_ids: ["blinded"],
  timed_effects: [],
  active_modifiers: [],
  blindsight_requires_hearing: true,
  template: {
    name: "Synthetic Hearing Blindsight",
    blindsight_ft: 30,
    truesight_ft: 0,
    blindsight_requires_hearing: true,
    size: "medium",
  },
};
assert.equal(C.canSee(hearing, hidden, 30), true);
hearing.active_effect_ids.push("deafened");
assert.equal(C.effectiveSenseRangeFt(hearing, "blindsight"), 0);
assert.equal(C.canSee(hearing, hidden, 30), false);
hearing.active_effect_ids = hearing.active_effect_ids.filter((id) => id !== "deafened");
assert.equal(hearing.template.blindsight_ft, 30);
assert.equal(C.canSee(hearing, hidden, 30), true);

console.log("Browser invisibility-benefit suppression parity passed.");
