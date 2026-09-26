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
  distance: () => 5,
};
window.IRON_PIT_BROWSER_FORMATION = {
  targetOrder: (_member, setup) => setup.monsters || [],
  chooseStandardAttack: (member, setup) => {
    const target = (setup.monsters || [])[0];
    const attack = (member.state.template.attacks || [])[0];
    return target && attack ? { target, attack, distance: 5 } : null;
  },
};
window.IRON_PIT_BROWSER_MODIFIERS = {
  effectiveSpeed: (state) => state.template.speed_ft || 30,
  nextAttackAgainstAdvantage: (state, targetId) => (state.active_modifiers || [])
    .filter((item) => item.kind === "next-attack-against-advantage" && item.target_id === targetId).length,
  add: (state, item) => { state.active_modifiers.push({ ...item }); },
};
window.IRON_PIT_BROWSER_ATTACK = {
  resolveAttack(sequence, round, actor, target, attack, _distance, extra = {}) {
    return { sequence, round_number: round, event_type: "attack", actor_id: actor.combatant_id,
      target_id: target.combatant_id, weapon_id: attack.weaponId || attack.id, feature_id: extra.featureId || null,
      hit: false, description: "Hook test attack." };
  },
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
load("browser-resources.js");
load("browser-resource-conversion.js");
load("browser-rage.js");
load("browser-support.js");
load("browser-steady-aim.js");
load("browser-frenzy-2014.js");
load("browser-2014-monk.js");
load("browser-persistent-spell-attacks.js");
load("browser-ability-hook-installation.js");

const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const phase = H.PHASES.BONUS_ACTION_WINDOW;
const registrations = H.abilitiesFor(phase).map((item) => [item.id, item.priority, item.rulesets]);
assert.deepEqual(registrations, [
  ["rage-enter", 10, ["2014", "2024"]],
  ["second-wind", 20, ["2014", "2024"]],
  ["steady-aim", 25, ["2024"]],
  ["adrenaline-rush", 30, ["2024"]],
  ["resource-conversion", 30, ["2014", "2024"]],
  ["persistent-spell-attack", 40, ["2014"]],
  ["monk-bonus-attack-2014", 100, ["2014"]],
  ["frenzy-bonus-attack-2014", 110, ["2014"]],
  ["rage-maintain", 120, ["2024"]],
]);
assert.deepEqual(H.abilitiesFor(H.PHASES.TURN_FINALIZE).map((item) => item.id), ["rage-expiry-cleanup"]);

function baseState(template, resources = {}) {
  return {
    template,
    current_hp: template.max_hp,
    temporary_hp: 0,
    resources: { ...resources },
    active_effect_ids: [],
    active_modifiers: [],
    timed_effects: [],
    movement_remaining_ft: template.speed_ft || 30,
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
const run = (actor, bonusActionCheckpoint, round = 1, monsters = [], turnEvents = []) => H.runPhase(phase, {
  sequence: 1, round, member: actor, setup: { heroes: [actor], monsters },
  turnKey: `${round}:${actor.combatant_id}`, bonusActionCheckpoint, turnEvents, events: [],
});
const finalizePhase = (actor, round = 1, monsters = [], turnEvents = []) => H.runPhase(H.PHASES.TURN_FINALIZE, {
  sequence: 1, round, member: actor, setup: { heroes: [actor], monsters },
  turnKey: `${round}:${actor.combatant_id}`, turnEvents, events: [],
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
  const rogue = member("rogue", {
    name: "Rogue", ruleset: "2024", max_hp: 24, level: 3, speed_ft: 30,
    traits: ["adrenaline-rush"], wearing_heavy_armor: false, rage_damage_bonus: 0,
    stationary_bonus_action_next_attack_advantage: true,
    attacks: [{ id: "shortbow", weaponId: "shortbow", kind: "ranged", normal: 80, long: 320 }],
  }, { "adrenaline-rush": 2 });
  const target = member("aim-target", {
    name: "Aim Target", ruleset: "2024", max_hp: 20, level: 1, speed_ft: 30,
    traits: [], wearing_heavy_armor: false, rage_damage_bonus: 0, attacks: [],
  }, {});
  const result = run(rogue, "afterEscape", 1, [target]);
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["steady-aim"]);
  assert.equal(rogue.state.bonus_action_available, false);
  assert.equal(rogue.state.movement_remaining_ft, 0);
  assert.equal(rogue.state.resources["adrenaline-rush"], 2, "Steady Aim wins the offensive Bonus Action before Adrenaline Rush");
  assert.equal(rogue.state.active_modifiers.length, 1);
  assert.equal(rogue.state.active_modifiers[0].kind, "next-attack-against-advantage");
  assert.equal(rogue.state.active_modifiers[0].target_id, target.combatant_id);
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

{
  const monk = member("monk", {
    name: "Monk", ruleset: "2014", max_hp: 32, level: 5, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 0, martial_arts_bonus_attack: true,
    flurry_of_blows: false, attacks: [{ id: "monk-unarmed", weaponId: "unarmed-strike", kind: "melee", reach: 5 }],
  }, { ki: 5 });
  const target = member("target", {
    name: "Target", ruleset: "2014", max_hp: 20, level: 1, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 0, attacks: [],
  }, {});
  const prior = [{ event_type: "attack", actor_id: monk.combatant_id, weapon_id: "shortsword" }];
  const result = run(monk, "postAction", 1, [target], prior);
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["martial-arts"]);
  assert.equal(monk.state.bonus_action_available, false);
}

{
  const berserker = member("berserker", {
    name: "Berserker", ruleset: "2014", max_hp: 50, level: 5, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 2, frenzy_bonus_attack_2014: true,
    attacks: [{ id: "greataxe", weaponId: "greataxe", kind: "melee", reach: 5, diceCount: 1, diceSize: 12, damageBonus: 4, bonus: 7 }],
  }, { rage: 3 });
  berserker.state.active_effect_ids.push("rage", "frenzy-2014");
  berserker.state.rage_expires_round = 5; berserker.state.rage_max_round = 10;
  const target = member("frenzy-target", {
    name: "Target", ruleset: "2014", max_hp: 20, level: 1, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 0, attacks: [],
  }, {});
  const result = run(berserker, "postAction", 1, [target], []);
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["frenzy"]);
}

{
  const barbarian = member("maintain-rage", {
    name: "Barbarian", ruleset: "2024", max_hp: 60, level: 6, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 2, frenzy_bonus_attack_2014: false,
  }, { rage: 3 });
  barbarian.state.active_effect_ids.push("rage");
  barbarian.state.rage_expires_round = 2; barbarian.state.rage_max_round = 100;
  const result = run(barbarian, "postAction", 2);
  assert.equal(result.claimed, true);
  assert.deepEqual(result.events.map((event) => event.feature_id), ["rage"]);
  assert.equal(barbarian.state.rage_expires_round, 3);
}

{
  const barbarian = member("expired-rage", {
    name: "Barbarian", ruleset: "2024", max_hp: 60, level: 6, traits: [],
    wearing_heavy_armor: false, rage_damage_bonus: 2, frenzy_bonus_attack_2014: false,
  }, { rage: 3 });
  barbarian.state.active_effect_ids.push("rage");
  barbarian.state.rage_expires_round = 2; barbarian.state.rage_max_round = 100;
  barbarian.state.bonus_action_available = false;
  const post = run(barbarian, "postAction", 2);
  assert.equal(post.claimed, false);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(barbarian.state), true);
  const cleaned = finalizePhase(barbarian, 2);
  assert.equal(cleaned.claimed, false);
  assert.equal(window.IRON_PIT_BROWSER_RAGE.active(barbarian.state), false,
    "Rage expiry cleanup must still run after another feature has spent the Bonus Action");
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
const grappleEscapeIndex = turnSource.indexOf("if (H().shouldEscape(member.state))");
const afterEscapeIndex = turnSource.indexOf('"afterEscape"');
assert.ok(beforeEscapeIndex >= 0 && beforeEscapeIndex < grappleEscapeIndex);
assert.ok(grappleEscapeIndex < afterEscapeIndex, "Adrenaline checkpoint must remain after grapple escape");

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.ok(html.indexOf("browser-ability-hooks.js") < html.indexOf("browser-rage.js"));
  assert.ok(html.indexOf("browser-support.js") < html.indexOf("browser-steady-aim.js"));
  assert.ok(html.indexOf("browser-steady-aim.js") < html.indexOf("browser-ability-hook-installation.js"));
  assert.ok(html.indexOf("browser-ability-hook-installation.js") < html.indexOf("browser-turn.js"));
}

console.log("Browser Bonus Action hook migration regressions passed.");
