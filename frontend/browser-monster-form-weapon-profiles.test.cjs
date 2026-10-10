"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname,
  "browser-monster-form-weapon-profiles.js"), "utf8"));
const compose = window.IRON_PIT_BROWSER_MONSTER_FORM_WEAPON_PROFILES.composeMonsterFormWeaponProfiles;
const owner = {
  id: "2014-original-monster", kind: "monster", ruleset: "2014",
  ability_scores: { strength: 18, dexterity: 18 },
  attacks: [{
    id: "angel-mace", bonus: 8, damageBonus: 4,
    attackAbility: "strength", attackAbilityModifier: 4,
    onHitDamage: [{ source: "printed-radiant-rider", diceCount: 4, diceSize: 8, damageType: "radiant" }],
    damageSourceQualifiers: ["magical"],
  }],
};
const form = {
  id: "2014-source-form", kind: "monster", ruleset: "2014",
  ability_scores: { strength: 12, dexterity: 15 },
  attacks: [{ id: "form-bite", bonus: 4, damageBonus: 1, diceCount: 1, diceSize: 6 }],
};
const out = compose(owner, form, { "angel-mace": { ability: "strength", addsAbilityToDamage: true } });
assert.equal(out.length, 2);
assert.equal(out[0].bonus, 5);
assert.equal(out[0].damageBonus, 1);
assert.equal(out[0].attackAbilityModifier, 1);
assert.deepEqual(out[0].onHitDamage, owner.attacks[0].onHitDamage);
assert.equal(out[0].onHitDamage.length, 1);
assert.deepEqual(out[0].damageSourceQualifiers, ["magical"]);
assert.deepEqual(out[1], form.attacks[0]);
assert.notStrictEqual(out[1], form.attacks[0]);
assert.equal(owner.attacks[0].bonus, 8);
assert.throws(() => compose(owner, form, {}), /provenance/);
assert.throws(() => compose(owner, form, { "angel-mace": {
  ability: "dexterity", addsAbilityToDamage: true,
}}), /conflicts/);
assert.throws(() => compose(owner, { ...form, ruleset: "2024" }, {
  "angel-mace": { ability: "strength", addsAbilityToDamage: true },
}), /same-edition/);
assert.throws(() => compose({
  ...owner, attacks: [{ ...owner.attacks[0], fixedDamage: 7 }],
}, form, { "angel-mace": { ability: "strength", addsAbilityToDamage: true } }), /Fixed-damage/);
console.log("Universal Change Shape weapon profile bonus/rider parity passed.");
