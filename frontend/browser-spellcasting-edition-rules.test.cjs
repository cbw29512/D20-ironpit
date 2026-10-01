"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync("frontend/browser-spellcasting.js", "utf8"),
  { filename: "browser-spellcasting.js" },
);

const C = window.IRON_PIT_BROWSER_SPELLCASTING;

function state(ruleset) {
  return {
    template: { id: `${ruleset}-caster`, ruleset },
    resources: { "spell-slot-1": 2, "spell-slot-2": 2 },
    spell_slot_expended_turn_key: null,
    bonus_action_spell_cast_turn_key: null,
    non_action_cantrip_spell_cast_turn_key: null,
  };
}

{
  const s = state("2014"), turnKey = "1:cleric";
  C.markSlotSpellCast(s, turnKey, { spellLevel: 2, actionCost: "bonus_action" });
  assert.equal(s.spell_slot_expended_turn_key, null);
  assert.equal(s.bonus_action_spell_cast_turn_key, turnKey);
  assert.equal(s.non_action_cantrip_spell_cast_turn_key, turnKey);
  assert.equal(C.spellCastAvailable(s, turnKey, 0, "action", { expendsSpellSlot: false }), true);
  assert.equal(C.spellCastAvailable(s, turnKey, 1, "action", { expendsSpellSlot: true }), false);
  assert.equal(C.spellCastAvailable(s, turnKey, 1, "reaction", { expendsSpellSlot: true }), false);
  assert.equal(C.spellCastAvailable(s, "1:enemy", 1, "reaction", { expendsSpellSlot: true }), true);
}

{
  const s = state("2014"), turnKey = "1:cleric";
  C.markSlotSpellCast(s, turnKey, { spellLevel: 1, actionCost: "action" });
  assert.equal(C.slotSpellAvailable(s, turnKey, { spellLevel: 2, actionCost: "action" }), true);
  assert.equal(C.slotSpellAvailable(s, turnKey, { spellLevel: 1, actionCost: "bonus_action" }), false);
}

{
  const s = state("2024"), turnKey = "1:cleric";
  C.markSlotSpellCast(s, turnKey, { spellLevel: 1, actionCost: "action" });
  assert.equal(s.spell_slot_expended_turn_key, turnKey);
  assert.equal(C.slotSpellAvailable(s, turnKey, { spellLevel: 2, actionCost: "bonus_action" }), false);
  assert.equal(C.spellCastAvailable(s, turnKey, 0, "action", { expendsSpellSlot: false }), true);
  assert.equal(C.spellCastAvailable(s, turnKey, 2, "action", { expendsSpellSlot: false }), true);
}

console.log("Browser edition-aware spellcasting regressions passed.");
