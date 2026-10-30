(() => {
  "use strict";

  function note(state, amount, sourceId) {
    try {
      if (!(amount > 0) || sourceId == null) return;
      const normalized = String(sourceId).trim();
      if (!normalized) throw new Error("Damage source id cannot be blank.");
      state.damage_taken_this_turn_by_source ||= {};
      state.damage_taken_this_turn_by_source[normalized] =
        (state.damage_taken_this_turn_by_source[normalized] || 0) + amount;
    } catch (error) {
      console.error("Failed browser damage-source attribution.", {
        combatant: state?.template?.name, sourceId, error,
      });
      throw error;
    }
  }

  function clear(state) {
    try {
      state.damage_taken_this_turn_by_source = {};
    } catch (error) {
      console.error("Failed browser damage-source ledger clear.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_DAMAGE_SOURCE = { clear, note };
})();
