"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
const actor = (id, side) => ({
  combatant_id: id, side, position_ft: 0,
  state: {
    template: { name: id, creature_type: "humanoid" }, active_effect_ids: [],
    timed_effects: [], active_modifiers: [], current_hp: 10, is_alive: true,
    is_dead: false, action_available: true,
  },
});
const source = actor("source", "monsters");
const target = actor("target", "heroes");
const setup = { monsters: [source], heroes: [target] };
let lastContext;
window.IRON_PIT_BROWSER_STATE = { distance: () => 5, sizeAtMost: () => true };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  canSee: (observer) => !observer.active_effect_ids.includes("blinded"),
};
window.IRON_PIT_BROWSER_SAVING_THROWS = {
  resolveSavingThrow: (_state, _ability, _dc, context) => {
    lastContext = context;
    return { roll: { rolls: [19], total: 19 }, succeeded: false };
  },
  saveMode: () => "normal",
};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { saveAdvantageSourceNames: () => [] };
window.IRON_PIT_BROWSER_MODIFIERS = { expireTargetTurn: () => {} };
window.IRON_PIT_BROWSER_TIMED = { removeGroup: () => [] };
window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
load("browser-saves.js");
load("browser-condition-lifecycle.js");

const visual = {
  id: "renamed-gaze", name: "Renamed Gaze",
  range: 60, requiresTargetToSeeSource: true, dc: 13,
  saveAbility: "wisdom",
};
const legal = window.IRON_PIT_BROWSER_SAVES.legalAction;
assert.equal(legal(visual, target, 5, source.combatant_id, source), true);
target.state.active_effect_ids.push("blinded");
assert.equal(legal(visual, target, 5, source.combatant_id, source), false);
assert.equal(legal({ ...visual, requiresTargetToSeeSource: false }, target, 5, source.combatant_id, source), true);

const effect = {
  effect_id: "frightened", source_id: source.combatant_id, source_effect_id: visual.id,
  repeat_save_ability: "wisdom", repeat_save_dc: 13,
  repeat_save_timing: "target_turn_end",
  repeat_save_disadvantage_while_source_visible: true,
};
target.state.timed_effects = [effect];
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, target, "target_turn_end", setup);
assert.equal((lastContext.disadvantageSources || []).length, 0, "Blinded target cannot see source");

target.state.active_effect_ids = [];
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, target, "target_turn_end", setup);
assert.deepEqual(lastContext.disadvantageSources, ["visible-source"], "Visible source supplies one contextual Disadvantage");

effect.repeat_save_disadvantage_while_source_visible = false;
window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, target, "target_turn_end", setup);
assert.equal((lastContext.disadvantageSources || []).length, 0, "Ordinary repeat saves unchanged");

console.log("Source-neutral reverse sight and contextual repeat-save Disadvantage parity passed.");
