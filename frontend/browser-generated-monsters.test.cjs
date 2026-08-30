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
assert.equal(Object.keys(manual).length, 67);
assert.equal(Object.keys(generated).length, 67);
assert.deepEqual(Object.keys(generated).sort(), Object.keys(manual).sort());

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
  charge: item.charge || null,
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
  assert.deepEqual(normalized(generated[id]), normalized(manual[id]), `${id} generated runtime drifted from certified browser data`);
}

console.log("Generated monster roster matches all 67 certified production templates.");
