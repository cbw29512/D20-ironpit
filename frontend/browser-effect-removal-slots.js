(() => {
  "use strict";
  // All effect-removal slot selection uses fight-local resource counts.
  // The real slot used defines automatic Dispel Magic strength.
  function choose(remover, action, turnKey, spellLevels = []) {
    try {
      const state = remover.state;
      if (!action.upcastSlotLevel) {
        if (!action.resourceId) return {id: null, level: action.autoRemoveMaxLevel ?? 3};
        if ((state.resources?.[action.resourceId] || 0) < (action.resourceCost || 1)) return null;
        return {id: action.resourceId, level: action.autoRemoveMaxLevel ?? 3};
      }
      if (!action.expendsSpellSlot || !action.resourceId)
        throw new Error("Higher-slot effect removal requires a declared spell-slot resource.");
      if (!window.IRON_PIT_BROWSER_SPELLCASTING.slotSpellAvailable(state, turnKey)) return null;
      const levels = [];
      for (let level = action.level; level <= 9; level++) {
        if ((state.resources?.[`spell-slot-${level}`] || 0) > 0) levels.push(level);
      }
      if (!levels.length) return null;
      const withinCapacity = spellLevels.filter((level) => level <= levels[levels.length - 1]);
      const needed = withinCapacity.length ? Math.max(...withinCapacity) : action.level;
      const level = levels.find((item) => item >= needed) || levels[0];
      return {id: `spell-slot-${level}`, level};
    } catch (error) {
      console.error("Effect removal slot selection failed", {actionId: action?.id, error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_EFFECT_REMOVAL_SLOTS = {choose};
})();
