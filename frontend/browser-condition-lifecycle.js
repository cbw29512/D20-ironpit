(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  const label = (id) => id.replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase());
  function repeatSaveDue(effect, round, timing) {
    if (effect.repeat_save_timing !== timing) return false;
    return effect.repeat_save_eligible_round == null || round >= effect.repeat_save_eligible_round;
  }
  const autoSuccessDue = (effect, round, timing) => effect.automatic_success_round != null
    && round >= effect.automatic_success_round && effect.repeat_save_timing === timing;
  const expiryDue = (effect, round, timing) => effect.expiry_timing === timing
    && (effect.expires_round == null || round >= effect.expires_round);

  function periodicDamage(sequence, round, target, effect, timing) {
    if (effect.periodic_damage_timing !== timing) return null;
    if (!effect.periodic_damage_type || !effect.periodic_damage_dice_count) throw new Error("Periodic damage state is incomplete.");
    const rolls = D().rollMany(effect.periodic_damage_dice_count, effect.periodic_damage_dice_size);
    const raw = Math.max(0, rolls.reduce((sum, value) => sum + value, 0) + (effect.periodic_damage_bonus || 0));
    const applied = A().adjustedDamage(target.state, raw, effect.periodic_damage_type), before = target.state.current_hp;
    if (applied) A().applyDamage(target.state, applied, false, [effect.periodic_damage_type]);
    return {
      sequence, round_number: round, event_type: "feature", actor_id: target.combatant_id,
      actor_name: target.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      damage_roll: { notation: `${effect.periodic_damage_dice_count}d${effect.periodic_damage_dice_size}+${effect.periodic_damage_bonus || 0}`, rolls,
        modifier: effect.periodic_damage_bonus || 0, total: applied },
      damage_components: [{ source: effect.source_effect_id || effect.effect_id, damage_type: effect.periodic_damage_type,
        rolls, modifier: effect.periodic_damage_bonus || 0, total: raw, applied_total: applied }],
      hp_before: before, hp_after: target.state.current_hp, feature_id: effect.source_effect_id || "periodic-damage",
      animation: "damage", description: `${target.state.template.name} takes ${applied} ${effect.periodic_damage_type} damage from ${effect.source_effect_id || effect.effect_id}.`,
    };
  }

  function transition(target, effect, save, round) {
    if (save.succeeded) return { removed: T().removeGroup(target.state, effect), applied: [] };
    if (!effect.repeat_save_failure_condition) return { removed: [], applied: [] };
    const removed = T().removeGroup(target.state, effect);
    const continues = effect.repeat_save_failure_continues !== false;
    const duration = effect.repeat_save_failure_duration_rounds;
    const next = T().apply(target.state, effect.repeat_save_failure_condition, effect.source_id, {
      sourceEffectId: effect.source_effect_id || null,
      appliedRound: round,
      expiresRound: duration == null ? null : round + duration,
      expiryTiming: duration == null ? null : "target_turn_end",
      repeatSaveAbility: continues ? effect.repeat_save_ability : null,
      repeatSaveDc: continues ? effect.repeat_save_dc : null,
      repeatSaveTiming: continues ? effect.repeat_save_timing : null,
      automaticSuccessRound: continues ? (effect.automatic_success_round || null) : null,
      allowedRemovalActionIds: effect.repeat_save_failure_allowed_removal_action_ids?.length
        ? [...effect.repeat_save_failure_allowed_removal_action_ids]
        : [...(effect.allowed_removal_action_ids || [])],
      endsOnDamage: Boolean(effect.repeat_save_failure_ends_on_damage || effect.ends_on_damage),
      endsIfSourceIncapacitated: Boolean(effect.ends_if_source_incapacitated),
      endsIfSourceDead: Boolean(effect.ends_if_source_dead),
    });
    return { removed, applied: next ? [next] : [] };
  }

  function resolveTargetTiming(sequence, round, target, timing) {
    const events = [];
    for (const effect of [...target.state.timed_effects]) {
      if (!target.state.timed_effects.includes(effect)) continue;
      const damage = periodicDamage(sequence, round, target, effect, timing);
      if (damage) { events.push(damage); sequence += 1; if (target.state.is_dead) continue; }
      if (autoSuccessDue(effect, round, timing)) {
        const removed = T().removeGroup(target.state, effect);
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: null, save_ability: effect.repeat_save_ability,
          save_dc: effect.repeat_save_dc, save_succeeded: true, removed_condition_ids: removed,
          feature_id: effect.source_effect_id || "timed-effect-auto-success", animation: "condition-save",
          description: `${target.state.template.name} automatically succeeds against ${label(effect.source_effect_id || effect.effect_id)} when its maximum duration ends.`,
        });
        continue;
      }
      if (repeatSaveDue(effect, round, timing)) {
        const save = V().resolveSavingThrow(target.state, effect.repeat_save_ability, effect.repeat_save_dc);
        const result = transition(target, effect, save, round);
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: effect.repeat_save_ability,
          save_dc: effect.repeat_save_dc, save_succeeded: save.succeeded,
          applied_condition_ids: result.applied, removed_condition_ids: result.removed,
          feature_id: effect.source_effect_id || "condition-repeat-save", animation: "condition-save",
          description: `${target.state.template.name} repeats the ${effect.repeat_save_ability} save against ${label(effect.source_effect_id || effect.effect_id)}: ${save.succeeded ? "SUCCESS" : "FAILURE"}.`,
        });
        if (save.succeeded || result.applied.length) continue;
      }
      if (expiryDue(effect, round, timing)) {
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: target.combatant_id, actor_name: target.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.`,
        });
      }
    }
    if (timing === "target_turn_end") M()?.expireTargetTurn(target.state);
    return { events, sequence };
  }

  function resolveSourceTiming(sequence, round, source, setup, timing) {
    const events = [];
    for (const target of [...setup.heroes, ...setup.monsters]) {
      const expiring = target.state.timed_effects.filter((effect) =>
        effect.source_id === source.combatant_id && expiryDue(effect, round, timing),
      );
      for (const effect of expiring) {
        if (!target.state.timed_effects.includes(effect)) continue;
        const removed = T().removeGroup(target.state, effect); if (!removed.length) continue;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          removed_condition_ids: removed, feature_id: effect.source_effect_id || "condition-ended",
          animation: "condition-ended", description: `${label(effect.source_effect_id || effect.effect_id)} ends on ${target.state.template.name}.`,
        });
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_CONDITION_LIFECYCLE = { resolveSourceTiming, resolveTargetTiming };
})();