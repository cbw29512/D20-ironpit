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
assert.equal(Object.keys(manual).length, 67, "Legacy fragments remain a 67-monster compatibility subset");
assert.equal(Object.keys(generated).length, 67, "Generated runtime must expose only currently RAW-certified monsters");
assert.ok(generated["srd-tyrannosaurus-rex"]);
assert.equal(generated["srd-commoner"], undefined, "Blocked Commoner must not leak into the browser runtime");

const movementKeys = ["burrow_ft", "climb_ft", "fly_ft", "hover", "swim_ft", "walk_ft"];
for (const monster of Object.values(generated)) {
  assert.deepEqual(Object.keys(monster.movement_modes).sort(), movementKeys, `${monster.id} must export the full movement fingerprint`);
  assert.ok(Array.isArray(monster.source_trait_names), `${monster.id} must export its printed trait fingerprint`);
  assert.ok(Array.isArray(monster.source_reaction_names), `${monster.id} must export its printed reaction fingerprint`);
  assert.ok(Array.isArray(monster.source_bonus_action_names), `${monster.id} must export its printed bonus-action fingerprint`);
  assert.ok(Array.isArray(monster.source_limited_use_names), `${monster.id} must export its limited-use fingerprint`);
}
assert.deepEqual(generated["srd-bat"].movement_modes, {
  walk_ft: 5, fly_ft: 30, climb_ft: 0, swim_ft: 0, burrow_ft: 0, hover: false,
});
assert.deepEqual(generated["srd-wolf"].source_trait_names, ["Pack Tactics"]);
assert.deepEqual(generated["srd-deer"].source_trait_names, ["Agile"]);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_reaction_names, []);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_bonus_action_names, ["Nimble Escape"]);
assert.deepEqual(generated["srd-saber-toothed-tiger"].source_limited_use_names, []);

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
  "browser-grapple.js", "browser-state.js", "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js",
  "browser-attack.js", "browser-saves.js", "browser-multiattack.js",
]) load(file);
window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 10 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 10 : 1),
};
const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const combatant = (id, side, position, template) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(structuredClone(template)),
});
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

console.log("Generated monster runtime contains only RAW-certified templates, with complete source fingerprints and T. rex retargeting.");
