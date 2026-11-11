(() => {
  "use strict";

  // Card-driven nonstacking debuff shared by weapon hits and movement triggers.
  function applyFromSource(target, sourceId, sourceEffectId, sourceName, spec) {
    try {
      if (!spec || target.state.is_dead || !target.state.is_alive) return null;
      if (!["target_turn_start", "target_turn_end"].includes(spec.tickTiming) || spec.stacking !== "nonstacking"
        || !spec.effectId || !Number.isInteger(spec.diceCount) || spec.diceCount <= 0
        || !Number.isInteger(spec.diceSize) || spec.diceSize < 2 || !spec.damageType) {
        throw new Error("Incomplete source-declared recurring hit damage.");
      }
      const state = target.state;
      state.timed_effects ||= [];
      if (state.timed_effects.some((item) => item.effect_id === spec.effectId)) return null;
      state.timed_effects.push({
        effect_id: spec.effectId,
        source_id: sourceId,
        source_effect_id: sourceEffectId,
        source_name: sourceName,
        ends_if_source_dead: Boolean(spec.endsIfSourceDead),
        allowed_removal_action_ids: [...(spec.removalActionIds || [])],
        expires_at_start_of_source_turn: false,
        end_of_turn_dice_count: spec.tickTiming === "target_turn_end" ? spec.diceCount : 0,
        end_of_turn_dice_size: spec.diceSize,
        end_of_turn_damage_type: spec.tickTiming === "target_turn_end" ? spec.damageType : null,
        start_of_turn_dice_count: spec.tickTiming === "target_turn_start" ? spec.diceCount : 0,
        start_of_turn_dice_size: spec.diceSize,
        start_of_turn_damage_type: spec.tickTiming === "target_turn_start" ? spec.damageType : null,
      });
      state.active_effect_ids ||= [];
      if (!state.active_effect_ids.includes(spec.effectId)) {
        state.active_effect_ids.push(spec.effectId);
      }
      return spec.effectId;
    } catch (error) {
      console.error("Browser recurring source damage failed.", { sourceEffectId, error });
      throw error;
    }
  }

  function applyOnHit(target, attacker, attack) {
    try {
      const spec = attack.onHitRecurringDamage;
      if (!spec) return null;
      return applyFromSource(target, attacker.combatant_id, attack.id, attack.name, spec);
    } catch (error) {
      console.error("Browser on-hit recurring damage failed.", { attack: attack?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ON_HIT_RECURRING_DAMAGE = { applyOnHit, applyFromSource };
})();
