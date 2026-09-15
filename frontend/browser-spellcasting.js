(() => {
  "use strict";

  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function slotSpellAvailable(state, turnKey) {
    if (!turnKey) throw new Error("Spell-slot legality requires an active turn key.");
    return state.spell_slot_expended_turn_key !== turnKey;
  }

  function actionResourceAvailable(state, action, turnKey) {
    const level = action.level || 0;
    if (level < 0) throw new Error("Spell level cannot be negative.");
    const fallbackId = level > 0 ? `spell-slot-${level}` : null;
    const resolvedId = RES().resolvedId(action.resourceId, fallbackId);
    const usesSpellSlot = Boolean(resolvedId && resolvedId.startsWith("spell-slot-"));
    if (usesSpellSlot && !slotSpellAvailable(state, turnKey)) return false;
    return RES().actionAvailable(state, action.resourceId, action.resourceCost || 1, fallbackId);
  }

  function markSlotSpellCast(state, turnKey) {
    if (!slotSpellAvailable(state, turnKey)) {
      throw new Error("A spell slot has already been expended to cast a spell on this turn.");
    }
    state.spell_slot_expended_turn_key = turnKey;
  }

  window.IRON_PIT_BROWSER_SPELLCASTING = {
    actionResourceAvailable, markSlotSpellCast, slotSpellAvailable,
  };
})();