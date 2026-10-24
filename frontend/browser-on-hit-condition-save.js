(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const K = () => window.IRON_PIT_BROWSER_CREATURE_KIND
    || (() => { throw new Error("browser-creature-kind.js is required."); })();

  function resolve(target, attack, sourceTemplate = null, round = null, setup = null, attacker = null) {
    try {
    const effect = attack.onHitConditionSave;
    if (!effect || target.state.is_dead || !target.state.is_alive) return null;
    if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) return null;
    const kinds = [...(effect.excludedCreatureTypes || []), ...(effect.excludedCreatureSubtypes || [])];
    if (kinds.some((kind) => K().matches(target.state.template, kind))) return null;
    if (I().immune(target.state, effect.conditionId, sourceTemplate, { actor: target, setup })) return null;
    const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(target.state, effect.saveAbility, effect.dc, {
      conditionId: effect.conditionId,
      effectTags: effect.conditionId === "poisoned" ? ["poison"] : [],
      roundNumber: round,
      encounterRoller: target,
      setup,
    });
    let appliedCondition = null;
    const additionalConditions = [];
    const escalation = effect.failureMarginEscalation || null;
    const escalated = !save.succeeded && save.roll != null && escalation != null
      && save.roll.total <= effect.dc - escalation.margin;
    let duration = effect.durationRounds ?? null;
    if (escalated && escalation.replacementDurationDiceCount != null) {
      if (!window.IRON_PIT_DICE?.roll) throw new Error("Escalated duration requires the shared dice runtime.");
      duration = Array.from({ length: escalation.replacementDurationDiceCount },
        () => window.IRON_PIT_DICE.roll(escalation.replacementDurationDiceSize))
        .reduce((sum, roll) => sum + roll, 0) * escalation.replacementDurationRoundMultiplier;
    }
    if (escalated && duration == null) throw new Error("Escalated timed conditions require a source-declared duration.");
    if (!save.succeeded) {
      const timed = duration != null || effect.repeatSaveTiming;
      if (timed) {
        if (!T()?.apply) throw new Error("Timed on-hit condition save requires browser-timed-conditions.js.");
        appliedCondition = T().apply(target.state, effect.conditionId, attacker?.combatant_id || sourceTemplate?.id || "on-hit-save", {
          sourceEffectId: attack.name || attack.id,
          sourceTemplate,
          targetActor: target, setup,
          appliedRound: round,
          expiresRound: duration != null && round != null ? round + duration : null,
          expiryTiming: duration != null ? "target_turn_end" : null,
          repeatSaveAbility: effect.repeatSaveTiming ? effect.saveAbility : null,
          repeatSaveDc: effect.repeatSaveTiming ? effect.dc : null,
          repeatSaveTiming: effect.repeatSaveTiming || null,
          repeatSaveFailureConditionId: effect.repeatSaveFailureConditionId || null,
          useDefaultPoisonRecovery: false,
          cannotRegainHitPoints: Boolean(effect.cannotRegainHitPoints),
          startOfTurnDiceCount: effect.startOfTurnDamageDiceCount || 0,
          startOfTurnDiceSize: effect.startOfTurnDamageDiceSize || 6,
          startOfTurnDamageType: effect.startOfTurnDamageType || null,
        }) || null;
      } else if (!target.state.active_effect_ids.includes(effect.conditionId)) {
        target.state.active_effect_ids.push(effect.conditionId);
        T()?.applyTerminalOutcome?.(target.state, effect.conditionId);
        appliedCondition = effect.conditionId;
      }
      if (escalated) {
        if (!T()?.apply) throw new Error("Escalated conditions require browser-timed-conditions.js.");
        for (const conditionId of escalation.additionalConditionIds) {
          const added = T().apply(target.state, conditionId,
            attacker?.combatant_id || sourceTemplate?.id || "on-hit-save", {
              sourceEffectId: (escalation.endsOnDamage || escalation.allowedRemovalActionIds?.length)
                ? `${attack.name || attack.id}:escalated` : (attack.name || attack.id),
              sourceTemplate, targetActor: target, setup,
              appliedRound: round,
              expiresRound: round == null ? null : round + duration,
              expiryTiming: "target_turn_end",
              endsOnDamage: Boolean(escalation.endsOnDamage),
              allowedRemovalActionIds: escalation.allowedRemovalActionIds || [],
              useDefaultPoisonRecovery: false,
            });
          if (added) additionalConditions.push(added);
        }
      }
    }
    let forcedMovementFt = 0;
    if (!save.succeeded && (effect.failurePushFt || 0) > 0) {
      if (!setup || !attacker) throw new Error("Failed-save forced movement requires encounter setup and attacker.");
      forcedMovementFt = window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pushStraightAway(
        target, attacker, setup, effect.failurePushFt,
      );
    }
    return {
      saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc,
      saveSucceeded: save.succeeded, appliedCondition, additionalConditions, forcedMovementFt,
    };
    } catch (error) {
      console.error("On-hit condition save resolution failed", { target: target?.combatant_id, error }); throw error;
    }
  }

  function resolveOngoingHpLoss(target, attack, sourceTemplate = null, round = null, setup = null, attacker = null) {
    try {
      const rule = attack.onHitOngoingHpLoss;
      if (!rule || target.state.is_dead || !target.state.is_alive) return null;
      const exclusions = rule.excludedCreatureTypes || [];
      if (exclusions.some((kind) => K().matches(target.state.template, kind))) return null;
      const sourceId = attacker?.combatant_id;
      if (!sourceId) throw new Error("Source-owned persistent HP loss requires a combatant source id.");
      const H = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
      if (!H?.applyOrStackHpLoss) throw new Error("Universal source-owned HP-loss runtime is required.");
      const sourceEffectId = rule.sourceName;
      const existing = (target.state.timed_effects || []).find((effect) =>
        effect.effect_id === rule.effectId && effect.source_id === sourceId
        && effect.source_effect_id === sourceEffectId);
      if (existing) {
        if (!rule.stacksOnReapply) return null;
        H.applyOrStackHpLoss(target.state, rule.effectId, sourceId, sourceEffectId,
          rule.diceCount, rule.diceSize, Boolean(rule.endsOnMagicalHealing));
        return { saveRoll: null, saveAbility: null, saveDc: null,
          saveSucceeded: null, appliedCondition: rule.effectId };
      }
      const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
        target.state, rule.saveAbility, rule.dc, {
          roundNumber: round, encounterRoller: target, setup,
        },
      );
      let appliedCondition = null;
      if (!save.succeeded) {
        H.applyOrStackHpLoss(target.state, rule.effectId, sourceId, sourceEffectId,
          rule.diceCount, rule.diceSize, Boolean(rule.endsOnMagicalHealing));
        appliedCondition = rule.effectId;
      }
      return {
        saveRoll: save.roll, saveAbility: rule.saveAbility, saveDc: rule.dc,
        saveSucceeded: save.succeeded, appliedCondition,
      };
    } catch (error) {
      console.error("On-hit persistent HP loss failed", { target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE = { resolve, resolveOngoingHpLoss, creatureMatchesKind: K().matches };
})();
