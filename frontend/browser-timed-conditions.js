(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const POISONED = "poisoned", TIMED_PENALTY = "timed-penalty";

  function apply(state, effectId, sourceId, options = {}) {
    if (I().immune(state, effectId)) return null;
    if (effectId === POISONED && state.timed_effects.some((effect) => effect.effect_id === POISONED)) return POISONED;
    const delayRounds = options.repeatSaveDelayRounds || 0;
    if (!Number.isInteger(delayRounds) || delayRounds < 0) throw new Error("Repeat-save delay must be a nonnegative integer.");
    if (delayRounds && options.appliedRound == null) throw new Error("Delayed repeat saves require the application round.");
    const sourceEffectId = options.sourceEffectId || null;
    state.timed_effects = state.timed_effects.filter((effect) => !(
      effect.effect_id === effectId && effect.source_id === sourceId && (effect.source_effect_id || null) === sourceEffectId
    ));
    const expiryTiming = options.expiryTiming || (options.expiresAtStartOfSourceTurn ? "source_turn_start" : null);
    const hasRepeatSave = options.repeatSaveAbility != null && options.repeatSaveDc != null && options.repeatSaveTiming != null;
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: sourceEffectId,
      applied_round: options.appliedRound || null,
      expires_round: options.expiresRound || null,
      expires_at_start_of_source_turn: expiryTiming === "source_turn_start",
      expiry_timing: expiryTiming,
      repeat_save_ability: options.repeatSaveAbility || null,
      repeat_save_dc: options.repeatSaveDc || null,
      repeat_save_timing: options.repeatSaveTiming || null,
      repeat_save_eligible_round: hasRepeatSave && options.appliedRound != null ? options.appliedRound + delayRounds : null,
      allowed_removal_action_ids: [...(options.allowedRemovalActionIds || [])],
      turn_behavior: options.turnBehavior || "normal",
      action_or_bonus_only: Boolean(options.actionOrBonusOnly),
      reactions_disabled: Boolean(options.reactionsDisabled),
      speed_multiplier: options.speedMultiplier == null ? 1 : options.speedMultiplier,
      requires_active_effect_id: options.requiresActiveEffectId || null,
      ends_on_damage: Boolean(options.endsOnDamage),
      ends_if_source_incapacitated: Boolean(options.endsIfSourceIncapacitated),
      ends_if_source_dead: Boolean(options.endsIfSourceDead),
      d20_disadvantage_ability: options.d20DisadvantageAbility || null,
      damage_penalty_dice_count: options.damagePenaltyDiceCount || 0,
      damage_penalty_dice_size: options.damagePenaltyDiceSize || 6,
      automatic_success_round: options.automaticSuccessRound || null,
    });
    if (options.trackActiveEffect !== false && !state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  }

  function applyPenalty(state, sourceId, sourceEffectId, round, effect) {
    const autoAfter = effect.automaticSuccessAfterRounds;
    return apply(state, TIMED_PENALTY, sourceId, {
      sourceEffectId, appliedRound: round, trackActiveEffect: false,
      repeatSaveAbility: effect.repeatSaveAbility, repeatSaveDc: effect.repeatSaveDc,
      repeatSaveTiming: effect.repeatSaveTiming,
      d20DisadvantageAbility: effect.d20DisadvantageAbility,
      damagePenaltyDiceCount: effect.damagePenaltyDiceCount || 0,
      damagePenaltyDiceSize: effect.damagePenaltyDiceSize || 6,
      automaticSuccessRound: autoAfter == null ? null : round + autoAfter,
    });
  }

  function d20Disadvantage(state, ability) {
    return state.timed_effects.filter((effect) => effect.d20_disadvantage_ability === ability).length;
  }

  function applyDamageRollPenalty(state, components) {
    const specs = state.timed_effects.filter((effect) => effect.damage_penalty_dice_count > 0);
    for (const component of components) {
      if (!(component.rolls || []).length || component.total <= 0) continue;
      for (const effect of specs) {
        const rolls = window.IRON_PIT_DICE.rollMany(effect.damage_penalty_dice_count, effect.damage_penalty_dice_size);
        const reduction = Math.min(component.total, rolls.reduce((sum, roll) => sum + roll, 0));
        component.total -= reduction; component.modifier -= reduction; component.notation += ` - ${reduction}`;
      }
    }
    return components;
  }

  function affectedByAction(state, actionId) {
    return state.timed_effects.some((effect) => effect.source_effect_id === actionId);
  }

  function removeEffect(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    const stillActive = state.timed_effects.some((item) => item.effect_id === effect.effect_id);
    if (!stillActive) state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
    return !stillActive;
  }

  function removeGroup(state, effect) {
    if (!effect.source_effect_id) return removeEffect(state, effect) ? [effect.effect_id] : [];
    const grouped = state.timed_effects.filter((item) =>
      item.source_id === effect.source_id && item.source_effect_id === effect.source_effect_id,
    );
    const removed = [];
    for (const item of grouped) if (removeEffect(state, item)) removed.push(item.effect_id);
    return removed;
  }

  function expireSourceStart(sequence, round, source, setup) {
    const events = [];
    for (const target of [...setup.heroes, ...setup.monsters]) {
      const expiring = target.state.timed_effects.filter((effect) =>
        effect.source_id === source.combatant_id
        && (effect.expiry_timing === "source_turn_start" || effect.expires_at_start_of_source_turn)
        && (!effect.expires_round || round >= effect.expires_round),
      );
      for (const effect of expiring) {
        if (!target.state.timed_effects.includes(effect)) continue;
        const removed = removeGroup(target.state, effect); if (!removed.length) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${target.state.template.name} is no longer affected by ${effect.source_effect_id || effect.effect_id}.`,
        });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_TIMED = {
    affectedByAction, apply, applyDamageRollPenalty, applyPenalty, d20Disadvantage,
    expireSourceStart, removeEffect, removeGroup,
  };
})();