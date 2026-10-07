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

  function apply(actor, target, action, rider, round) {
    try {
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) throw new Error("Failed-save timed effect requires browser-timed-conditions.js.");
      return timed.apply(target.state, rider.effectId, actor.combatant_id, {
        sourceEffectId: action.id,
        sourceTemplate: actor.state.template,
        sourceIsMagical: Boolean(action.magicalEffect),
        appliedRound: round,
        expiresRound: rider.durationRounds != null ? round + rider.durationRounds : null,
        expiryTiming: rider.expiryTiming || "target_turn_end",
        repeatSaveAbility: rider.repeatSaveAbility || null,
        repeatSaveDc: rider.repeatSaveDc ?? null,
        repeatSaveTiming: rider.repeatSaveTiming || null,
        turnBehavior: rider.turnBehavior || "normal",
        endsOnDamage: Boolean(rider.endsOnDamage),
        endsIfSourceIncapacitated: Boolean(rider.endsIfSourceIncapacitated),
        endsIfSourceDead: Boolean(rider.endsIfSourceDead),
        allowedRemovalActionIds: [...(rider.allowedRemovalActionIds || [])],
        nextAttackDisadvantage: Boolean(rider.nextAttackDisadvantage),
        suppressReactions: Boolean(rider.blocksReactions),
        controlLimits: controlLimitsFrom(rider),
        useDefaultPoisonRecovery: false,
        repeatSaveFailuresToLock: rider.repeatSaveFailuresToLock || null,
        escapeCheckAbility: rider.escapeCheckAbility || null,
        escapeCheckDc: rider.escapeCheckDc ?? null,
        groundContact: Boolean(rider.groundContact || (
          (action.createsDifficultTerrain || action.creates_difficult_terrain)
          && rider.effectId === "restrained"
        )),
        endsOnTeleport: Boolean(rider.endsOnTeleport || rider.groundContact),
        sourceEffectImmunityOnEnd: Boolean(rider.sourceEffectImmunityOnEnd),
      });
    } catch (error) {
      console.error("Failed browser failed-save timed rider application", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = { apply, isImmune, grantImmunity, immunityId };
})();
