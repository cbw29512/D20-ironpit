"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-action-economy.js", "browser-spellcasting.js", "browser-condition-removal.js"]) load(file);

const C = window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
const wake = {
  id: "wake-sleeper", name: "Wake Sleeper", actionCost: "action", range: 5,
  targetMode: "ally", removableConditions: ["unconscious"], maxConditionsPerUse: 1,
  resourceCosts: {}, resourceCostsPerCondition: {}, expendsSpellSlot: false,
  requiresSourcePermission: true,
};
const member = (id, removals = []) => ({
  combatant_id: id, side: "heroes", position_ft: 0,
  state: {
    current_hp: 10, is_alive: true, is_dead: false,
    action_available: true, bonus_action_available: true, reaction_available: true,
    active_effect_ids: [], timed_effects: [], resources: {}, spell_slot_expended_turn_key: null,
    template: { name: id, condition_removal_actions: removals },
  },
});

{
  const remover = member("ally", [wake]);
  const target = member("sleeping");
  target.state.active_effect_ids = ["unconscious"];
  target.state.timed_effects = [{
    effect_id: "unconscious", source_id: "other", source_effect_id: "unrelated-unconscious",
    allowed_removal_action_ids: [],
  }];
  assert.equal(C.chooseAction(remover, { heroes: [remover, target], monsters: [] }, "1:ally"), null);
}

{
  const remover = member("ally", [wake]);
  const target = member("sleeping");
  target.state.active_effect_ids = ["unconscious"];
  target.state.timed_effects = [{
    effect_id: "unconscious", source_id: "brass-dragon", source_effect_id: "sleep-breath",
    allowed_removal_action_ids: ["wake-sleeper"],
  }];
  const choice = C.chooseAction(remover, { heroes: [remover, target], monsters: [] }, "1:ally");
  assert.ok(choice);
  assert.equal(choice.action.id, "wake-sleeper");
  assert.deepEqual(choice.conditions, ["unconscious"]);
}

console.log("Browser Wake Sleeper source-permission regressions passed.");
