"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
global.window = globalThis;
const load = name => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));
load("browser-turn-start-visual-policy.js");
load("browser-visual-source-aversion.js");
const policy = window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY;
const rider = { effectId: "frightened", durationRounds: 10, expiryTiming: "target_turn_end",
  repeatSaveAbility: "wisdom", repeatSaveDc: 11, repeatSaveTiming: "target_turn_end",
  repeatSaveDisadvantageWhileSourceVisible: true, sourceEffectImmunityOnEnd: true };
const rule = { sourceId: "visual-fear-source", sourceName: "Renamed Gaze",
  rangeFt: 30, saveDc: 11, saveAbility: "wisdom",
  requiredTargetCreatureTypes: ["humanoid"], requiresSourceSight: false,
  requiresSourceNotIncapacitated: false, requiresTrueFormVisibility: true,
  sourceEffectImmunityOnSuccess: true, failedSaveTimedEffect: rider };
const mk = (id, type, visual = null) => ({ combatant_id: id, side: id === "victim" ? "heroes" : "monsters",
  state: { template: { name: id, creature_type: type, visualTurnStartRule: visual },
    current_hp: 10, is_dead: false, true_form_visible: true, turns_started: 1,
    timed_effects: [], active_effect_ids: [] } });
const source = mk("source", "fey", rule), target = mk("victim", "humanoid");
const setup = { heroes: [target], monsters: [source] };
window.IRON_PIT_BROWSER_STATE = { distance: () => 10 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: () => false, canSee: () => true };
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune: () => false };
let succeeds = false, saves = 0, timed = 0, immunity = 0;
window.IRON_PIT_BROWSER_SAVING_THROWS = { resolveSavingThrow: () => {
  saves++; return { roll: { total: succeeds ? 20 : 1 }, succeeded: succeeds }; } };
window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = {
  isImmune: () => immunity > 0,
  grantImmunity: () => { immunity++; },
  apply: (_source, actor, _action, effect) => {
    timed++;
    actor.state.timed_effects.push({ source_id: "source", source_effect_id: rule.sourceId, effect_id: effect.effectId });
    return effect.effectId;
  },
};
load("browser-visual-turn-start-integration.js");
const run = turn_order => window.IRON_PIT_BROWSER_VISUAL_TURN_START_INTEGRATION.resolve({
  member: target, setup, sequence: 0, round: 1, initiative: { turn_order },
});
let result = run(["source", "victim"]);
assert.deepEqual(result.events[0].applied_condition_ids, ["frightened"]);
assert.equal(timed, 1);
result = run(["source", "victim"]);
assert.equal(result.events.length, 0, "Do not repeat initial saves while active.");
target.state.timed_effects = [];
succeeds = true;
result = run(["source", "victim"]);
assert.equal(result.events[0].save_succeeded, true);
assert.equal(immunity, 1);
assert.equal(run(["source", "victim"]).events.length, 0, "Initial success establishes source immunity.");
immunity = 0; succeeds = false;
source.state.true_form_visible = false;
assert.equal(run(["source", "victim"]).events.length, 0, "Hidden true form cannot trigger fear.");
source.state.true_form_visible = true;
target.state.template.creature_type = "undead";
assert.equal(run(["source", "victim"]).events.length, 0, "Undead fails humanoid requirement.");
target.state.template.creature_type = "humanoid";
assert.equal(run(["victim", "source"]).events[0].event_type, "feature");
assert.ok(target.state.visual_aversion_windows.length);
assert.equal(policy.validate(rule), rule);
const view = window.IRON_PIT_BROWSER_VISUAL_TURN_START_INTEGRATION.observerSeesTrueForm;
window.IRON_PIT_BROWSER_EFFECTIVE_SENSES = { effectiveSenseRangeFt: (state) =>
  state.suppressed_sense_ids?.includes("truesight") ? 0 : (state.template.truesight_ft || 0) };
source.state.magical_visual_disguise_active = true;
assert.equal(view(source, target, 10), false, "Ordinary vision sees the illusion.");
target.state.template.truesight_ft = 15;
assert.equal(view(source, target, 10), true, "Truesight sees through a magical disguise.");
target.state.template.truesight_ft = 5;
assert.equal(view(source, target, 10), false, "Truesight must reach the source.");
target.state.template.truesight_ft = 15;
target.state.suppressed_sense_ids = ["truesight"];
assert.equal(view(source, target, 10), false, "Suppressed senses cannot bypass a disguise.");
target.state.suppressed_sense_ids = [];
source.state.true_form_visible = false;
assert.equal(view(source, target, 10), false, "Separately hidden true form stays hidden.");
assert.throws(() => view(source, target, -1), /distance/);
console.log("Universal 2014 passive visual fear timing/eligibility/immunity checks passed.");
