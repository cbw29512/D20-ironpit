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

  function availableFreeSpellCast(state, spellId) {
    try {
      for (const grant of state.template.free_spell_cast_grants || []) {
        if (grant.spell_id !== spellId) continue;
        if (!grant.resource_id) return grant;
        if (!(grant.resource_id in (state.resources || {}))) {
          throw new Error(`Free spell cast ${grant.source_id} references missing resource ${grant.resource_id}.`);
        }
        if ((state.resources[grant.resource_id] || 0) >= (grant.resource_cost || 1)) return grant;
      }
      return null;
    } catch (error) {
      console.error("Failed browser free spell-cast lookup", { spellId, error });
      throw error;
    }
  }

  function consumeFreeSpellCast(state, grant) {
    try {
      if (!grant.resource_id) return null;
      if (!(grant.resource_id in (state.resources || {}))) {
        throw new Error(`Free spell cast ${grant.source_id} references missing resource ${grant.resource_id}.`);
      }
      const cost = grant.resource_cost || 1;
      if ((state.resources[grant.resource_id] || 0) < cost) throw new Error(`${grant.source_name} has no uses remaining.`);
      state.resources[grant.resource_id] -= cost;
      return state.resources[grant.resource_id];
    } catch (error) {
      console.error("Failed browser free spell-cast consumption", { grant: grant.source_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELLCASTING = {
    availableFreeSpellCast, consumeFreeSpellCast, markSlotSpellCast, slotSpellAvailable,
  };
})();
