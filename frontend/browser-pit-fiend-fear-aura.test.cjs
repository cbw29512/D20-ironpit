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
  "browser-heroes.js", "browser-ability-hooks.js", "browser-opening-modifiers.js",
  "browser-condition-rules.js", "browser-grid-geometry.js", "browser-state.js",
  "browser-condition-immunity.js", "browser-defensive-modifier-rules.js", "browser-rolls.js",
  "browser-saving-throws.js", "browser-saves.js", "browser-timed-conditions.js",
  "browser-condition-lifecycle.js", "browser-failed-save-timed-effects.js",
  "browser-timed-emanations.js",
]) load(file);
const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_BROWSER_TIMED_EMANATIONS;
const L = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
let queue = [];
window.IRON_PIT_DICE = {
  roll: (sides) => {
    assert.equal(sides, 20);
    assert.ok(queue.length, "Unexpected save roll");
    return queue.shift();
  },
  rollMany: (count, sides) => Array.from(
    { length: count }, () => window.IRON_PIT_DICE.roll(sides),
  ),
};
const fearAction = {
  id: "renamed-dread-aura",
  name: "Renamed Dread Aura",
  actionCost: "action",
  activationTiming: "passive",
  resourceId: null,
  resourceCost: 1,
  durationRounds: null,
  conditionIds: [],
  damageResistances: [],
  expiryTiming: null,
  priority: 0,
  animation: "condition-aura",
  hostileStartTurnConditionAura: {
    trigger: "enemy_turn_start",
    radius_ft: 20,
    save_ability: "wisdom",
    save_dc: 21,
    condition_id: "frightened",
    success_immunity: true,
    source_is_magical: false,
    inactive_while_source_incapacitated: true,
    condition_duration_rounds: null,
    condition_expiry_timing: "target_turn_start",
    effect_tags: ["frightened"],
  },
};
const member = (template, id, side, position) => ({
  combatant_id: id,
  side,
  position_ft: position,
  state: S.buildState(structuredClone(template)),
});
function fixture(sourceId = "source-a", sourcePosition = 20) {
  try {
    const sourceTemplate = structuredClone(
      window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"],
    );
    sourceTemplate.id = "renamed-dread-source";
    sourceTemplate.name = "Renamed Dread Source";
    sourceTemplate.kind = "monster";
    sourceTemplate.ruleset = "2014";
    sourceTemplate.timed_self_buff_actions = [structuredClone(fearAction)];
    const targetTemplate = structuredClone(
      window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"],
    );
    targetTemplate.id = "renamed-target";
    targetTemplate.name = "Renamed Target";
    targetTemplate.ruleset = "2014";
    const source = member(sourceTemplate, sourceId, "monsters", sourcePosition);
    const target = member(targetTemplate, "target", "heroes", 0);
    return { source, target, setup: { heroes: [target], monsters: [source] } };
  } catch (error) {
    console.error("Failed to build Fear Aura browser fixture", { error });
    throw error;
  }
}
{
  const { source, target, setup } = fixture();
  const cardBefore = JSON.stringify(source.state.template);
  queue = [1];
  const failed = E.resolveStartOfTurn(1, 1, target, setup);
  assert.equal(failed.events.length, 1);
  assert.equal(failed.events[0].save_dc, 21);
  assert.equal(failed.events[0].save_ability, "wisdom");
  assert.deepEqual(failed.events[0].applied_condition_ids, ["frightened"]);
  const effect = target.state.timed_effects.find((item) => item.effect_id === "frightened");
  assert.ok(effect);
  assert.equal(effect.expiry_timing, "target_turn_start");
  const ended = L.resolveTargetTiming(failed.sequence, 1, target, "target_turn_start", setup);
  assert.deepEqual(ended.events[0].removed_condition_ids, ["frightened"]);
  assert.equal(JSON.stringify(source.state.template), cardBefore);
  assert.deepEqual(S.buildState(target.state.template).timed_effects, []);
}
{
  const { source, target, setup } = fixture();
  queue = [20];
  const passed = E.resolveStartOfTurn(1, 1, target, setup);
  assert.equal(passed.events[0].save_succeeded, true);
  assert.match(passed.events[0].description, /rest of the match/);
  queue = [];
  assert.deepEqual(E.resolveStartOfTurn(passed.sequence, 500, target, setup).events, []);
  const other = member(source.state.template, "source-b", "monsters", 20);
  setup.monsters.push(other);
  queue = [1];
  const second = E.resolveStartOfTurn(passed.sequence, 2, target, setup);
  assert.equal(second.events.length, 1);
  assert.equal(second.events[0].actor_id, "source-b");
  assert.deepEqual(S.buildState(target.state.template).timed_effects, []);
}
for (const reason of ["range", "incapacitated", "condition-immune", "dead", "ally"]) {
  const { source, target, setup } = fixture();
  if (reason === "range") source.position_ft = 25;
  if (reason === "incapacitated") source.state.active_effect_ids.push("stunned");
  if (reason === "condition-immune") target.state.template.condition_immunities = ["frightened"];
  if (reason === "dead") { source.state.is_dead = true; source.state.is_alive = false; }
  if (reason === "ally") source.side = "heroes";
  queue = [];
  assert.deepEqual(E.resolveStartOfTurn(1, 1, target, setup), { events: [], sequence: 1 });
  assert.deepEqual(target.state.timed_effects, []);
}
{
  const { target, setup } = fixture("renamed-source-id", 20);
  queue = [1];
  const result = E.resolveStartOfTurn(1, 1, target, setup);
  assert.equal(result.events[0].feature_id, "renamed-dread-aura");
  assert.match(result.events[0].description, /Renamed Dread Aura/);
}
console.log("Source-neutral hostile Frightened aura lifecycle regressions passed.");
