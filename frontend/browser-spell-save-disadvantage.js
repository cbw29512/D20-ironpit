(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_RESOURCES;

  function waived(state, option, turnKey) {
    if (!option?.waivedWhileSourceEffectId) return false;
    const active = (state.timed_effects || []).some(
      (effect) => effect.source_effect_id === option.waivedWhileSourceEffectId,
    );
    if (!active) return false;
    if (option.waivedOncePerTurn && turnKey != null) {
      return (state.feature_last_turn_keys || {})[option.id] !== turnKey;
    }
    return true;
  }

  function choose(state, turnKey) {
    try {
      const options = state.template.spellSaveDisadvantageOptions || [];
      const legal = options.filter((option) =>
        R().available(state, option.resourceId, option.resourceCost || 1)
        || waived(state, option, turnKey));
      legal.sort((a, b) => (b.priority || 0) - (a.priority || 0));
      return legal[0] || null;
    } catch (error) {
      console.error("Browser spell-save Disadvantage selection failed", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function spend(state, option, turnKey) {
    try {
      if (!option) return null;
      if (waived(state, option, turnKey)) {
        if (option.waivedOncePerTurn && turnKey != null) {
          state.feature_last_turn_keys = state.feature_last_turn_keys || {};
          state.feature_last_turn_keys[option.id] = turnKey;
        }
        return null;
      }
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
