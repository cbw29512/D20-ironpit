"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);

const certificationManifest = JSON.parse(fs.readFileSync(
  path.join(__dirname, "..", "data", "monster_certification_manifest.json"), "utf8",
));
const expectedReadyIds = certificationManifest.monsters
  .filter((monster) => monster.public_ready_status === "ready")
  .map((monster) => monster.runtime_template_id)
  .filter(Boolean)
  .sort();

load("browser-monsters-generated.js");
const generated = window.IRON_PIT_BROWSER_MONSTERS;
const generatedIds = Object.keys(generated).sort();
assert.equal(window.IRON_PIT_CANONICAL_MONSTERS_READY, true);
assert.equal(certificationManifest.summary.public_ready, expectedReadyIds.length);
assert.deepEqual(generatedIds, expectedReadyIds, "Browser roster must exactly match RAW-ready manifest");

for (const monster of Object.values(generated)) {
  assert.ok(Array.isArray(monster.source_trait_names), `${monster.id}: trait fingerprint missing`);
  assert.ok(Array.isArray(monster.source_reaction_names), `${monster.id}: reaction fingerprint missing`);
  assert.ok(Array.isArray(monster.source_bonus_action_names), `${monster.id}: bonus-action fingerprint missing`);
  assert.ok(Array.isArray(monster.source_limited_use_names), `${monster.id}: limited-use fingerprint missing`);
  assert.ok(Array.isArray(monster.source_legendary_action_names), `${monster.id}: legendary fingerprint missing`);
  assert.deepEqual(
    Object.keys(monster.movement_modes).sort(),
    [
      "burrow_ft", "climb_ft", "fly_ft", "hover",
      "pass_through_creatures_as_difficult_terrain", "swim_ft", "walk_ft",
    ],
    `${monster.id}: movement fingerprint incomplete`,
  );
}

const goat = generated["srd-goat"];
assert.ok(goat);
assert.equal(goat.attacks[0].fixedDamage, 1);
assert.deepEqual(goat.attacks[0].charge, {
  minimumMove: 20,
  replacementDamage: { diceCount: 1, diceSize: 4, damageBonus: 0, damageType: "bludgeoning" },
});

const boar = generated["srd-boar"];
assert.ok(boar);
assert.deepEqual(boar.attacks.find((item) => item.id === "boar-gore").charge, {
  minimumMove: 20,
  diceCount: 1,
  diceSize: 6,
  damageType: "piercing",
  proneMaxSize: "medium",
});

const allosaurus = generated["srd-allosaurus"];
assert.ok(allosaurus);
assert.deepEqual(allosaurus.attacks.find((item) => item.id === "allosaurus-claws").charge, {
  minimumMove: 30,
  proneMaxSize: "large",
  followUpAttackId: "allosaurus-bite",
});

const triceratops = generated["srd-triceratops"];
assert.ok(triceratops);
assert.deepEqual(triceratops.attacks.find((item) => item.id === "triceratops-gore").charge, {
  minimumMove: 20,
  diceCount: 2,
  diceSize: 8,
  damageType: "piercing",
  proneMaxSize: "huge",
});

for (const [monsterId, attackId, maxTargetSize, grappleEscapeDc] of [
  ["srd-giant-scorpion", "srd-giant-scorpion-claw", "large", 13],
  ["srd-grick", "srd-grick-tentacles", "medium", 12],
  ["srd-griffon", "srd-griffon-rend", "medium", 14],
]) {
  const attack = generated[monsterId]?.attacks.find((item) => item.id === attackId);
  assert.ok(attack, `${monsterId}: expected grapple attack missing`);
  assert.deepEqual(attack.controlEffect, { maxTargetSize, grappleEscapeDc });
}

const merfolk = generated["srd-merfolk-skirmisher"];
assert.ok(merfolk);
assert.deepEqual(merfolk.attacks.map((item) => item.kind), ["ranged", "melee"]);
assert.deepEqual(merfolk.attacks[0].onHitModifiers, [
  { kind: "speed", flatBonus: -10, expiresAtEndOfTargetTurn: true },
]);

const worg = generated["srd-worg"];
assert.ok(worg);
assert.deepEqual(worg.attacks[0].onHitModifiers, [{
  kind: "attacks-against-advantage",
  consumeOnAttackAgainst: true,
  expiresAtStartOfSourceTurn: true,
}]);

for (const file of [
  "browser-heroes.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-modifiers.js", "browser-state.js",
  "browser-rage.js", "browser-rolls.js", "browser-timed-conditions.js", "browser-zero-hp.js",
  "browser-attack.js", "browser-charge.js", "browser-saves.js", "browser-condition-lifecycle.js",
  "browser-formation.js", "browser-multiattack.js",
]) load(file);

window.IRON_PIT_DICE = {
  roll: (sides) => sides === 20 ? 15 : 1,
  rollMany: (count, sides) => Array.from({ length: count }, () => sides === 20 ? 15 : 1),
};
const S = window.IRON_PIT_BROWSER_STATE;
const C = window.IRON_PIT_BROWSER_CHARGE;
const combatant = (id, side, template) => ({
  combatant_id: id,
  side,
  position_ft: side === "monsters" ? 5 : 0,
  state: S.buildState(structuredClone(template)),
});

const attacker = combatant("monster-1:srd-allosaurus", "monsters", allosaurus);
const target = combatant(
  "hero-1:karnok-stoneward-l1", "heroes", window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"],
);
attacker.state.initiative_total = 20;
target.state.initiative_total = 10;
S.beginTurn(attacker.state);
const chargeResult = C.resolveClosing(1, 1, attacker, target, {
  heroes: [target], monsters: [attacker],
});
assert.equal(chargeResult.handled, true);
assert.deepEqual(
  chargeResult.events.filter((event) => event.event_type === "attack").map((event) => event.weapon_id),
  ["allosaurus-claws", "allosaurus-bite"],
);

console.log(`Generated monster runtime matches ${generatedIds.length} RAW-ready manifest entries and executes declarative Charge/control mechanics.`);