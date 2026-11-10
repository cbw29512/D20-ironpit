(() => {
  "use strict";

  const sizes = new Set(["tiny", "small", "medium", "large", "huge", "gargantuan"]);

  function apply(state, sourceId, actionId, size) {
    try {
      if (!sizes.has(size)) throw new Error("Temporary size requires a legal creature size.");
      if (state.replacement_form) throw new Error("Size override cannot overlap a replacement form.");
      if ((state.timed_effects || []).some((item) => item.owned_override_size != null)) {
        throw new Error("A size override is already active.");
      }
      const matching = (state.timed_effects || []).filter((item) =>
        item.source_id === sourceId && item.source_effect_id === actionId);
      if (matching.length !== 1) throw new Error("Temporary size requires exactly one owned timed effect.");
      if (state.template.size === size) throw new Error("Size override must change the actual size.");
      matching[0].owned_previous_size = state.template.size;
      matching[0].owned_override_size = size;
      state.template = { ...state.template, size };
    } catch (error) {
      console.error("Browser timed size override failed", { sourceId, actionId, size, error });
      throw error;
    }
  }

  function restore(state, effect) {
    try {
      const previous = effect.owned_previous_size;
      const current = effect.owned_override_size;
      if (current == null) return;
      if (!previous || state.template.size !== current) {
        throw new Error("Temporary size source ownership drifted during cleanup.");
      }
      state.template = { ...state.template, size: previous };
    } catch (error) {
      console.error("Browser timed size restoration failed", { effectId: effect?.effect_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TIMED_SIZE_OVERRIDE = { apply, restore };
})();
