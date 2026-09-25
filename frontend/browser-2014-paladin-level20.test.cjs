"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);

for (const file of [
  "browser-heroes.js",
  "browser-condition-immunity.js",
  "browser-condition-rules.js",
  "browser-action-economy.js",
  "browser-ability-hooks.js",
  "browser-modifiers.js",
  "browser-timed-conditions.js",
  "browser-timed-self-buffs.js",
  "browser-state.js",
  "browser-zero-hp.js",
  "browser-attack-outcome.js",
  "browser-attack.js",
  "browser-defensive-modifier-rules.js",
  "browser-timed-emanations.js",
]) load(file);

const heroes = window.IRON_PIT_BROWSER_HEROES;
const level19 = heroes["aurelia-brightshield-2014-l19"];
const hero = heroes["aurelia-brightshield-2014-l20"];

assert.ok(level19, "Aurelia level 19 must remain exported");
assert.ok(hero, "Aurelia level 20 must be exported");
assert.equal(hero.level, 20);
assert.equal(hero.max_hp, 164);
assert.deepEqual(hero.ability_scores, level19.ability_scores);
assert.equal(hero.aura_radius_2014_ft, 30);
assert.equal(hero.aura_of_protection_2014_bonus, 5);
assert.deepEqual(
  [1, 2, 3, 4, 5].map((level) => hero.resources[`spell-slot-${level}`]),
  [4, 3, 3, 3, 2],
);
assert.equal(hero.resources["lay-on-hands"], 100);
assert.equal(hero.resources["cleansing-touch"], 5);
assert.equal(hero.resources["holy-nimbus"], 1);
assert.equal(hero.canonical_prepared_spells.length, 15);

assert.equal(hero.timed_self_buff_actions.length, 1);
const nimbus = hero.timed_self_buff_actions[0];
assert.equal(nimbus.id, "holy-nimbus");
assert.equal(nimbus.name, "Holy Nimbus");
assert.equal(nimbus.actionCost, "action");
assert.equal(nimbus.resourceId, "holy-nimbus");
assert.equal(nimbus.resourceCost, 1);
assert.equal(nimbus.durationRounds, 10);
assert.equal(nimbus.expiryTiming, "source_turn_start");
assert.deepEqual(nimbus.startTurnEmanationDamage, {
  trigger: "enemy_turn_start",
  radius_ft: 30,
  fixed_damage: 10,
  damage_type: "radiant",
});

assert.equal(nimbus.savingThrowAdvantageGrants.length, 1);
const saveGrant = nimbus.savingThrowAdvantageGrants[0];
assert.equal(saveGrant.source_name, "Holy Nimbus");
assert.equal(saveGrant.requires_spell_effect, true);
assert.deepEqual(saveGrant.source_creature_types, ["fiend", "undead"]);
assert.deepEqual(
  [...saveGrant.abilities].sort(),
  ["charisma", "constitution", "dexterity", "intelligence", "strength", "wisdom"],
);

const S = window.IRON_PIT_BROWSER_STATE;
const B = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
const D = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;

function targetTemplate() {
  return {
    id: "holy-nimbus-target",
    name: "Holy Nimbus Target",
    kind: "monster",
    ruleset: "2014",
    creature_type: "humanoid",
    size: "medium",
    max_hp: 30,
    speed_ft: 30,
    armor_class: 12,
    damage_resistances: ["radiant"],
    damage_immunities: [],
    damage_vulnerabilities: [],
    condition_immunities: [],
    traits: [],
    resources: {},
    timed_self_buff_actions: [],
  };
}

const paladin = {
  combatant_id: "aurelia",
  side: "heroes",
  position_ft: 0,
  state: S.buildState(structuredClone(hero)),
};
const target = {
  combatant_id: "target",
  side: "monsters",
  position_ft: 25,
  state: S.buildState(targetTemplate()),
};
const setup = {
  heroes: [paladin],
  monsters: [target],
  hero_total_levels: 20,
  monster_total_cr: "1",
  ruleset: "2014",
};

S.beginTurn(paladin.state);
const activation = B.resolve(1, 1, paladin, nimbus);
assert.equal(activation.feature_id, "holy-nimbus");
assert.equal(activation.resource_remaining, 0);
assert.equal(paladin.state.action_available, false);
assert.equal(
  paladin.state.timed_effects.some((effect) => effect.source_effect_id === "holy-nimbus"),
  true,
);

assert.deepEqual(
  D.saveAdvantageSourceNames(
    paladin.state,
    "wisdom",
    { spellEffect: true, sourceCreatureType: "fiend" },
  ),
  ["Holy Nimbus"],
);
assert.deepEqual(
  D.saveAdvantageSourceNames(
    paladin.state,
    "dexterity",
    { spellEffect: true, sourceCreatureType: "undead" },
  ),
  ["Holy Nimbus"],
);
assert.deepEqual(
  D.saveAdvantageSourceNames(
    paladin.state,
    "wisdom",
    { spellEffect: false, sourceCreatureType: "fiend" },
  ),
  [],
);
assert.deepEqual(
  D.saveAdvantageSourceNames(
    paladin.state,
    "wisdom",
    { spellEffect: true, sourceCreatureType: "fey" },
  ),
  [],
);

const turnStart = H.PHASES.TURN_START;
assert.equal(
  H.abilitiesFor(turnStart).some((ability) => ability.id === "timed-emanation-damage"),
  true,
);

const before = target.state.current_hp;
const inRange = H.runPhase(turnStart, {
  sequence: 2,
  round: 1,
  member: target,
  setup,
  turnKey: "1:target",
  events: [],
});
assert.equal(inRange.events.length, 1);
assert.equal(inRange.events[0].feature_id, "holy-nimbus");
assert.equal(inRange.events[0].distance_before_ft, 25);
assert.equal(inRange.events[0].damage_components[0].total, 10);
assert.equal(inRange.events[0].damage_components[0].applied_total, 5);
assert.equal(target.state.current_hp, before - 5);
assert.equal(inRange.claimed, false);

target.position_ft = 35;
const outOfRange = H.runPhase(turnStart, {
  sequence: inRange.sequence,
  round: 2,
  member: target,
  setup,
  turnKey: "2:target",
  events: [],
});
assert.equal(outOfRange.events.length, 0);
assert.equal(target.state.current_hp, before - 5);

const expired = window.IRON_PIT_BROWSER_TIMED.expireSourceStart(
  outOfRange.sequence,
  11,
  paladin,
  setup,
);
assert.equal(expired.events.some((event) => event.feature_id === "holy-nimbus"), true);
assert.deepEqual(
  D.saveAdvantageSourceNames(
    paladin.state,
    "wisdom",
    { spellEffect: true, sourceCreatureType: "fiend" },
  ),
  [],
);

target.position_ft = 25;
const afterExpiry = H.runPhase(turnStart, {
  sequence: expired.sequence,
  round: 11,
  member: target,
  setup,
  turnKey: "11:target",
  events: [],
});
assert.equal(afterExpiry.events.length, 0);
assert.equal(target.state.current_hp, before - 5);

const taggedHero = structuredClone(hero);
const taggedAction = structuredClone(nimbus);
taggedAction.startTurnEmanationDamage = null;
taggedAction.savingThrowAdvantageGrants = [{
  source_id: "tagged-defense",
  source_name: "Tagged Defense",
  abilities: ["wisdom"],
  required_effect_tags: ["poison"],
}];
const taggedPaladin = {
  combatant_id: "tagged-aurelia",
  side: "heroes",
  position_ft: 0,
  state: S.buildState(taggedHero),
};
S.beginTurn(taggedPaladin.state);
B.resolve(1, 1, taggedPaladin, taggedAction);
assert.deepEqual(
  D.saveAdvantageSourceNames(taggedPaladin.state, "wisdom", { effectTags: ["poison"] }),
  ["Tagged Defense"],
);
assert.deepEqual(
  D.saveAdvantageSourceNames(taggedPaladin.state, "wisdom", {}),
  [],
);

console.log("2014 Paladin level 20 Holy Nimbus browser parity passed.");
