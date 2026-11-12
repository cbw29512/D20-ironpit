"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name },
);
load("browser-spoken-language-eligibility.js");
const match = window.IRON_PIT_BROWSER_SPOKEN_LANGUAGES.understood;

const source = { spoken: ["common"], understood: ["common"], speaksAll: false };
const target = { spoken: [], understood: ["common"], understandsAll: false };
assert.equal(match(source, target), true);
assert.equal(match(source, { understood: ["draconic"] }), false);
assert.equal(match({ spoken: ["aquan"] }, { understood: ["ignan"] }), true);
assert.equal(match({ spoken: ["auran"] }, { understood: ["primordial"] }), true);
assert.equal(match({ spoken: ["infernal"] }, { understandsAll: true }), true);
assert.equal(match({ speaksAll: true }, { understood: ["common"] }), true);
assert.equal(match({ speaksAll: true }, { understood: [] }), false);
assert.equal(match(null, target), false);
assert.equal(match(source, null), false);
assert.equal(match({ spoken: [] }, target), false);

window.IRON_PIT_BROWSER_STATE = { distance: () => 5 };
window.IRON_PIT_BROWSER_CONDITION_RULES = { canSee: () => true };
load("browser-spell-policy-support.js");
const caster = {
  combatant_id: "caster", side: "monsters",
  state: { template: { name: "Caster", languageProfile: source } },
};
const victim = {
  combatant_id: "victim", side: "heroes",
  state: {
    template: { name: "Victim", creature_type: "humanoid", languageProfile: target },
    is_alive: true, is_dead: false, current_hp: 10, active_effect_ids: [],
  },
};
const setup = { heroes: [victim], monsters: [caster] };
const commandLike = {
  id: "renamed-order", range: 60, requiresSharedSpokenLanguage: true,
  requiresTargetSight: true, excludedTargetCreatureTypes: ["undead"],
};
const legal = window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT.legalSingleTargets;
assert.deepEqual(legal(caster, setup, commandLike), [victim]);
victim.state.template.languageProfile = { understood: ["draconic"] };
assert.deepEqual(legal(caster, setup, commandLike), []);
victim.state.template.languageProfile = undefined;
assert.deepEqual(legal(caster, setup, commandLike), []);
victim.state.template.languageProfile = target;
victim.state.template.creature_type = "undead";
assert.deepEqual(legal(caster, setup, commandLike), []);

load("browser-spell-resolution-effects.js");
const spellChoice = {
  slotLevel: 1, targetIds: ["victim"],
  action: {
    id: "renamed-order", name: "Renamed Order", level: 1,
    range: 60, saveAbility: "wisdom", dc: 11,
    requiresSharedSpokenLanguage: true,
  },
};
const direct = window.IRON_PIT_BROWSER_SPELL_RESOLUTION_EFFECTS;
assert.equal(direct.saveAction(spellChoice).requiresSharedSpokenLanguage, true);
victim.state.template.creature_type = "humanoid";
victim.state.template.languageProfile = { understood: ["draconic"] };
assert.throws(
  () => direct.resolveEffect(1, 1, caster, setup, spellChoice, "1:caster"),
  /lacks proven comprehension/,
);
console.log("Browser shared spoken-language target legality and direct resolution guard passed.");
