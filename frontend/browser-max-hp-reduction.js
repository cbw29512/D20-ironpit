(() => {
  "use strict";

  function effectiveMaxHp(state) {
    try {
      return Math.max(0, state.template.max_hp + (state.max_hp_bonus || 0) - (state.max_hp_reduction || 0));
    } catch (error) {
      console.error("Failed to calculate effective max HP", { error });
      throw error;
    }
  }

  function apply(state, amount) {
    try {
      if (!Number.isInteger(amount) || amount < 0) throw new Error("Maximum HP reduction must be a non-negative integer.");
      const before = effectiveMaxHp(state);
      if (amount === 0 || before === 0) return { before, after: before };
      state.max_hp_reduction = (state.max_hp_reduction || 0) + amount;
      const after = effectiveMaxHp(state);
      state.current_hp = Math.min(state.current_hp, after);
      return { before, after };
    } catch (error) {
      console.error("Failed to apply maximum HP reduction", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAX_HP_REDUCTION = { apply, effectiveMaxHp };
})();
