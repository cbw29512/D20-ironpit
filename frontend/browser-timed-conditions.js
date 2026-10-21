(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const C = () => window.IRON_PIT_BROWSER_DEBUFF_COUNTERS || { movementCost: () => null };
  const RF = () => window.IRON_PIT_BROWSER_REPLACEMENT_FORMS;
  const T = () => window.IRON_PIT_BROWSER_TERMINAL_EFFECTS;
  const POISONED = "poisoned";
  const TERMINAL = new Set(["petrified"]);
  const POISON_RECOVERY_DC = 10;

  function applyTerminalOutcome(state, effectId, affectedStates = []) {
    if (!TERMINAL.has(effectId) || state.is_dead) return false;
    if (!T()?.applyTerminalDeath) throw new Error("Browser terminal-effect runtime is not loaded.");
    return T().applyTerminalDeath(state, affectedStates) === "dead";
  }

  function apply(state, effectId, sourceId, options = {}) {
    if (I().immune(state, effectId, options.sourceTemplate || null, {
      sourceIsMagical: options.sourceIsMagical === true,
      groundContact: options.groundContact === true,
      actor: options.targetActor || null, setup: options.setup || null,
    })) return null;
    const defaultPoison = effectId === POISONED && options.useDefaultPoisonRecovery !== false
      && !options.expiryTiming && !options.expiresAtStartOfSourceTurn;
    if (defaultPoison && state.timed_effects.some((effect) => effect.effect_id === POISONED)) return POISONED;
    const sourceEffectId = options.sourceEffectId || null;
    state.timed_effects = state.timed_effects.filter((effect) => !(
      effect.effect_id === effectId && effect.source_id === sourceId && (effect.source_effect_id || null) === sourceEffectId
    ));
    const expiryTiming = defaultPoison ? null : (options.expiryTiming || (options.expiresAtStartOfSourceTurn ? "source_turn_start" : null));
    state.timed_effects.push({
      effect_id: effectId,
      source_id: sourceId,
      source_effect_id: sourceEffectId,
      applied_round: options.appliedRound ?? null,
      expires_round: options.expiresRound ?? null,
      expires_target_turn_count: options.expiresTargetTurnCount ?? null,
      expires_at_start_of_source_turn: defaultPoison ? false : expiryTiming === "source_turn_start",
      expiry_timing: expiryTiming,
      repeat_save_ability: defaultPoison ? (options.repeatSaveAbility || "constitution") : (options.repeatSaveAbility || null),
      repeat_save_dc: defaultPoison ? (options.repeatSaveDc || POISON_RECOVERY_DC) : (options.repeatSaveDc || null),
      repeat_save_timing: defaultPoison ? "target_turn_start" : (options.repeatSaveTiming || null),
      damage_repeat_save_trigger: options.damageRepeatSaveTrigger || "none",
      repeat_save_before_damaging_terrain: Boolean(options.repeatSaveBeforeDamagingTerrain),
      source_maintenance_action_cost: options.sourceMaintenanceActionCost || "none",
      source_turn_count_at_application: options.sourceTurnCountAtApplication ?? null,
      exclusive_source_effect_group_id: options.exclusiveSourceEffectGroupId || null,
      repeat_save_disadvantage_while_source_visible: Boolean(options.repeatSaveDisadvantageWhileSourceVisible),
      allowed_removal_action_ids: [...(options.allowedRemovalActionIds || [])],
      turn_behavior: options.turnBehavior || "normal",
      suppress_action: Boolean(options.suppressAction),
      suppress_bonus_action: Boolean(options.suppressBonusAction),
      suppress_reactions: Boolean(options.suppressReactions),
      suppress_movement: Boolean(options.suppressMovement),
      cannot_regain_hit_points: Boolean(options.cannotRegainHitPoints),
      ends_on_magical_healing: Boolean(options.endsOnMagicalHealing),
      next_attack_disadvantage: Boolean(options.nextAttackDisadvantage),
      ends_on_damage: Boolean(options.endsOnDamage),
      ends_on_owner_attack: Boolean(options.endsOnOwnerAttack),
      ends_on_owner_spell_cast: Boolean(options.endsOnOwnerSpellCast),
      ends_if_source_incapacitated: Boolean(options.endsIfSourceIncapacitated),
      ends_if_source_dead: Boolean(options.endsIfSourceDead),
      source_is_magical: Boolean(options.sourceIsMagical),
      repeat_save_context: options.repeatSaveContext ? structuredClone(options.repeatSaveContext) : null,
      owned_damage_resistances: [...(options.ownedDamageResistances || [])],
      owned_debuff_counters: [...(options.ownedDebuffCounters || [])],
      owned_movement_mode_grants: [...(options.ownedMovementModeGrants || [])],
      removed_from_battlefield: Boolean(options.removedFromBattlefield),
      start_of_turn_hp_loss_dice_count: options.startOfTurnHpLossDiceCount || 0,
      start_of_turn_hp_loss_dice_size: options.startOfTurnHpLossDiceSize || 10,
      return_damage_dice_count: options.returnDamageDiceCount || 0,
      return_damage_dice_size: options.returnDamageDiceSize || 0,
      return_damage_bonus: options.returnDamageBonus || 0,
      return_damage_type: options.returnDamageType || null,
      return_damage_excluded_creature_types: [...(options.returnDamageExcludedCreatureTypes || [])],
      repeat_save_failure_count: 0,
      repeat_save_failures_to_lock: options.repeatSaveFailuresToLock || null,
      repeat_save_failure_condition_id: options.repeatSaveFailureConditionId || null,
      escape_check_ability: options.escapeCheckAbility || null,
      escape_check_dc: options.escapeCheckDc ?? null,
      ground_contact: Boolean(options.groundContact),
      ends_on_teleport: Boolean(options.endsOnTeleport || options.groundContact),
      source_effect_immunity_on_end: Boolean(options.sourceEffectImmunityOnEnd),
      control_limits: options.controlLimits || null,
    });
    if (!state.active_effect_ids.includes(effectId)) state.active_effect_ids.push(effectId);
    if (effectId === "unconscious" && !state.active_effect_ids.includes("prone") && !I().immune(state, "prone")) state.active_effect_ids.push("prone");
    applyTerminalOutcome(state, effectId, options.affectedStates || []);
    RF()?.revertIfIncapacitated(state);
    return effectId;
  }

  const committedActivity = (state) => Boolean((state.delayed_resource_refills || []).length);
  const suppressesAction = (state) => committedActivity(state) || (state.timed_effects || []).some((effect) => effect.suppress_action);
  const suppressesBonusAction = (state) => committedActivity(state) || (state.timed_effects || []).some((effect) => effect.suppress_bonus_action);
  const suppressesReactions = (state) => (state.timed_effects || []).some((effect) => effect.suppress_reactions);
  const suppressesMovement = (state) => committedActivity(state) || (state.timed_effects || []).some((effect) => effect.suppress_movement);
  const nextAttackDisadvantage = (state) => (state.timed_effects || []).filter((effect) => effect.next_attack_disadvantage).length;
  function consumeNextAttackDisadvantage(state) {
    let consumed = 0;
    for (const effect of [...(state.timed_effects || [])]) {
      if (!effect.next_attack_disadvantage || !state.timed_effects.includes(effect)) continue;
      if (removeGroup(state, effect).length) consumed += 1;
    }
    return consumed;
  }
  const suppressesVoluntaryTurn = (state) => suppressesAction(state) && suppressesBonusAction(state) && suppressesMovement(state);

  function removeEffect(state, effect) {
    state.timed_effects = state.timed_effects.filter((item) => item !== effect);
    const stillActive = state.timed_effects.some((item) => item.effect_id === effect.effect_id);
    const innate = (state.template?.innate_condition_ids || []).includes(effect.effect_id);
    if (!stillActive && !innate) state.active_effect_ids = state.active_effect_ids.filter((id) => id !== effect.effect_id);
    return !stillActive && !innate;
  }

  function removeGroup(state, effect, options = {}) {
    const grantImmunity = options.grantSourceImmunity == null
      ? Boolean(effect.source_effect_immunity_on_end)
      : Boolean(options.grantSourceImmunity);
    const actionId = effect.source_effect_id;
    const sourceId = effect.source_id;
    const round = state.current_round || 1;
    const sourceIsMagical = Boolean(effect.source_is_magical);
    if (!effect.source_effect_id) return removeEffect(state, effect) ? [effect.effect_id] : [];
    const grouped = state.timed_effects.filter((item) =>
      item.source_id === effect.source_id && item.source_effect_id === effect.source_effect_id,
    );
    const removed = [];
    for (const item of grouped) if (removeEffect(state, item)) removed.push(item.effect_id);
    state.active_modifiers = (state.active_modifiers || []).filter((item) => !(
      item.source_id === effect.source_id && item.source_effect_id === effect.source_effect_id
    ));
    if (removed.length && grantImmunity && actionId && !String(actionId).includes(":success-immunity")) {
      window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS?.grantImmunity(state, actionId, sourceId, round, { sourceIsMagical });
    }
    return removed;
  }

  function expireOnOwnerEvent(state, event, affectedStates = []) {
    try {
      if (!["attack", "spell_cast"].includes(event)) throw new Error(`Unknown owner expiry event: ${event}.`);
      const flag = event === "attack" ? "ends_on_owner_attack" : "ends_on_owner_spell_cast";
      const removed = [];
      for (const effect of [...(state.timed_effects || [])]) {
        if (!(state.timed_effects || []).includes(effect) || !effect[flag]) continue;
        const concentration = state.concentration;
        let ids;
        if (concentration && concentration.effect_id === effect.source_effect_id
          && concentration.source_id === effect.source_id) {
          ids = state.timed_effects.filter((item) => item.source_id === concentration.source_id
            && item.source_effect_id === concentration.effect_id).map((item) => item.effect_id);
          if (!window.IRON_PIT_BROWSER_CONCENTRATION?.end) {
            throw new Error("Owner expiry requires the concentration engine.");
          }
          window.IRON_PIT_BROWSER_CONCENTRATION.end(state, affectedStates);
        } else {
          ids = removeGroup(state, effect);
        }
        for (const id of ids) if (!removed.includes(id)) removed.push(id);
      }
      return removed;
    } catch (error) {
      console.error("Owner action timed-effect expiry failed.", { event, error });
      throw error;
    }
  }

  function removeOnMagicalHealing(state) {
    try {
      const removed = [];
      for (const effect of [...(state.timed_effects || [])]) {
        if (!effect.ends_on_magical_healing) continue;
        if (removeEffect(state, effect) && !removed.includes(effect.effect_id)) removed.push(effect.effect_id);
      }
      return removed;
    } catch (error) {
      console.error("Timed effect magical-healing cleanup failed", { error });
      throw error;
    }
  }

  function resolveMovementCounters(state) {
    const resolved = [
      ...(window.IRON_PIT_BROWSER_FLIGHT_GROUND?.resolveGroundConditions(state) || []),
    ];
    for (const effect of [...(state.timed_effects || [])]) {
      const cost = C().movementCost(state, effect.effect_id, { sourceIsMagical: Boolean(effect.source_is_magical) });
      if (cost == null || state.movement_remaining_ft < cost) continue;
      const removed = removeGroup(state, effect);
      if (!removed.length) continue;
      state.movement_remaining_ft -= cost;
      for (const debuffId of removed) resolved.push({ debuffId, sourceId: effect.source_id, movementCost: cost });
    }
    return resolved;
  }

  function ownsDamageResistance(state, damageType) {
    try {
      return (state.timed_effects || []).some((effect) =>
        (effect.owned_damage_resistances || []).includes(damageType),
      );
    } catch (error) {
      console.error("Timed resistance lookup failed.", error);
      throw error;
    }
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
    apply, applyTerminalOutcome, expireOnOwnerEvent, consumeNextAttackDisadvantage, expireSourceStart, nextAttackDisadvantage, ownsDamageResistance,
    removeEffect, removeGroup, removeOnMagicalHealing, resolveMovementCounters, suppressesAction, suppressesBonusAction,
    suppressesMovement, suppressesReactions, suppressesVoluntaryTurn,
  };
})();