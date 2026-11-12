"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-spoken-language.js"), "utf8"),
  { filename: "browser-spoken-language.js" },
);
const L = window.IRON_PIT_BROWSER_SPOKEN_LANGUAGE;
const cases = [
  [ ["common"], ["common"], true ],
  [ ["common"], ["goblin"], false ],
  [ [], ["common"], false ],
  [ ["goblin"], [], false ],
  [ ["all"], ["draconic"], true ],
  [ ["draconic"], ["all"], true ],
  [ [], ["all"], false ],
  [ ["common"], [], false ],
];
for (const [spoken, understood, expected] of cases) {
  assert.equal(L.understands(
    { name: "renamed source", spoken_languages: spoken },
    { name: "renamed target", understood_languages: understood },
  ), expected);
}

// Validate the ordinary browser save-spell target filter also uses this one
// language predicate rather than implementing name-specific Command behavior.
window.IRON_PIT_BROWSER_STATE = { distance: () => 20 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-spell-policy-support.js"), "utf8"),
  { filename: "browser-spell-policy-support.js" },
);
const caster = {
  combatant_id: "caster", side: "monsters",
  state: { template: { spoken_languages: ["common"] }, resources: {} },
};
const target = (id, language) => ({
  combatant_id: id, side: "heroes",
  state: {
    template: {
      understood_languages: language ? [language] : [],
      creature_type: "humanoid",
    },
    current_hp: 10, is_alive: true, is_dead: false, active_effect_ids: [],
  },
});
const setup = {
  monsters: [caster],
  heroes: [target("understands", "common"), target("unknown", null), target("other", "goblin")],
};
const policy = window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT;
for (const name of ["Command", "Renamed Spell"]) {
  const legal = policy.legalSingleTargets(caster, setup, {
    id: name, name, level: 1, range: 60, requiresSharedSpokenLanguage: true,
    requiresTargetHearing: true, requiresTargetSight: true,
  });
  assert.deepEqual(legal.map((item) => item.combatant_id), ["understands"]);
}

console.log("Browser spoken-language eligibility and save-spell targeting passed.");
