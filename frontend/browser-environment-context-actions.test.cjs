"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const C = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXT_ACTIONS;
const E = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
const cards = window.IRON_PIT_BROWSER_MONSTERS_2014;

const magmin = cards["2014-magmin"];
const wisp = cards["2014-will-o-wisp"];
assert.ok(magmin && wisp, "independently cleared mutable-light cards must be source-admitted");

assert.deepEqual(
  [magmin, wisp].map((card) =>
    card.environment_context_control_actions.map((action) => action.name)),
  [["Ignited Illumination"], ["Variable Illumination"]],
);
assert.deepEqual(
  wisp.environment_context_control_actions[0].modes.map((mode) => mode.emitted_contexts[0].radius_ft),
  Array.from({ length: 16 }, (_, index) => index + 5),
);

const source = {
  combatant_id: "magmin", side: "monsters", position_ft: 0,
  state: S.buildState(structuredClone(magmin)),
};
const cloakerTemplate = structuredClone(magmin);
cloakerTemplate.id = "synthetic-cloaker";
cloakerTemplate.name = "Synthetic Cloaker";
cloakerTemplate.environment_context_control_actions = [];
cloakerTemplate.environment_context_reactions = [{
  source_id: "light-sensitivity", source_name: "Light Sensitivity",
  context_id: "bright_light", disadvantage_on: ["attack_rolls"],
}];
const target = {
  combatant_id: "target", side: "heroes", position_ft: 10,
  state: S.buildState(cloakerTemplate),
};
const setup = { heroes: [target], monsters: [source] };
const action = magmin.environment_context_control_actions[0];
assert.equal(source.state.environment_context_modes[action.id], "extinguished");
const choice = C.choose(source, setup);
assert.equal(choice.action.id, action.id);
assert.equal(choice.mode.id, "ablaze");
const event = C.resolve(1, 1, source, choice.action, choice.mode, [source.state, target.state]);
assert.equal(source.state.environment_context_modes[action.id], "ablaze");
assert.equal(source.state.bonus_action_available, false);
assert.equal(E.inside(target, setup, "bright_light"), true);
assert.equal(event.feature_id, "Ignited Illumination");

const reset = S.buildState(structuredClone(magmin));
assert.equal(reset.environment_context_modes[action.id], "extinguished");
console.log("Mutable environment-context Action browser parity passed.");
