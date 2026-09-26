(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_RESOURCES;

  function choose(state) {
    try {
      const options = state.template.spellSaveDisadvantageOptions || [];
      const legal = options.filter((option) =>
        R().available(state, option.resourceId, option.resourceCost || 1));
      legal.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return legal[0] || null;
    } catch (error) {
      console.error("Browser spell-save Disadvantage selection failed", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function spend(state, option) {
    try {
      if (!option) return null;
      return R().spend(state, option.resourceId, option.resourceCost || 1);
    } catch (error) {
      console.error("Browser spell-save Disadvantage resource spending failed", {
        combatant: state?.template?.name, option: option?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_SAVE_DISADVANTAGE = { choose, spend };
})();
