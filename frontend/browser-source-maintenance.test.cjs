"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action" && state.bonus_action_available,
  spend: (state, cost) => {
    if (cost !== "bonus_action" || !state.bonus_action_available) throw new Error("unavailable");
    state.bonus_action_available = false;
  },
};
let immunityGrants = 0;
window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = {
  grantImmunity: () => { immunityGrants += 1; },
};
load("browser-ability-hooks.js");
load("browser-timed-conditions.js");
load("browser-source-maintenance.js");

const state = (ruleset = "2014") => ({
  template: { name: "Renamed Card", ruleset, innate_condition_ids: [] },
  timed_effects: [], active_effect_ids: [], active_modifiers: [],
  turns_started: 0, bonus_action_available: true, current_round: 1,
});
const member = (id, side) => ({ combatant_id: id, side, state: state() });
const apply = (target, source, effectId) => window.IRON_PIT_BROWSER_TIMED.apply(
  target.state, "charmed", source.combatant_id, {
    sourceEffectId: effectId, sourceMaintenanceActionCost: "bonus_action",
    sourceTurnCountAtApplication: source.state.turns_started,
    sourceEffectImmunityOnEnd: true, useDefaultPoisonRecovery: false,
  },
);
const hook = (source, setup, sequence = 1) =>
  window.IRON_PIT_BROWSER_ABILITY_HOOKS.runPhase("bonusActionWindow", {
    sequence, round: 1, member: source, setup,
    turnKey: `1:${source.combatant_id}`,
    bonusActionCheckpoint: "sourceMaintenance", events: [],
  });

{
  const source = member("renamed-source", "monsters");
  const first = member("first", "heroes"), second = member("second", "heroes");
  const setup = { heroes: [first, second], monsters: [source] };
  apply(first, source, "renamed-song"); apply(second, source, "renamed-song");
  assert.equal(hook(source, setup).events.length, 0, "activation turn is free");
  source.state.turns_started = 1;
  const result = hook(source, setup);
  assert.equal(result.claimed, true);
  assert.equal(result.events[0].feature_id, "renamed-song");
  assert.equal(source.state.bonus_action_available, false);
  assert.equal(first.state.timed_effects[0].source_turn_count_at_application, 1);
}

{
  const source = member("blocked-source", "monsters");
  const target = member("target", "heroes");
  const setup = { heroes: [target], monsters: [source] };
  apply(target, source, "renamed-song");
  source.state.turns_started = 1;
  source.state.bonus_action_available = false;
  const result = hook(source, setup, 4);
  assert.equal(result.claimed, false);
  assert.deepEqual(result.events[0].removed_condition_ids, ["charmed"]);
  assert.equal(target.state.timed_effects.length, 0);
  assert.equal(immunityGrants, 0, "stopping is not a successful repeat save");
}

{
  const source = member("voluntary-source", "monsters");
  const target = member("voluntary-target", "heroes");
  const setup = { heroes: [target], monsters: [source] };
  apply(target, source, "renamed-song");
  const result = window.IRON_PIT_BROWSER_SOURCE_MAINTENANCE.stop(8, 1, source, setup);
  assert.equal(result.events.length, 1);
  assert.equal(source.state.bonus_action_available, true);
  assert.equal(target.state.timed_effects.length, 0);
}

console.log("Iron Pit browser source-maintenance regressions passed.");
