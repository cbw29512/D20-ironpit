"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
const manualFiles = [
  "browser-monsters.js", "browser-monsters-fixed.js", "browser-monsters-beast2.js",
  "browser-monsters-batch3.js", "browser-monsters-control.js", "browser-monsters-poison.js",
  "browser-monsters-venom.js", "browser-monsters-mixed.js", "browser-monsters-expansion.js",
];
for (const file of manualFiles) load(file);
const manual = structuredClone(window.IRON_PIT_BROWSER_MONSTERS);

load("browser-monsters-generated.js");
const generated = window.IRON_PIT_BROWSER_MONSTERS;
assert.equal(window.IRON_PIT_CANONICAL_MONSTERS_READY, true, "Canonical generated monster bundle must mark itself ready");
assert.equal(Object.keys(manual).length, 67, "Legacy fragments remain a 67-monster compatibility subset");
assert.equal(Object.keys(generated).length, 115, "Generated runtime must expose only currently RAW-certified monsters");
for (const id of [
  "srd-jackal", "srd-archelon", "srd-ankylosaurus", "srd-giant-eagle", "srd-giant-elk", "srd-giant-crocodile",
  "srd-allosaurus", "srd-minotaur-skeleton", "srd-triceratops", "srd-warhorse-skeleton",
  "srd-animated-armor", "srd-animated-flying-sword", "srd-awakened-tree", "srd-cultist", "srd-flying-snake",
  "srd-gargoyle", "srd-grimlock", "srd-guard-captain", "srd-hippopotamus",
  "srd-giant-scorpion", "srd-grick", "srd-griffon", "srd-manticore", "srd-ogre-zombie", "srd-pegasus", "srd-scorpion", "srd-skeleton", "srd-spider",
  "srd-tough", "srd-venomous-snake", "srd-violet-fungus", "srd-bandit-captain", "srd-knight",
  "srd-noble", "srd-warrior-veteran", "srd-goblin-boss", "srd-blood-hawk",
  "srd-swarm-of-bats", "srd-swarm-of-rats", "srd-swarm-of-crawling-claws",
  "srd-swarm-of-insects", "srd-swarm-of-venomous-snakes", "srd-goat", "srd-merfolk-skirmisher", "srd-worg", "srd-zombie",
]) {
  assert.ok(generated[id], `${id} must be present in generated runtime`);
}
assert.ok(generated["srd-tyrannosaurus-rex"]);
assert.equal(generated["srd-commoner"], undefined, "Blocked Commoner must not leak into the browser runtime");
assert.equal(generated["srd-killer-whale"], undefined, "Aquatic-only Killer Whale must remain deferred from the standard arena");
assert.deepEqual(generated["srd-cultist"].attacks[0].onHitDamage, [
  { source: "Necrotic", diceCount: 0, diceSize: 2, damageBonus: 1, damageType: "necrotic" },
]);
assert.deepEqual(generated["srd-worg"].attacks[0].onHitModifiers, [{
  kind: "attacks-against-advantage", consumeOnAttackAgainst: true, expiresAtStartOfSourceTurn: true,
}]);
const goatTemplate = generated["srd-goat"];
assert.equal(goatTemplate.attacks[0].fixedDamage, 1);
assert.deepEqual(goatTemplate.attacks[0].charge, {
  minimumMove: 20,
  replacementDamage: { diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "bludgeoning" },
});
const merfolkTemplate = generated["srd-merfolk-skirmisher"];
assert.equal(merfolkTemplate.primary_attack_id, "merfolk-skirmisher-ocean-spear-ranged");
assert.deepEqual(merfolkTemplate.attacks.map((item) => item.kind), ["ranged", "melee"]);
assert.deepEqual(merfolkTemplate.attacks[0].onHitDamage, [
  { source: "Cold", diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "cold" },
]);
assert.deepEqual(merfolkTemplate.attacks[0].onHitModifiers, [
  { kind: "speed", flatBonus: -10, expiresAtEndOfTargetTurn: true },
]);
assert.deepEqual(merfolkTemplate.attacks[1].onHitModifiers, merfolkTemplate.attacks[0].onHitModifiers);
assert.deepEqual(merfolkTemplate.source_trait_names, ["Amphibious"]);

const movementKeys = ["burrow_ft", "climb_ft", "fly_ft", "hover", "swim_ft", "walk_ft"];
for (const monster of Object.values(generated)) {
  assert.deepEqual(Object.keys(monster.movement_modes).sort(), movementKeys, `${monster.id} must export the full movement fingerprint`);
  assert.ok(Array.isArray(monster.source_trait_names), `${monster.id} must export its printed trait fingerprint`);
  assert.ok(Array.isArray(monster.source_reaction_names), `${monster.id} must export its printed reaction fingerprint`);
  assert.ok(Array.isArray(monster.source_bonus_action_names), `${monster.id} must export its bonus-action fingerprint`);
  assert.ok(Array.isArray(monster.source_limited_use_names), `${monster.id} must export its limited-use fingerprint`);
  assert.ok(Array.isArray(monster.source_legendary_action_names), `${monster.id} must export its legendary-action fingerprint`);
  assert.ok(monster.source_spellcasting_fingerprint === null || typeof monster.source_spellcasting_fingerprint === "string");
}
assert.deepEqual(generated["srd-bat"].movement_modes, {
  walk_ft: 5, fly_ft: 30, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false,
});
assert.deepEqual(generated["srd-animated-flying-sword"].movement_modes, {
  walk_ft: 5, fly_ft: 50, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: true,
});
assert.deepEqual(merfolkTemplate.movement_modes, {
  walk_ft: 10, fly_ft: 0, climb_ft: 0, swim_ft: 40, burrow_ft: 0, hover: false,
});
assert.deepEqual(generated["srd-wolf"].source_trait_names, ["Pack Tactics"]);
assert.deepEqual(generated["srd-tough"].source_trait_names, ["Pack Tactics"]);
assert.deepEqual(generated["srd-blood-hawk"].source_trait_names, ["Pack Tactics"]);
assert.deepEqual(generated["srd-blood-hawk"].attacks[0].conditionalDamage, {
  trigger: "target_bloodied", mode: "replace_weapon", diceCount: 1, diceSize: 8,
  damageBonus: 2, damageType: "piercing",
});
for (const id of ["srd-swarm-of-bats", "srd-swarm-of-rats", "srd-swarm-of-crawling-claws"]) {
  assert.deepEqual(generated[id].source_trait_names, ["Swarm"]);
  assert.equal(generated[id].traits.includes("swarm"), true);
  assert.equal(generated[id].attacks[0].conditionalDamage.trigger, "attacker_bloodied");
  assert.equal(generated[id].attacks[0].conditionalDamage.mode, "replace_weapon");
}
assert.equal(generated["srd-swarm-of-crawling-claws"].attacks[0].proneMaxSize, "medium");
const insectSwarm = generated["srd-swarm-of-insects"];
assert.deepEqual(insectSwarm.source_trait_names, ["Spider Climb", "Swarm"]);
assert.equal(insectSwarm.traits.includes("swarm"), true);
assert.deepEqual(insectSwarm.movement_modes, {
  walk_ft: 20, fly_ft: 20, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false,
});
assert.deepEqual(insectSwarm.attacks[0].conditionalDamage, {
  trigger: "attacker_bloodied", mode: "replace_weapon", diceCount: 1, diceSize: 4,
  damageBonus: 1, damageType: "poison",
});
const snakeSwarm = generated["srd-swarm-of-venomous-snakes"];
assert.deepEqual(snakeSwarm.source_trait_names, ["Swarm"]);
assert.equal(snakeSwarm.traits.includes("swarm"), true);
assert.equal(snakeSwarm.movement_modes.swim_ft, 30);
assert.deepEqual(snakeSwarm.attacks[0].onHitDamage, [
  { source: "Poison", diceCount: 3, diceSize: 6, damageBonus: 0, damageType: "poison" },
]);
assert.deepEqual(snakeSwarm.attacks[0].conditionalDamage, {
  trigger: "attacker_bloodied", mode: "replace_weapon", diceCount: 1, diceSize: 4,
  damageBonus: 4, damageType: "piercing",
});
assert.deepEqual(generated["srd-deer"].source_trait_names, ["Agile"]);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_reaction_names, []);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_bonus_action_names, ["Nimble Escape"]);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_limited_use_names, []);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_legendary_action_names, []);
assert.equal(generated["srd-saber-toothed-tiger"].source_spellcasting_fingerprint, null);
for (const id of ["srd-bandit-captain", "srd-knight", "srd-noble", "srd-warrior-veteran"]) {
  assert.deepEqual(generated[id].source_reaction_names, ["Parry"]);
  assert.deepEqual(generated[id].parry_reaction, { ac_bonus: 2 });
}
assert.deepEqual(generated["srd-goblin-boss"].source_reaction_names, ["Redirect Attack"]);
assert.deepEqual(generated["srd-goblin-boss"].redirect_attack_reaction, {
  ally_max_size: "medium", ally_range_ft: 5,
});

const minotaurCharge = generated["srd-minotaur-skeleton"].attacks.find((item) => item.id === "minotaur-skeleton-gore").charge;
assert.deepEqual(minotaurCharge, {
  minimumMove: 20, diceCount: 2, diceSize: 8, damageType: "piercing", proneMaxSize: "large",
});
const triceratops = generated["srd-triceratops"];
assert.deepEqual(triceratops.attacks.find((item) => item.id === "triceratops-gore").charge, {
  minimumMove: 20, diceCount: 2, diceSize: 8, damageType: "piercing", proneMaxSize: "huge",
});
assert.deepEqual(triceratops.attack_action.slots.map((slot) => slot.attackIds), [
  ["triceratops-gore"], ["triceratops-gore"],
]);
const warhorseSkeleton = generated["srd-warhorse-skeleton"];
assert.deepEqual(warhorseSkeleton.attacks.find((item) => item.id === "warhorse-skeleton-hooves").charge, {
  minimumMove: 20, proneMaxSize: "large",
});
const allosaurus = generated["srd-allosaurus"];
assert.equal(allosaurus.primary_attack_id, "allosaurus-bite");
assert.deepEqual(allosaurus.attacks.map((item) => item.id), ["allosaurus-bite", "allosaurus-claws"]);
assert.deepEqual(allosaurus.attacks.find((item) => item.id === "allosaurus-claws").charge, {
  minimumMove: 30, proneMaxSize: "large", followUpAttackId: "allosaurus-bite",
});
const grappleProfiles = [
  ["srd-giant-scorpion", "srd-giant-scorpion-claw", "large", 13],
  ["srd-grick", "srd-grick-tentacles", "medium", 12],
  ["srd-griffon", "srd-griffon-rend", "medium", 14],
];
for (const [monsterId, attackId, maxTargetSize, grappleEscapeDc] of grappleProfiles) {
  const grappleAttack = generated[monsterId].attacks.find((item) => item.id === attackId);
  assert.deepEqual(grappleAttack.controlEffect, { maxTargetSize, grappleEscapeDc });
}

const slots = (action) => (action?.slots || []).map((slot) => Array.isArray(slot)
  ? { attackIds: slot, saveActionIds: [] }
  : { attackIds: slot.attackIds || [], saveActionIds: slot.saveActionIds || [] });
const attack = (item) => ({
  id: item.id, name: item.name, kind: item.kind, bonus: item.bonus,
  diceCount: item.diceCount, diceSize: item.diceSize, damageBonus: item.damageBonus,
  damageType: item.damageType, reach: item.kind === "melee" ? (item.reach || 5) : null,
  normal: item.normal || null, long: item.long || null, fixedDamage: item.fixedDamage ?? null,
  conditionalAdvantage: item.conditionalAdvantage || null, onHitDamage: item.onHitDamage || [],
  proneMaxSize: item.proneMaxSize || null, controlEffect: item.controlEffect || null,
  forbidSelfGrappledTarget: Boolean(item.forbidSelfGrappledTarget), charge: item.charge || null,
});
const normalized = (item) => ({
  id: item.id, name: item.name, challenge_rating: item.challenge_rating, size: item.size,
  armor_class: item.armor_class, max_hp: item.max_hp, speed_ft: item.speed_ft,
  initiative_bonus: item.initiative_bonus, attacks: item.attacks.map(attack),
  primary_attack_id: item.primary_attack_id, attackSlots: slots(item.attack_action),
  saving_throw_actions: item.saving_throw_actions || [], traits: [...(item.traits || [])].sort(),
  resources: item.resources || {}, damage_resistances: [...(item.damage_resistances || [])].sort(),
  damage_vulnerabilities: [...(item.damage_vulnerabilities || [])].sort(),
  damage_immunities: [...(item.damage_immunities || [])].sort(),
  condition_immunities: [...(item.condition_immunities || [])].sort(),
});

for (const id of Object.keys(manual)) {
  if (!generated[id]) continue;
  assert.deepEqual(normalized(generated[id]), normalized(manual[id]), `${id} generated runtime drifted from certified compatibility data`);
}

const rex = generated["srd-tyrannosaurus-rex"];
assert.equal(rex.challenge_rating, "8");
assert.deepEqual(rex.attack_action.slots.map((slot) => slot.attackIds), [
  ["tyrannosaurus-rex-bite"], ["tyrannosaurus-rex-tail"],
]);
const bite = rex.attacks.find((item) => item.id === "tyrannosaurus-rex-bite");
const tail = rex.attacks.find((item) => item.id === "tyrannosaurus-rex-tail");
assert.equal(bite.controlEffect.maxTargetSize, "large");
assert.equal(bite.controlEffect.grappleEscapeDc, 17);
assert.equal(bite.controlEffect.restrainsWhileGrappled, true);
assert.equal(tail.forbidSelfGrappledTarget, true);
assert.equal(tail.proneMaxSize, "huge");

for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js", "browser-action-economy.js",
  "browser-grapple.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-zero-hp.js", "browser-attack.js", "browser-charge.js", "browser-saves.js", "browser-condition-lifecycle.js", "browser-multiattack.js",
]) load(file);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 10 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 10 : 1),
};
const S = window.IRON_PIT_BROWSER_STATE;
const C = window.IRON_PIT_BROWSER_CHARGE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const MOD = window.IRON_PIT_BROWSER_MODIFIERS;
const LIFE = window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE;
const combatant = (id, side, position, template) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});

const merfolkSlowTarget = combatant("hero-slow:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
MOD.applyHitEffects(merfolkSlowTarget.state, "merfolk", merfolkTemplate.attacks[0]);
assert.equal(MOD.effectiveSpeed(merfolkSlowTarget.state), 20);
S.beginTurn(merfolkSlowTarget.state);
assert.equal(merfolkSlowTarget.state.movement_remaining_ft, 20);
const slowExpiry = LIFE.resolveTargetTiming(1, 1, merfolkSlowTarget, "target_turn_end");
assert.deepEqual(slowExpiry.events, []);
assert.equal(MOD.effectiveSpeed(merfolkSlowTarget.state), 30);
assert.deepEqual(merfolkSlowTarget.state.active_modifiers, []);

const goatMember = combatant("monster-goat:srd-goat", "monsters", 5, goatTemplate);
const goatTarget = combatant("hero-goat:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
goatMember.state.initiative_total = 20;
goatTarget.state.initiative_total = 10;
S.beginTurn(goatMember.state);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 19 : 3,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 19 : 3),
};
const goatResult = C.resolveClosing(1, 1, goatMember, goatTarget, { heroes: [goatTarget], monsters: [goatMember] });
const goatAttack = goatResult.events.find((event) => event.event_type === "attack");
assert.equal(goatResult.handled, true);
assert.equal(goatAttack.damage_roll.notation, "1d4+0");
assert.equal(goatAttack.damage_roll.total, 3);
assert.equal(goatAttack.applied_condition_ids.includes("prone"), false);

const chargeHorse = combatant("monster-1:srd-warhorse-skeleton", "monsters", 5, warhorseSkeleton);
const chargeHero = combatant("hero-charge:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
chargeHorse.state.initiative_total = 20;
chargeHero.state.initiative_total = 10;
S.beginTurn(chargeHorse.state);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 15 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 15 : 1),
};
const chargeResult = C.resolveClosing(1, 1, chargeHorse, chargeHero, { heroes: [chargeHero], monsters: [chargeHorse] });
const chargeAttack = chargeResult.events.at(-1);
assert.equal(chargeResult.handled, true);
assert.equal(chargeAttack.damage_roll.notation, "1d6+4", "Prone-only Charge must not manufacture bonus damage");
assert.ok(chargeAttack.applied_condition_ids.includes("prone"));

const allosaurusMember = combatant("monster-1:srd-allosaurus", "monsters", 5, allosaurus);
const allosaurusTarget = combatant("hero-allosaurus:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
allosaurusMember.state.initiative_total = 20;
allosaurusTarget.state.initiative_total = 10;
S.beginTurn(allosaurusMember.state);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 15 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 15 : 1),
};
const allosaurusResult = C.resolveClosing(1, 1, allosaurusMember, allosaurusTarget, {
  heroes: [allosaurusTarget], monsters: [allosaurusMember],
});
const allosaurusAttacks = allosaurusResult.events.filter((event) => event.event_type === "attack");
assert.equal(allosaurusResult.handled, true);
assert.deepEqual(allosaurusAttacks.map((event) => event.weapon_id), ["allosaurus-claws", "allosaurus-bite"]);
assert.deepEqual(allosaurusAttacks.map((event) => event.feature_id), ["charge", "charge-follow-up"]);
assert.equal(allosaurusAttacks[0].damage_roll.notation, "1d8+4");
assert.ok(allosaurusAttacks[0].applied_condition_ids.includes("prone"));
assert.equal(allosaurusAttacks[1].damage_roll.notation, "2d10+4");

const missAllosaurus = combatant("monster-2:srd-allosaurus", "monsters", 5, allosaurus);
const missTarget = combatant("hero-miss:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
missAllosaurus.state.initiative_total = 20;
missTarget.state.initiative_total = 10;
S.beginTurn(missAllosaurus.state);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 1 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 1 : 1),
};
const missResult = C.resolveClosing(1, 1, missAllosaurus, missTarget, { heroes: [missTarget], monsters: [missAllosaurus] });
assert.deepEqual(missResult.events.filter((event) => event.event_type === "attack").map((event) => event.weapon_id), ["allosaurus-claws"]);

window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 10 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 10 : 1),
};
const rexMember = combatant("monster-1:srd-tyrannosaurus-rex", "monsters", 10, rex);
const heroOne = combatant("hero-1:karnok-stoneward-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const heroTwo = combatant("hero-2:rokhan-stonefury-l1", "heroes", 0, window.IRON_PIT_BROWSER_HEROES["rokhan-stonefury-l1"]);
const setup = { heroes: [heroOne, heroTwo], monsters: [rexMember] };
S.beginTurn(rexMember.state);
const result = M.resolveAttackAction(1, 1, rexMember, setup);
const attacks = result.events.filter((event) => event.event_type === "attack");
assert.deepEqual(attacks.map((event) => event.weapon_id), ["tyrannosaurus-rex-bite", "tyrannosaurus-rex-tail"]);
assert.equal(attacks[0].target_id, heroOne.combatant_id);
assert.equal(attacks[1].target_id, heroTwo.combatant_id, "Tail must retarget away from the creature held by Bite");
assert.ok(heroOne.state.active_effect_ids.includes("grappled"));
assert.ok(heroOne.state.active_effect_ids.includes("restrained"));
assert.ok(heroTwo.state.active_effect_ids.includes("prone"));

console.log("Generated monster runtime contains 115 RAW-certified templates, including timed on-hit Speed modifiers, Charge damage replacement, fixed typed hit riders, and source-turn on-hit Advantage modifiers, with aquatic-only Killer Whale deferred, shared grapple-control monsters, Allosaurus Charge follow-up Bite, native data-only swarms, Charge riders, Prone-only Charge, conditional damage, Redirect Attack, and T. rex retargeting.");
