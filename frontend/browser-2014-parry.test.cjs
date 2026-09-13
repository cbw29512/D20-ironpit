"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "reaction" && state.reaction_available,
  spend: (state, cost) => { if (cost === "reaction") state.reaction_available = false; },
};
load("browser-condition-immunity.js");
load("browser-condition-rules.js");
load("browser-reactions.js");

const X = window.IRON_PIT_BROWSER_REACTIONS;
const melee = { id: "rapier", kind: "melee" };
const ranged = { id: "bow", kind: "ranged" };
const incoming = { id: "claw", kind: "melee" };
const roll = { selected_roll: 12, total: 16 };

function defender() {
  return {
    reaction_available: true,
    active_effect_ids: [],
    wielded_attack_id: "rapier",
    template: {
      armor_class: 15,
      parry_reaction: { ac_bonus: 2 },
      primary_attack_id: "rapier",
      attacks: [melee, ranged],
    },
  };
}
function attacker() { return { active_effect_ids: [], template: { ruleset: "2014" } }; }

{
  const d = defender();
  assert.deepEqual(X.parryHit(d, attacker(), incoming, roll, true, 15), { hit: false, used: true });
  assert.equal(d.reaction_available, false);
}
{
  const d = defender(); d.active_effect_ids.push("blinded");
  assert.deepEqual(X.parryHit(d, attacker(), incoming, roll, true, 15), { hit: true, used: false });
  assert.equal(d.reaction_available, true);
}
{
  const d = defender(); d.wielded_attack_id = "bow";
  assert.deepEqual(X.parryHit(d, attacker(), incoming, roll, true, 15), { hit: true, used: false });
  assert.equal(d.reaction_available, true);
}
{
  const d = defender(); const a = attacker(); a.active_effect_ids.push("invisible");
  assert.deepEqual(X.parryHit(d, a, incoming, roll, true, 15), { hit: true, used: false });
  assert.equal(d.reaction_available, true);
}

console.log("2014 browser Parry RAW trigger regressions passed.");
