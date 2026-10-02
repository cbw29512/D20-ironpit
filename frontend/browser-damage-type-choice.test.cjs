"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_DICE = { roll: () => 1, rollMany: (count) => Array(count).fill(1) };
window.IRON_PIT_BROWSER_MODIFIERS = {
  damageSourceQualifiers: () => new Set(["attack", "unarmed"]),
};
window.IRON_PIT_BROWSER_ATTACK = {
  adjustedDamage: (target, amount, damageType) => {
    if ((target.template.damage_immunities || []).includes(damageType)) return 0;
    if ((target.template.damage_resistances || []).includes(damageType)) return Math.floor(amount / 2);
    if ((target.template.damage_vulnerabilities || []).includes(damageType)) return amount * 2;
    return amount;
  },
};

vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-rolls.js"), "utf8"),
  { filename: "browser-rolls.js" },
);

const attack = {
  id: "empowered-unarmed",
  kind: "melee",
  damageType: "bludgeoning",
  damageTypeChoices: ["force"],
  damageSourceQualifiers: ["unarmed"],
};

const attacker = {
  template: {
    name: "Kael",
    damage_resistance_bypass_grants: [],
  },
};

assert.equal(
  window.IRON_PIT_BROWSER_ROLLS.chooseDamageType(
    attacker,
    attack,
    { template: { damage_immunities: ["bludgeoning"], damage_resistances: [], damage_vulnerabilities: [] } },
    ["attack", "unarmed"],
  ),
  "force",
);

assert.equal(
  window.IRON_PIT_BROWSER_ROLLS.chooseDamageType(
    attacker,
    attack,
    { template: { damage_immunities: ["force"], damage_resistances: [], damage_vulnerabilities: [] } },
    ["attack", "unarmed"],
  ),
  "bludgeoning",
);

console.log("browser damage type choice regression passed");
