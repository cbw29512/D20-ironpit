(() => {
  "use strict";

  function sourceIds(state) {
    try {
      if (!window.IRON_PIT_BROWSER_CONDITION_RULES?.has(state, "charmed")) return new Set();
      return new Set(
        (state.timed_effects || [])
          .filter((effect) => effect.effect_id === "charmed" && effect.source_id)
          .map((effect) => effect.source_id),
      );
    } catch (error) {
      console.error("Failed to read Charmed sources", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  function blocks(actor, targetId) {
    try {
      return sourceIds(actor).has(targetId);
    } catch (error) {
      console.error("Failed to evaluate Charmed targeting", { combatant: actor?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CHARMED_TARGETING = { sourceIds, blocks };
})();
