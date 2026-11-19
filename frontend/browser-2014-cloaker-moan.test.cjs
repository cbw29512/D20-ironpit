"use strict";

const assert = require("node:assert/strict");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
require("./browser-test-runtime.cjs").loadWebsite();

const script = [
  "import json",
  "from app.content.capability_compiler import _compile_save",
  "from app.content.monster_source_2014 import load_monster_source_2014",
  "from app.content.monster_source_audible_turn_conditions_2014 import source_proven_audible_turn_conditions_2014",
  "from scripts.browser_template_serializer import _save",
  "source = next(row for row in load_monster_source_2014() if row.id == 'cloaker')",
  "definition, = source_proven_audible_turn_conditions_2014(source)",
  "print(json.dumps(_save(_compile_save(definition))))",
].join("\n");
const projectRoot = path.resolve(__dirname, "..");
const action = JSON.parse(execFileSync("python", ["-c", script], {
  cwd: projectRoot,
  encoding: "utf8",
  env: { ...process.env, PYTHONPATH: "backend:scripts" },
}));

assert.deepEqual({
  id: action.id,
  dc: action.dc,
  save: action.saveAbility,
  range: action.range,
  hearing: action.requiresTargetHearing,
  excluded: action.excludedTargetCreatureTypes,
  immunity: action.sourceEffectImmunityOnSuccess,
  effect: action.failedSaveTimedEffect.effectId,
  expiry: action.failedSaveTimedEffect.expiryTiming,
}, {
  id: "moan", dc: 13, save: "wisdom", range: 60, hearing: true,
  excluded: ["aberration"], immunity: true,
  effect: "frightened", expiry: "source_turn_end",
});

function member(id, side, type = "humanoid") {
  const template = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"]);
  template.id = id;
  template.name = id;
  template.creature_type = type;
  return {
    combatant_id: id,
    side,
    position_ft: side === "heroes" ? 5 : 0,
    state: window.IRON_PIT_BROWSER_STATE.buildState(template),
  };
}

const source = member("source", "monsters", "aberration");
const target = member("target", "heroes");
const setup = { heroes: [target], monsters: [source] };
const original = structuredClone(action);

window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow = () => ({
  roll: { natural: 1, total: 1 }, succeeded: false,
});
window.IRON_PIT_BROWSER_SAVES.resolveAction(
  1, 1, source, target, action, 5, { setup, spendAction: false },
);
assert.ok(target.state.active_effect_ids.includes("frightened"));
assert.equal(target.state.timed_effects.find((row) => row.effect_id === "frightened").expiry_timing,
  "source_turn_end");

target.state.active_effect_ids = [];
target.state.timed_effects = [];
target.state.action_available = true;
window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow = () => ({
  roll: { natural: 20, total: 20 }, succeeded: true,
});
window.IRON_PIT_BROWSER_SAVES.resolveAction(
  2, 1, source, target, action, 5, { setup, spendAction: false },
);
assert.ok(target.state.timed_effects.some((row) =>
  row.effect_id === "moan:success-immunity:source"));
assert.deepEqual(action, original, "Source-derived browser action must remain immutable.");
console.log("Cloaker Moan source binding and browser save lifecycle passed.");
