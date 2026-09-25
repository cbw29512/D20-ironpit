"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
window.IRON_PIT_ACTION_ECONOMY = {
  available: () => true,
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  slotSpellAvailable: () => true,
};
window.IRON_PIT_BROWSER_STATE = {
  sizeAtMost: () => true,
};
window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = {
  slotLevels: (member, spell) => {
    if (spell.level === 0) return [0];
    const maximum = spell.upcastDicePerLevel > 0 ? 9 : spell.level;
    const levels = [];
    for (let level = spell.level; level <= maximum; level += 1) {
      if ((member.state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
    }
    return levels;
  },
};

vm.runInThisContext(
  fs.readFileSync("frontend/browser-offensive-ranges.js", "utf8"),
  { filename: "browser-offensive-ranges.js" },
);

const R = window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
const caster = {
  combatant_id: "caster",
  side: "heroes",
  state: {
    action_available: true,
    resources: { "spell-slot-2": 1 },
    template: {
      attacks: [],
      saving_throw_actions: [],
      spell_save_actions: [],
      spell_attack_actions: [{
        id: "guiding-bolt",
        level: 1,
        actionCost: "action",
        range: 120,
        upcastDicePerLevel: 1,
      }],
    },
  },
};
const target = {
  combatant_id: "target",
  side: "monsters",
  state: {
    grapple_sources: [],
    template: { size: "medium" },
  },
};

const ranges = R.rangesForTarget(caster, target, "1:caster");
assert.ok(ranges.some((item) => item.family === "spell" && item.range === 120));

console.log("Browser offensive ranges preserve spell-attack legal upcast availability.");
