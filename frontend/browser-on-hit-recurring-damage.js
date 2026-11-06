(() => {
  "use strict";

  // Card-driven on-hit debuff. No monster or printed Action name is dispatched.
  function applyOnHit(target, attacker, attack) {
    try {
      const spec = attack.onHitRecurringDamage;
      if (!spec || target.state.is_dead || !target.state.is_alive) return null;
      if (spec.tickTiming !== "target_turn_end" || spec.stacking !== "nonstacking"
        || !spec.effectId || !Number.isInteger(spec.diceCount) || spec.diceCount <= 0
        || !Number.isInteger(spec.diceSize) || spec.diceSize < 2 || !spec.damageType) {
        throw new Error("Incomplete source-declared recurring hit damage.");
      }
      const state = target.state;
      state.timed_effects ||= [];
      if (state.timed_effects.some((item) => item.effect_id === spec.effectId)) return null;
      state.timed_effects.push({
        effect_id: spec.effectId,
        source_id: attacker.combatant_id,
        source_effect_id: attack.id,
        source_name: attack.name,
        ends_if_source_dead: Boolean(spec.endsIfSourceDead),
        allowed_removal_action_ids: [...(spec.removalActionIds || [])],
        expires_at_start_of_source_turn: false,
        end_of_turn_dice_count: spec.diceCount,
        end_of_turn_dice_size: spec.diceSize,
        end_of_turn_damage_type: spec.damageType,
      });
      state.active_effect_ids ||= [];
      if (!state.active_effect_ids.includes(spec.effectId)) {
        state.active_effect_ids.push(spec.effectId);
      }
      return spec.effectId;
    } catch (error) {
      console.error("Browser recurring on-hit damage failed.", { attack: attack?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ON_HIT_RECURRING_DAMAGE = { applyOnHit };
})();
