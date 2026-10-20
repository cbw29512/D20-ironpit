(() => {
  "use strict";

  // Source cards select available abilities. The target selects the best chance.
  // This module never looks at source names or monster identities.
  function choose(state, choices, dc, context = {}) {
    try {
      if (!Array.isArray(choices) || choices.length < 2 || new Set(choices).size !== choices.length) {
        throw new Error("A chosen saving throw needs distinct source-declared abilities.");
      }
      const saves = window.IRON_PIT_BROWSER_SAVING_THROWS;
      if (!saves?.saveMode) throw new Error("Universal saving-throw runtime unavailable.");
      const modifier = window.IRON_PIT_BROWSER_MODIFIERS;
      const reductions = window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION;
      let best = null;
      let chance = -1;
      for (const ability of choices) {
        const printed = state.template.saving_throw_bonuses?.[ability];
        if (!Number.isFinite(printed)) throw new Error(`Missing certified ${ability} saving throw.`);
        const live = printed + (reductions?.abilityModifierDelta(state, ability) || 0)
          + (modifier?.savingThrowFlat?.(state, ability) || 0);
        let p = Math.max(0, Math.min(1, (21 + live - dc) / 20));
        const mode = saves.saveMode(state, ability, context);
        if (mode === "advantage") p = 1 - (1 - p) ** 2;
        else if (mode === "disadvantage") p = p ** 2;
        else if (mode !== "normal") throw new Error(`Unsupported save mode ${mode}.`);
        if (p > chance) {
          chance = p;
          best = ability;
        }
      }
      if (!best) throw new Error("No legal target-chosen saving throw.");
      return best;
    } catch (error) {
      console.error("Failed to select target's saving throw ability", { dc, choices, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE = { choose };
})();
