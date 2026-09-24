"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;

window.IRON_PIT_ACTION_ECONOMY = { available: () => true };
window.IRON_PIT_BROWSER_SPELLCASTING = { slotSpellAvailable: () => true };
window.IRON_PIT_BROWSER_STATE = { effectiveMaxHp: (state) => state.template.max_hp };
window.IRON_PIT_BROWSER_SPELL_AREA = {};
window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS = { healingMaximized: () => false };

vm.runInThisContext(
  fs.readFileSync("frontend/browser-healing-policy.js", "utf8"),
  { filename: "browser-healing-policy.js" },
);

const healer = {
  combatant_id: "cleric",
  side: "heroes",
  position_ft: 0,
  state: {
    template: {
      max_hp: 100,
      traits: [],
      outgoing_healing_dice_maximizer: {
        source_id: "supreme-healing",
        source_name: "Supreme Healing",
      },
    },
  },
};

const target = {
  combatant_id: "ally",
  side: "heroes",
  position_ft: 0,
  state: {
    current_hp: 50,
    is_alive: true,
    is_dead: false,
    template: { max_hp: 100, traits: [] },
  },
};

assert.equal(
  window.IRON_PIT_BROWSER_HEALING_POLICY.healingMaximized(healer, target),
  true,
  "caster-owned outgoing healing maximizer must maximize healing dice",
);

delete healer.state.template.outgoing_healing_dice_maximizer;
assert.equal(
  window.IRON_PIT_BROWSER_HEALING_POLICY.healingMaximized(healer, target),
  false,
  "healing is not maximized when neither caster nor recipient owns a maximizer",
);

window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS.healingMaximized = () => true;
assert.equal(
  window.IRON_PIT_BROWSER_HEALING_POLICY.healingMaximized(healer, target),
  true,
  "recipient-owned Beacon-style maximization remains compatible",
);

console.log("Browser outgoing healing maximization regressions passed.");
