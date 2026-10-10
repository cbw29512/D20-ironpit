"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-monster-form-weapon-traits.js"), "utf8"));
const apply = window.IRON_PIT_BROWSER_MONSTER_FORM_WEAPON_TRAITS.inheritWeaponHitTraitForForm;
const rider = { source: "2014:deva:Angelic Weapons", diceCount: 4, diceSize: 8,
  damageBonus: 0, damageType: "radiant" };
const owner = { kind: "monster", ruleset: "2014", attacks: [
  { id: "owner-mace", onHitDamage: [{ source: "printed-mace", diceCount: 4,
    diceSize: 8, damageBonus: 0, damageType: "radiant" }], damageSourceQualifiers: ["magical"] }
]};
const form = { kind: "monster", ruleset: "2014", attacks: [{ id: "form-claw" }]};
const out = apply(owner, form, [...owner.attacks, ...form.attacks], rider, true);
assert.equal(out[0].onHitDamage.length, 1, "original printed rider not doubled");
assert.equal(out[1].onHitDamage.length, 1);
assert.deepEqual(out[1].onHitDamage[0], rider);
assert.deepEqual(out[1].damageSourceQualifiers, ["magical"]);
assert.deepEqual(apply(owner, form, out, rider, true), out, "no duplicate on repeat");
assert.equal(form.attacks[0].onHitDamage, undefined);
assert.throws(() => apply(owner, form, owner.attacks, rider, true), /inventory/);
assert.throws(() => apply(owner, { ...form, ruleset: "2024" }, out, rider, true), /same-edition/);
assert.throws(() => apply(owner, form, [owner.attacks[0], { id: "form-claw",
  onHitDamage: [{ ...rider, diceCount: 5 }] }], rider, true), /conflicts/);
console.log("Source-gated universal transformed weapon hit traits pass browser parity.");
