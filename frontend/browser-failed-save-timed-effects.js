(() => {
  "use strict";

  function immunityId(actionId, sourceId) {
    return `${actionId}:success-immunity:${sourceId}`;
  }

  function isImmune(target, action, sourceId) {
    try {
      const id = immunityId(action.id, sourceId);
      return (target.state.timed_effects || []).some((effect) => effect.effect_id === id);
    } catch (error) {
      console.error("Failed source-effect immunity lookup", { actionId: action?.id, sourceId, error });
      throw error;
    }
  }

  function grantImmunity(state, actionId, sourceId, round, options = {}) {
    try {
      const id = immunityId(actionId, sourceId);
      if ((state.timed_effects || []).some((effect) => effect.effect_id === id)) return id;
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) throw new Error("Source-effect immunity requires browser-timed-conditions.js.");
      return timed.apply(state, id, sourceId, {
        sourceEffectId: `${actionId}:success-immunity`,
        sourceTemplate: options.sourceTemplate || null,
        sourceIsMagical: Boolean(options.sourceIsMagical),
        appliedRound: round,
        expiresRound: null,
        expiryTiming: null,
        expiresAtStartOfSourceTurn: false,
        useDefaultPoisonRecovery: false,
      });
    } catch (error) {
      console.error("Failed source-effect immunity grant", { actionId, sourceId, error });
      throw error;
    }
  }

  function controlLimitsFrom(rider) {
    if (rider.controlLimits) return rider.controlLimits;
    const abilities = [...(rider.d20DisadvantageAbilities || [])];
    if (rider.disadvantageStrengthD20Tests && !abilities.includes("strength")) abilities.push("strength");
    const speed = rider.speedMultiplier == null ? 1 : rider.speedMultiplier;
    const acBonus = rider.armorClassBonus || 0;
    const saveFlats = [...(rider.savingThrowFlatBonuses || [])];
    if (speed === 1 && !rider.actionBonusExclusive && rider.maxAttacksPerTurn == null && !abilities.length && !acBonus && !saveFlats.length) {
      return null;
    }
    return {
      speed_multiplier: speed,
      action_bonus_exclusive: Boolean(rider.actionBonusExclusive),
      max_attacks_per_turn: rider.maxAttacksPerTurn ?? null,
      d20_disadvantage_abilities: abilities,
      armor_class_bonus: acBonus,
      saving_throw_flat_bonuses: saveFlats,
    };
  }

  function apply(actor, target, action, rider, round, setup = null) {
    try {
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) throw new Error("Failed-save timed effect requires browser-timed-conditions.js.");
      const applied = [];
      const effectIds = [rider.effectId, ...(rider.additionalEffectIds || [])];
      for (const [index, effectId] of effectIds.entries()) {
        if (index && !applied.length) break;
        const ownsLifecycle = index === 0;
        const groundContact = ownsLifecycle && Boolean(rider.groundContact || (
          (action.createsDifficultTerrain || action.creates_difficult_terrain)
          && effectId === "restrained"
        ));
        const result = timed.apply(target.state, effectId, actor.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: actor.state.template,
          targetActor: target, setup,
          sourceIsMagical: Boolean(action.magicalEffect),
          appliedRound: round,
          expiresRound: ownsLifecycle && rider.durationRounds != null
            ? round + rider.durationRounds : null,
          expiryTiming: ownsLifecycle ? (rider.expiryTiming || "target_turn_end") : null,
          repeatSaveAbility: ownsLifecycle ? (rider.repeatSaveAbility || null) : null,
          repeatSaveDc: ownsLifecycle ? (rider.repeatSaveDc ?? null) : null,
          repeatSaveTiming: ownsLifecycle ? (rider.repeatSaveTiming || null) : null,
          repeatSaveDisadvantageWhileSourceVisible: ownsLifecycle
            && Boolean(rider.repeatSaveDisadvantageWhileSourceVisible),
          repeatSaveFailureConditionId: ownsLifecycle
            ? (rider.repeatSaveFailureConditionId || null) : null,
          allowedRemovalActionIds: ownsLifecycle ? [...(rider.allowedRemovalActionIds || [])] : [],
          turnBehavior: ownsLifecycle ? (rider.turnBehavior || "normal") : "normal",
          endsOnDamage: ownsLifecycle && Boolean(rider.endsOnDamage),
          endsIfSourceIncapacitated: ownsLifecycle && Boolean(rider.endsIfSourceIncapacitated),
          endsIfSourceDead: ownsLifecycle && Boolean(rider.endsIfSourceDead),
          nextAttackDisadvantage: ownsLifecycle && Boolean(rider.nextAttackDisadvantage),
          suppressReactions: ownsLifecycle && Boolean(rider.blocksReactions),
          controlLimits: ownsLifecycle ? controlLimitsFrom(rider) : null,
          useDefaultPoisonRecovery: false,
          repeatSaveFailuresToLock: ownsLifecycle ? (rider.repeatSaveFailuresToLock || null) : null,
          escapeCheckAbility: ownsLifecycle ? (rider.escapeCheckAbility || null) : null,
          escapeCheckDc: ownsLifecycle ? (rider.escapeCheckDc ?? null) : null,
          groundContact,
          endsOnTeleport: ownsLifecycle && Boolean(rider.endsOnTeleport || groundContact),
          sourceEffectImmunityOnEnd: ownsLifecycle && Boolean(rider.sourceEffectImmunityOnEnd),
        });
        if (result) applied.push(result);
      }
      return applied;
    } catch (error) {
      console.error("Failed browser failed-save timed rider application", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = { apply, isImmune, grantImmunity, immunityId };
})();
