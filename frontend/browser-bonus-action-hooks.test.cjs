"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_BROWSER_CONDITION_RULES = { incapacitated: (state) => Boolean(state.is_unconscious) };
window.IRON_PIT_BROWSER_EXHAUSTION = { gain: () => 1 };
window.IRON_PIT_BROWSER_STATE = {
  grantTemporaryHp(state, amount) { state.temporary_hp = Math.max(state.temporary_hp || 0, amount); },
};
window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync: () => {} };
let shiftCalls = 0;
window.IRON_PIT_BROWSER_TACTICAL_SHIFT = {
  resolve(sequence, round, member) {
    shiftCalls += 1;
    if (!(member.state.template.tactical_shift_fraction > 0)) return null;
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, feature_id: "tactical-shift", description: "Tactical Shift rider." };
  },
};
window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT = {
  resolve(sequence) { return { events: [], sequence }; },
};

load("browser-action-economy.js");
load("browser-ability-hooks.js");
load("browser-rage.js");
load("browser-support.js");
load("browser-ability-hook-installation.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const phase = H.PHASES.BONUS_ACTION_WINDOW;
const registrations = H.abilitiesFor(phase).map((item) => [item.id, item.priority, item.rulesets]);
assert.deepEqual(registrations, [
  ["rage-enter", 10, ["2014", "2024"]],
  ["second-wind", 20, ["2014", "2024"]],
  ["adrenaline-rush", 30, ["2024"]],
]);

function baseState(template, resources = {}) {
  return {
    template,
    current_hp: template.max_hp,
    temporary_hp: 0,
    resources: { ...resources },
    active_effect_ids: [],
    timed_effects: [],
    temporary_damage_resistances: [],
    action_available: true,
    bonus_action_available: true,
    reaction_available: true,
    is_dead: false,
    is_unconscious: false,
    rage_expires_round: null,
    rage_max_round: null,
  };
}
const member = (id, template, resources) => ({
  combatant_id: id, side: "heroes", position_ft: 0, state: baseState(template, resources),
});
const run = (actor, bonusActionCheckpoint, round = 1) => H.runPhase(phase, {
  sequence: 1, round, member: actor, setup: { heroes: [actor], monsters: [] },
  turnKey: `${round}:${actor.combatant_id}`, bonusActionCheckpoint, events: [],
});

{
  const barbarian = member("barbarian", {
    name: "Barbarian", ruleset: "2024", max_hp: 60, level: 6, traits: ["adrenaline-rush"],
    wearing_heavy_armor: false, rage_damage_bonus: 2, frenzy_bonus_attack_2014: false,
    mindless_rage: false, instinctive_pounce_fraction: 0,
  }, { rage: 4, "adrenaline-rush": 3 });
  const result = run(barbarian, "beforeEscape");
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["rage"]);
  assert.equal(barbarian.state.resources.rage, 3);
  assert.equal(barbarian.state.resources["adrenaline-rush"], 3, "Rage must retain its existing priority over Adrenaline Rush");
}

{
  shiftCalls = 0;
  const fighter = member("fighter", {
    name: "Fighter", ruleset: "2024", max_hp: 40, level: 4, traits: ["adrenaline-rush"],
    wearing_heavy_armor: false, rage_damage_bonus: 0, tactical_shift_fraction: 0.5,
  }, { "second-wind": 3, "adrenaline-rush": 2 });
  fighter.state.current_hp = 20;
  window.IRON_PIT_DICE = { roll: () => 5 };
  const result = run(fighter, "beforeEscape");
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["second-wind", "tactical-shift"]);
  assert.equal(shiftCalls, 1, "Tactical Shift remains a rider on Second Wind");
  assert.equal(fighter.state.resources["second-wind"], 2);
  assert.equal(fighter.state.resources["adrenaline-rush"], 2, "Second Wind must retain priority over Adrenaline Rush");
}

{
  const fighter = member("healthy-fighter", {
    name: "Healthy Fighter", ruleset: "2024", max_hp: 40, level: 4, traits: ["adrenaline-rush"],
    wearing_heavy_armor: false, rage_damage_bonus: 0, tactical_shift_fraction: 0,
  }, { "second-wind": 3, "adrenaline-rush": 2 });
  const beforeEscape = run(fighter, "beforeEscape");
  assert.deepEqual(beforeEscape.events, [], "Adrenaline Rush must wait until after the grapple-escape checkpoint");
  const result = run(fighter, "afterEscape");
  assert.deepEqual(result.events.map((event) => event.feature_id), ["adrenaline-rush"]);
  assert.equal(fighter.state.resources["second-wind"], 3);
  assert.equal(fighter.state.resources["adrenaline-rush"], 1);
  assert.equal(fighter.state.temporary_hp, 2);
}

{
  const legacy = member("legacy", {
    name: "Legacy", ruleset: "2014", max_hp: 30, level: 4, traits: ["adrenaline-rush"],
    wearing_heavy_armor: false, rage_damage_bonus: 0, tactical_shift_fraction: 0,
  }, { "adrenaline-rush": 2 });
  const result = run(legacy, "afterEscape");
  assert.deepEqual(result.events, [], "2024-only Adrenaline Rush must not cross into the 2014 ruleset");
  assert.equal(result.claimed, false);
}

const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.match(turnSource, /BONUS_ACTION_WINDOW/);
assert.match(turnSource, /runPhase/);
assert.doesNotMatch(turnSource, /\.secondWind\(/);
assert.doesNotMatch(turnSource, /\.adrenaline\(/);
assert.doesNotMatch(turnSource, /\?\.enter\(/);
assert.doesNotMatch(turnSource, /IRON_PIT_BROWSER_TACTICAL_SHIFT/);
assert.doesNotMatch(turnSource, /IRON_PIT_BROWSER_ACTIVATION_MOVEMENT/);
const beforeEscapeIndex = turnSource.indexOf('"beforeEscape"');
const grappleEscapeIndex = turnSource.indexOf("shouldEscape");
const afterEscapeIndex = turnSource.indexOf('"afterEscape"');
assert.ok(beforeEscapeIndex >= 0 && beforeEscapeIndex < grappleEscapeIndex);
assert.ok(grappleEscapeIndex < afterEscapeIndex, "Adrenaline checkpoint must remain after grapple escape");

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.ok(html.indexOf("browser-ability-hooks.js") < html.indexOf("browser-rage.js"));
  assert.ok(html.indexOf("browser-support.js") < html.indexOf("browser-ability-hook-installation.js"));
  assert.ok(html.indexOf("browser-ability-hook-installation.js") < html.indexOf("browser-turn.js"));
}

console.log("Browser Bonus Action hook migration regressions passed.");
