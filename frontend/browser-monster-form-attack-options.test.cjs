"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(
  path.join(__dirname, "browser-monster-form-attack-options.js"), "utf8",
));
const merge = window.IRON_PIT_BROWSER_MONSTER_FORM_ATTACK_OPTIONS.composeMonsterFormAttackSequences;
const owner = {
  id: "2014-deva", kind: "monster", ruleset: "2014",
  attack_action: {
    id: "deva-multi", name: "Multiattack", isAttackAction: true,
    slots: [{ attackIds: ["mace"] }, { attackIds: ["mace"] }],
  },
};
const form = {
  id: "2014-giant-shape", kind: "monster", ruleset: "2014",
  attack_action: {
    id: "shape-multi", name: "Multiattack", isAttackAction: true,
    slots: [
      { attackIds: ["claw"] },
      { attackIds: ["sting"], previousAttack: { sameTarget: true } },
    ],
  },
};
const result = merge(owner, form);
assert.equal(result.variants.length, 2);
assert.deepEqual(result.variants.map((x) => x.id),
  ["2014-deva:deva-multi", "2014-giant-shape:shape-multi"]);
assert.deepEqual(result.variants[0].slots.map((x) => x.attackIds), [["mace"], ["mace"]]);
assert.equal(result.variants[1].slots[1].previousAttack.sameTarget, true);
assert.equal(result.slots, undefined, "Do not concatenate the two source Actions");
assert.equal(result.isAttackAction, true);
assert.equal(form.attack_action.slots[1].previousAttack.sameTarget, true);
const variants = {
  ...form, attack_action: {
    ...form.attack_action, slots: undefined, isAttackAction: false,
    variants: [
      { id: "melee", slots: [{ attackIds: ["claw"] }] },
      { id: "ranged", slots: [{ attackIds: ["rock"] }] },
    ],
  },
};
const variation = merge(owner, variants);
assert.deepEqual(variation.variants.map((x) => x.id),
  ["2014-deva:deva-multi", "2014-giant-shape:melee", "2014-giant-shape:ranged"]);
assert.equal(variation.isAttackAction, false);
assert.throws(() => merge(owner, { ...form, ruleset: "2024" }), /edition/);
assert.throws(() => merge({ ...owner, kind: "character" }, form), /Only monster/);
assert.throws(() => merge(owner, {
  ...form, attack_action: { ...form.attack_action, name: "Other Action" },
}), /Distinctly named/);
assert.equal(merge({ ...owner, attack_action: null }, { ...form, attack_action: null }), null);
const copy = merge(owner, { ...form, attack_action: null });
assert.notEqual(copy, owner.attack_action);
assert.deepEqual(copy, owner.attack_action);
console.log("Universal source-form alternative Attack Action composition passed.");
