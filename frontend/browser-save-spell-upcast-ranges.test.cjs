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
window.IRON_PIT_BROWSER_SPELL_POLICY = {
  slotLevels: (member, action) => {
    if (action.level === 0) return [0];
    const maximum = action.upcastDicePerLevel > 0 ? 9 : action.level;
    const levels = [];
    for (let level = action.level; level <= maximum; level += 1) {
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
      spell_attack_actions: [],
      spell_save_actions: [{
        id: "scaling-save",
        level: 1,
        actionCost: "action",
        range: 60,
        areaRadius: null,
        concentration: false,
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
assert.ok(ranges.some((item) => item.family === "spell" && item.range === 60));

console.log("Browser offensive ranges preserve save-spell legal upcast availability.");
