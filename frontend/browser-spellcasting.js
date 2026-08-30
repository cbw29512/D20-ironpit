(() => {
  "use strict";

  function slotSpellAvailable(state, turnKey) {
    if (!turnKey) throw new Error("Spell-slot legality requires an active turn key.");
    return state.spell_slot_expended_turn_key !== turnKey;
  }

  function markSlotSpellCast(state, turnKey) {
    if (!slotSpellAvailable(state, turnKey)) {
      throw new Error("A spell slot has already been expended to cast a spell on this turn.");
    }
    state.spell_slot_expended_turn_key = turnKey;
  }

  window.IRON_PIT_BROWSER_SPELLCASTING = { markSlotSpellCast, slotSpellAvailable };
})();
