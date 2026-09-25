(() => {
  "use strict";

  function slotSpellAvailable(state, turnKey) {
    if (!turnKey) throw new Error("Spell-slot legality requires an active turn key.");
    return state.spell_slot_expended_turn_key !== turnKey;
  }

  function legalSlotLevels(state, turnKey, printedLevel, options = {}) {
    if (printedLevel === 0) return [0];
    if (!Number.isInteger(printedLevel) || printedLevel < 1 || printedLevel > 9) {
      throw new Error("Printed spell level must be between 0 and 9.");
    }
    if (!slotSpellAvailable(state, turnKey)) return [];
    const maximum = options.higherSlotScaling ? 9 : printedLevel;
    const levels = [];
    for (let level = printedLevel; level <= maximum; level += 1) {
      if ((state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
    }
    return levels;
  }

  function markSlotSpellCast(state, turnKey) {
    if (!slotSpellAvailable(state, turnKey)) {
      throw new Error("A spell slot has already been expended to cast a spell on this turn.");
    }
    state.spell_slot_expended_turn_key = turnKey;
  }

  window.IRON_PIT_BROWSER_SPELLCASTING = { legalSlotLevels, markSlotSpellCast, slotSpellAvailable };
})();
