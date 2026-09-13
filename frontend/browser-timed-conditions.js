(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const POISONED = "poisoned";
  const POISON_RECOVERY_DC = 10;

  function apply(state, effectId, sourceId, options = {}) {
    if (I().immune(state, effectId)) return null;
    const arenaPoison = effectId === POISONED && state.template.ruleset !== "2014";
    if (arenaPoison && state.timed_effects.some((effect) => effect.effect_id === POISONED)) return POISONED;
    const sourceEffectId = options.sourceEffectId || null;
    state.timed_effects = state.timed_effects.filter((effect) => !(
      effect.effect_id === effectId && effect.source_id === sourceId && (effect.source_effect_id || null) === sourceEffectId
    ));
    const expiryTiming = arenaPoison ? null : (options.expiryTiming || (options.expiresAtStartOfSourceTurn ? "source_turn_start" : null));
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: sourceEffectId,
      applied_round: options.appliedRound || null,
      expires_round: options.expiresRound || null,
      expires_at_start_of_source_turn: arenaPoison ? false : expiryTiming === "source_turn_start",
      expiry_timing: expiryTiming,
      repeat_save_ability: arenaPoison ? (options.repeatSaveAbility || "constitution") : (options.repeatSaveAbility || null),
      repeat_save_dc: arenaPoison ? (options.repeatSaveDc || POISON_RECOVERY_DC) : (options.repeatSaveDc || null),
      repeat_save_timing: arenaPoison ? (options.repeatSaveTiming || "target_turn_start") : (options.repeatSaveTiming || null),
      allowed_removal_action_ids: [...(options.allowedRemovalActionIds || [])],
      turn_behavior: options.turnBehavior || "normal",
      ends_on_damage: Boolean(options.endsOnDamage),
      ends_if_source_incapacitated: Boolean(options.endsIfSourceIncapacitated),
      ends_if_source_dead: Boolean(options.endsIfSourceDead),
      source_effect_immunity_on_end: Boolean(options.sourceEffectImmunityOnEnd),
      speed_multiplier: options.speedMultiplier ?? 1,
      blocks_reactions: Boolean(options.blocksReactions),
      action_bonus_exclusive: Boolean(options.actionBonusExclusive),
      max_attacks_per_turn: options.maxAttacksPerTurn ?? null,
      disadvantage_strength_d20_tests: Boolean(options.disadvantageStrengthD20Tests),
    });
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    return effectId;
  }

  function strengthD20Disadvantage(state) {
    return (state.timed_effects || []).some((effect) => effect.disadvantage_strength_d20_tests) ? 1 : 0;
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

  window.IRON_PIT_BROWSER_TIMED = { apply, expireSourceStart, removeEffect, removeGroup, strengthD20Disadvantage };
})();