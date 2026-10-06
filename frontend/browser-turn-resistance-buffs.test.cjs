"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
for (const file of [
  "browser-monsters-2014.js", "browser-ability-hooks.js", "browser-opening-modifiers.js",
  "browser-condition-rules.js", "browser-grid-geometry.js", "browser-state.js",
  "browser-modifier-validation.js", "browser-modifiers.js", "browser-defensive-modifier-rules.js",
  "browser-condition-immunity.js", "browser-friendly-save-auras.js", "browser-rolls.js",
  "browser-saving-throws.js", "browser-saves.js", "browser-timed-conditions.js",
  "browser-turn-creature-effects.js", "browser-condition-lifecycle.js",
]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
let queue = [];
window.IRON_PIT_DICE = {
  roll: (sides) => { assert.equal(sides, 20); assert.ok(queue.length, "Unexpected save roll"); return queue.shift(); },
  rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
};
window.IRON_PIT_BROWSER_ZERO_HP = { reduceToZero: (state) => {
  state.current_hp = 0; state.is_dead = true; state.is_alive = false;
} };
const S = window.IRON_PIT_BROWSER_STATE;
const A = window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS;
const D = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
const T = window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS;
const member = (id, identity, side, distance) => ({ combatant_id: identity, side, position_ft: distance,
  state: S.buildState(structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014[id])) });
function fixture() {
  const source = member("2014-ghast", "source", "monsters", 10);
  const ghoul = member("2014-ghoul", "recipient", "monsters", 30);
  const other = member("2014-skeleton", "other", "monsters", 20);
  const enemy = member("2014-ghoul", "enemy", "heroes", 0);
  return { source, ghoul, other, enemy, setup: { heroes: [enemy], monsters: [source, ghoul, other] } };
}
function turn(setup, targets) {
  return T.resolve(1, 1, setup.heroes[0], targets, 14, "test-turn", "trembling", 1, "Test Turning",
    { setup, includeFrightened: false, includeIncapacitated: false });
}
{
  const { source, ghoul, other, enemy, setup } = fixture();
  const card = JSON.stringify(source.state.template);
  const aura = source.state.template.timed_self_buff_actions.find((a) => a.id === "turning-defiance");
  assert.equal(aura.activationTiming, "passive");
  assert.equal(aura.friendlySaveAdvantageAura.covers_arena, true);
  assert.deepEqual(aura.friendlySaveAdvantageAura.target_template_ids, ["2014-ghoul"]);
  A.sync(setup);
  for (const target of [source, ghoul, enemy]) {
    assert.equal(D.saveAdvantage(target.state, "wisdom", { effectTags: ["turning"] }), 1);
    assert.equal(D.saveAdvantage(target.state, "wisdom", { effectTags: ["frightened"] }), 0);
  }
  for (const target of [other]) assert.equal(D.saveAdvantage(target.state, "wisdom", { effectTags: ["turning"] }), 0);
  queue = [1, 20];
  const result = turn(setup, [ghoul]);
  assert.deepEqual(result.events[0].saving_throw_roll.rolls, [1, 20]);
  assert.match(result.events[0].description, /Turning Defiance/);
  ghoul.state.active_modifiers.push({ id: "penalty", source_id: "foe", kind: "saving-throw-disadvantage", save_ability: "wisdom" });
  queue = [20];
  assert.deepEqual(turn(setup, [ghoul]).events[0].saving_throw_roll.rolls, [20]);
  ghoul.position_ft = 100; A.sync(setup);
  assert.equal(D.saveAdvantage(ghoul.state, "wisdom", { effectTags: ["turning"] }), 1);
  assert.equal(JSON.stringify(source.state.template), card);
  assert.deepEqual(S.buildState(source.state.template).timed_effects, []);
}
{
  const { source, ghoul, enemy, setup } = fixture();
  enemy.state.template.turning_failure_destroy_max_cr = "2";
  queue = [1, 1, 20];
  const events = turn(setup, [source, ghoul]).events;
  assert.equal(source.state.is_dead, true);
  assert.deepEqual(events[1].saving_throw_roll.rolls, [20]);
  assert.doesNotMatch(events[1].description, /Turning Defiance/);
}
for (const dead of [false, true]) {
  const { source, ghoul, enemy, setup } = fixture();
  T.apply(enemy, ghoul, 1, "test-turn", "trembling", {
    includeFrightened: false, includeIncapacitated: false, repeatSaveTiming: "target_turn_end", saveDc: 14,
  });
  A.sync(setup); source.state.is_dead = dead;
  const rolls = dead ? [20] : [1, 20]; queue = [...rolls];
  const events = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE.resolveTargetTiming(1, 1, ghoul, "target_turn_end", setup).events;
  assert.deepEqual(events[0].saving_throw_roll.rolls, rolls);
  assert.equal(events[0].description.includes("Turning Defiance"), !dead);
  assert.deepEqual(events[0].removed_condition_ids, ["trembling"]);
}
{
  // Source-only Lich fixture: binding this trait does not certify its other abilities.
  const grants = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/turn-resistance-2014.json"), "utf8"));
  const template = { ...structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014["2014-skeleton"]), ...grants };
  const state = S.buildState(template);
  assert.deepEqual(D.saveAdvantageSourceNames(state, "wisdom", { effectTags: ["turning"] }), ["Turn Resistance"]);
  assert.equal(D.saveAdvantage(state, "wisdom", {}), 0);
  queue = [1, 20];
  assert.deepEqual(window.IRON_PIT_BROWSER_SAVES.resolveSavingThrow(state, "wisdom", 14, { effectTags: ["turning"] }).roll.rolls, [1, 20]);
  assert.deepEqual(S.buildState(template).active_modifiers, state.active_modifiers);
}
assert.equal(queue.length, 0);
console.log("Browser Ghast/Lich turning resistance buff regressions passed.");
