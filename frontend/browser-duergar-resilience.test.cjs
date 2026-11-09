"use strict";

// The browser consumes the same generic saving_throw_advantage_grants card
// fields emitted by the Python compiler. No Duergar-specific JS exists.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);

window.IRON_PIT_BROWSER_CONDITION_RULES = { autoFailStrDex: () => false };
window.IRON_PIT_BROWSER_BARBARIAN2 = { dangerSenseAdvantage: () => 0 };
window.IRON_PIT_BROWSER_DODGE = { dexSaveAdvantageSources: () => 0 };
window.IRON_PIT_BROWSER_EXHAUSTION = { saveDisadvantage: () => 0, d20Modifier: () => 0 };
load("browser-opening-modifiers.js");
load("browser-modifier-validation.js");
load("browser-modifiers.js");
load("browser-defensive-modifier-rules.js");
load("browser-rolls.js");
load("browser-saving-throws.js");

const abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"];
const makeGrant = (id, extra = {}) => ({
  source_id: `duergar-resilience-${id}`, source_name: "Duergar Resilience",
  abilities, ...extra,
});
const template = {
  id: "synthetic-resilient-creature", name: "Renamed creature",
  saving_throw_bonuses: Object.fromEntries(abilities.map((key) => [key, 0])),
  saving_throw_advantage_grants: [
    makeGrant("spells", { requires_spell_effect: true }),
    ...["poison", "illusion", "charm", "paralyzed"]
      .map((tag) => makeGrant(tag, { required_effect_tags: [tag] })),
  ],
};
const state = {
  template, active_effect_ids: [],
  active_modifiers: window.IRON_PIT_BROWSER_OPENING_MODIFIERS.build(template),
};

function verify(context, mode) {
  try {
    const dice = mode === "advantage" ? [3, 17] : [11];
    window.IRON_PIT_DICE = {
      roll: (sides) => {
        const value = dice.shift();
        assert.ok(value >= 1 && value <= sides, "unexpected extra die roll");
        return value;
      },
      rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
    };
    const result = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
      state, "wisdom", 99, context,
    );
    assert.equal(result.roll.mode, mode);
    assert.equal(dice.length, 0);
    const names = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS.saveAdvantageSourceNames(
      state, "wisdom", context,
    );
    assert.deepEqual(names, mode === "advantage" ? ["Duergar Resilience"] : []);
  } catch (error) {
    console.error("Browser Duergar Resilience parity failed", { context, mode, error });
    throw error;
  }
}

for (const context of [
  { spellEffect: true, magicalEffect: true },
  ...["poison", "illusion", "charm", "paralyzed"].map((tag) => ({ effectTags: [tag] })),
  { spellEffect: true, effectTags: ["poison"] },
]) verify(context, "advantage");

for (const context of [
  {}, { magicalEffect: true }, { effectTags: ["frightened"] },
]) verify(context, "normal");

console.log("Browser Duergar Resilience universal-save regressions passed.");
