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
  "browser-modifier-validation.js",
  "browser-modifiers.js",
  "browser-timed-conditions.js",
  "browser-timed-self-buff-policy.js",
  "browser-timed-self-buffs.js",
  "browser-state.js",
  "browser-rolls.js",
  "browser-zero-hp.js",
  "browser-attack-outcome.js",
  "browser-environment-contexts.js",
  "browser-attack.js",
  "browser-ability-checks.js",
]) load(file);

const queuedDice = (values, fallback = 10) => {
  const queue = [...values];
  const roll = (sides) => ((queue.length ? queue.shift() : fallback) - 1) % sides + 1;
  return { roll, rollMany: (count, sides) => Array.from({ length: count }, () => roll(sides)) };
};

const S = window.IRON_PIT_BROWSER_STATE;
const B = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS;
const E = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
const A = window.IRON_PIT_BROWSER_ATTACK;
const C = window.IRON_PIT_BROWSER_ABILITY_CHECKS;
const hero = window.IRON_PIT_BROWSER_HEROES["aurelia-brightshield-2014-l20"];
const nimbus = hero.timed_self_buff_actions[0];

assert.deepEqual(nimbus.emittedEnvironmentContexts, [
  { context_id: "sunlight", radius_ft: 30 },
]);
assert.equal(nimbus.startTurnEmanationDamage.radius_ft, 30);

const sunlightReaction = {
  source_id: "sunlight-sensitivity",
  source_name: "Sunlight Sensitivity",
  context_id: "sunlight",
  disadvantage_on: ["attack_rolls", "sight_based_perception_checks"],
};

function targetTemplate() {
  return {
    id: "synthetic-sunlight-reactor",
    name: "Synthetic Sunlight Reactor",
    kind: "monster",
    ruleset: "2014",
    creature_type: "humanoid",
    size: "medium",
    max_hp: 30,
    speed_ft: 30,
    armor_class: 12,
    damage_resistances: [],
    damage_immunities: [],
    damage_vulnerabilities: [],
    condition_immunities: [],
    traits: [],
    resources: {},
    timed_self_buff_actions: [],
    environment_context_reactions: [sunlightReaction],
    attacks: [{
      id: "test-club",
      name: "Club",
      kind: "melee",
      bonus: 4,
      damageBonus: 2,
      damageType: "bludgeoning",
      diceCount: 1,
      diceSize: 4,
      reach: 35,
    }],
  };
}

function member(id, side, template, position) {
  return {
    combatant_id: id,
    side,
    position_ft: position,
    state: S.buildState(structuredClone(template)),
  };
}

const paladin = member("aurelia", "heroes", hero, 0);
const target = member("target", "monsters", targetTemplate(), 25);
const setup = { heroes: [paladin], monsters: [target], ruleset: "2014" };

S.beginTurn(paladin.state);
B.resolve(1, 1, paladin, nimbus);
assert.equal(
  paladin.state.timed_effects.some((effect) => effect.source_effect_id === "holy-nimbus"),
  true,
);
assert.equal(E.inside(target, setup, "sunlight"), true);
assert.equal(E.disadvantageSources(target, setup, "attack_rolls"), 1);
assert.equal(E.disadvantageSources(target, setup, "sight_based_perception_checks"), 1);
assert.equal(
  C.mode(target.state, 0, 0, {
    member: target, setup, skill: "perception", reliesOnSight: true,
  }),
  "disadvantage",
);
assert.equal(
  C.mode(target.state, 0, 0, {
    member: target, setup, skill: "perception", reliesOnSight: false,
  }),
  "normal",
);

S.beginTurn(target.state);
window.IRON_PIT_DICE = queuedDice([3, 17, 4]);
const inRange = A.resolveAttack(2, 1, target, paladin, target.state.template.attacks[0], 25, { setup });
assert.equal(inRange.attack_roll.mode, "disadvantage");
assert.equal(inRange.attack_roll.selected_roll, 3);

target.position_ft = 35;
assert.equal(E.inside(target, setup, "sunlight"), false);
assert.equal(E.disadvantageSources(target, setup, "attack_rolls"), 0);
S.beginTurn(target.state);
window.IRON_PIT_DICE = queuedDice([17, 4]);
const outOfRange = A.resolveAttack(3, 2, target, paladin, target.state.template.attacks[0], 35, { setup });
assert.equal(outOfRange.attack_roll.mode, "normal");

target.position_ft = 25;
const expired = window.IRON_PIT_BROWSER_TIMED.expireSourceStart(4, 11, paladin, setup);
assert.equal(expired.events.some((event) => event.feature_id === "holy-nimbus"), true);
assert.equal(E.inside(target, setup, "sunlight"), false);
assert.equal(E.disadvantageSources(target, setup, "attack_rolls"), 0);
assert.equal(
  C.mode(target.state, 0, 0, {
    member: target, setup, skill: "perception", reliesOnSight: true,
  }),
  "normal",
);

const unused = member("unused", "monsters", targetTemplate(), 25);
const idle = member("idle", "heroes", hero, 0);
const idleSetup = { heroes: [idle], monsters: [unused], ruleset: "2014" };
assert.equal(E.disadvantageSources(unused, idleSetup, "attack_rolls"), 0);

const plainTemplate = targetTemplate();
plainTemplate.environment_context_reactions = [];
const plain = member("plain", "monsters", plainTemplate, 25);
const activeSetup = { heroes: [paladin], monsters: [plain], ruleset: "2014" };
S.beginTurn(paladin.state);
assert.equal(E.disadvantageSources(plain, activeSetup, "attack_rolls"), 0);

load("browser-monsters-2014.js");
const koboldTemplate = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-kobold"];
assert.ok(koboldTemplate);
assert.deepEqual(koboldTemplate.environment_context_reactions, [sunlightReaction]);
const boundKobold = member("kobold", "monsters", koboldTemplate, 5);
const boundPaladin = member("aurelia-bound", "heroes", hero, 0);
const boundSetup = { heroes: [boundPaladin], monsters: [boundKobold], ruleset: "2014" };
S.beginTurn(boundPaladin.state);
B.resolve(1, 1, boundPaladin, nimbus);
assert.equal(E.inside(boundKobold, boundSetup, "sunlight"), true);
assert.equal(E.disadvantageSources(boundKobold, boundSetup, "attack_rolls"), 1);
S.beginTurn(boundKobold.state);
window.IRON_PIT_DICE = queuedDice([3, 17, 4]);
const koboldAttack = A.resolveAttack(
  2, 1, boundKobold, boundPaladin, boundKobold.state.template.attacks[0], 5, { setup: boundSetup },
);
assert.equal(koboldAttack.attack_roll.mode, "disadvantage");
assert.equal(koboldAttack.attack_roll.selected_roll, 3);

console.log("environment context sunlight reaction parity passed.");
