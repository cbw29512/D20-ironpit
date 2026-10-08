"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters-2014.js", "browser-ability-hooks.js",
  "browser-opening-modifiers.js", "browser-condition-rules.js", "browser-grid-geometry.js", "browser-state.js",
  "browser-condition-immunity.js", "browser-defensive-modifier-rules.js", "browser-rolls.js",
  "browser-saving-throws.js", "browser-saves.js", "browser-timed-conditions.js", "browser-condition-lifecycle.js",
  "browser-failed-save-timed-effects.js", "browser-timed-emanations.js",
]) load(file);
const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_BROWSER_TIMED_EMANATIONS;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
let queue = [];
window.IRON_PIT_DICE = {
  roll: (sides) => { assert.equal(sides, 20); assert.ok(queue.length, "Unexpected save roll"); return queue.shift(); },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
const sourceTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-hezrou"]);
assert.ok(sourceTemplate, "Certified Hezrou must be exported");
const aura = sourceTemplate.timed_self_buff_actions.find((item) => item.id === "stench");
assert.equal(aura.activationTiming, "passive");
assert.equal(aura.durationRounds, null);
assert.equal(aura.hostileStartTurnConditionAura.save_dc, 14);
assert.equal(aura.hostileStartTurnConditionAura.success_immunity, true);
const member = (template, id, side, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
function fixture() {
  const target = member(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"], "hero", "heroes", 0);
  const source = member(sourceTemplate, "source-a", "monsters", 10);
  return { target, source, setup: { heroes: [target], monsters: [source] } };
}
{
  const { target, source, setup } = fixture();
  const cardBefore = JSON.stringify(source.state.template);
  queue = [1];
  const failed = E.resolveStartOfTurn(1, 1, target, setup);
  assert.deepEqual(failed.events[0].applied_condition_ids, ["poisoned"]);
  assert.match(failed.events[0].description, /Stench/);
  assert.equal(source.state.timed_effects.length, 0);
  assert.equal(source.state.action_available, true);
  const poison = target.state.timed_effects[0];
  assert.equal(poison.expires_round, null);
  assert.equal(poison.expiry_timing, "target_turn_start");
  assert.equal(poison.repeat_save_dc, null);
  const ended = L.resolveTargetTiming(failed.sequence, 1, target, "target_turn_start", setup);
  assert.deepEqual(ended.events[0].removed_condition_ids, ["poisoned"]);
  queue = [20];
  const passed = E.resolveStartOfTurn(ended.sequence, 2, target, setup);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.equal(target.state.timed_effects[0].expires_round, null);
  assert.deepEqual(E.resolveStartOfTurn(passed.sequence, 500, target, setup).events, []);
  const other = member(sourceTemplate, "source-b", "monsters", 10);
  setup.monsters.push(other);
  queue = [1];
  const second = E.resolveStartOfTurn(passed.sequence, 3, target, setup);
  assert.equal(second.events.length, 1);
  assert.equal(second.events[0].actor_id, "source-b");
  assert.equal(JSON.stringify(source.state.template), cardBefore);
  assert.deepEqual(S.buildState(target.state.template).timed_effects, []);
}
for (const reason of ["immune", "range", "dead", "ally"]) {
  const { target, source, setup } = fixture();
  if (reason === "immune") target.state.template.condition_immunities = ["poisoned"];
  if (reason === "range") source.position_ft = 15;
  if (reason === "dead") { source.state.is_dead = true; source.state.is_alive = false; }
  if (reason === "ally") source.side = "heroes";
  queue = [];
  assert.deepEqual(E.resolveStartOfTurn(1, 1, target, setup), { events: [], sequence: 1 });
  assert.deepEqual(target.state.timed_effects, []);
}
{
  const { target, setup } = fixture();
  target.state.template.damage_immunities = ["poison"];
  queue = [1];
  assert.deepEqual(E.resolveStartOfTurn(1, 1, target, setup).events[0].applied_condition_ids, ["poisoned"]);
}
for (const magical of [false, true]) {
  const { target, setup } = fixture();
  target.state.active_modifiers.push({
    kind: "saving-throw-advantage", save_ability: "constitution", source_name: "Test Ward",
    requires_magical_effect: magical, required_effect_tags: magical ? [] : ["poison"],
  });
  queue = magical ? [1] : [1, 20];
  const result = E.resolveStartOfTurn(1, 1, target, setup);
  assert.deepEqual(result.events[0].saving_throw_roll.rolls, magical ? [1] : [1, 20]);
}
{
  // The independently printed 2024 Hezrou omits success immunity.
  const rows = JSON.parse(fs.readFileSync(path.join(__dirname, "data/srd_5_2_1_monsters.json"), "utf8"));
  const text = rows.find((row) => row.name === "Hezrou").traits;
  assert.match(text, /Stench\. Constitution Saving Throw: DC 16/);
  assert.doesNotMatch(text, /Success:.*immune/);
  const { target, source, setup } = fixture();
  source.state.template.ruleset = target.state.template.ruleset = "2024";
  source.state.template.timed_self_buff_actions[0].hostileStartTurnConditionAura = {
    ...aura.hostileStartTurnConditionAura, save_dc: 16, success_immunity: false,
  };
  queue = [20, 20];
  assert.equal(E.resolveStartOfTurn(1, 1, target, setup).events[0].save_succeeded, true);
  assert.deepEqual(target.state.timed_effects, []);
  assert.equal(E.resolveStartOfTurn(2, 2, target, setup).events[0].save_succeeded, true);
}
{
  const { target, setup } = fixture();
  queue = [1];
  const result = window.IRON_PIT_BROWSER_ABILITY_HOOKS.runPhase("turnStart", {
    sequence: 1, round: 1, member: target, setup, events: [],
  });
  assert.equal(result.events[0].feature_id, "stench");
  assert.equal(result.claimed, false);
}
console.log("Shared passive condition aura source, immunity, expiry, reset and edition regressions passed.");
for (const [x, expected] of [[2, 1], [3, 0]]) {
  const { target, source, setup } = fixture();
  source.state.position = { x: 0, y: 0 };
  target.state.position = { x, y: 0 };
  queue = expected ? [1] : [];
  const result = E.resolveStartOfTurn(1, 1, target, setup);
  assert.equal(result.events.length, expected);
  if (expected) assert.equal(result.events[0].distance_before_ft, 10);
}
