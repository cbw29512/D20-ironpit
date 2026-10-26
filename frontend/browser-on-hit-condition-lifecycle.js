(() => {
  "use strict";

  function attachStartTurnDamage(state, effectId, sourceId, sourceEffectId, spec) {
    try {
      const count = spec.startOfTurnDamageDiceCount || 0;
      if (!count) return;
      if (!Number.isInteger(count) || count < 1 || count > 40
          || !Number.isInteger(spec.startOfTurnDamageDiceSize)
          || spec.startOfTurnDamageDiceSize < 2 || !spec.startOfTurnDamageType) {
        throw new Error("Invalid start-turn damage condition metadata.");
      }
      const timed = (state.timed_effects || []).find((item) =>
        item.effect_id === effectId && item.source_id === sourceId
        && (item.source_effect_id || null) === (sourceEffectId || null));
      if (!timed) throw new Error("Applied timed condition is missing from fight state.");
      timed.start_of_turn_dice_count = count;
      timed.start_of_turn_dice_size = spec.startOfTurnDamageDiceSize;
      timed.start_of_turn_damage_type = spec.startOfTurnDamageType;
    } catch (error) {
      console.error("Failed to attach start-turn condition damage", {
        effectId, sourceId, sourceEffectId, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ON_HIT_CONDITION_LIFECYCLE = { attachStartTurnDamage };
})();
