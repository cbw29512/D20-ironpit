"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available,
  spend: (state, cost) => { if (cost === "reaction") state.reaction_available = false; },
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-reactions.js"), "utf8"), { filename: "browser-reactions.js" });

const defender = {
  reaction_available: true,
  template: { armor_class: 17, parry_reaction: { ac_bonus: 2 } },
};
const attack = { kind: "melee" };
const attackRoll = { selected_roll: 12, total: 20 };

const result = window.IRON_PIT_BROWSER_REACTIONS.parryHit(defender, attack, attackRoll, true, 19);
assert.deepEqual(result, { hit: false, used: true });
assert.equal(defender.reaction_available, false);

console.log("Browser Parry effective-AC regression passed.");
