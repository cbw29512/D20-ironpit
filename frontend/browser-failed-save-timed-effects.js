(() => {
  "use strict";

  const IMMUNITY_ROUNDS_24H = 14400;

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
      const rounds = options.rounds ?? IMMUNITY_ROUNDS_24H;
      if (!rounds) return null;
      const id = immunityId(actionId, sourceId);
      if ((state.timed_effects || []).some((effect) => effect.effect_id === id)) return id;
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed) throw new Error("Source-effect immunity requires browser-timed-conditions.js.");
      return timed.apply(state, id, sourceId, {
        sourceEffectId: `${actionId}:success-immunity`,
        sourceTemplate: options.sourceTemplate || null,
        sourceIsMagical: Boolean(options.sourceIsMagical),
        appliedRound: round,
        expiresRound: round + rounds,
        expiryTiming: "source_turn_start",
        expiresAtStartOfSourceTurn: true,
        useDefaultPoisonRecovery: false,
      });
    } catch (error) {
      console.error("Failed source-effect immunity grant", { actionId, sourceId, error });
      throw error;
    }
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
        nextAttackDisadvantage: Boolean(rider.nextAttackDisadvantage),
        useDefaultPoisonRecovery: false,
        repeatSaveFailuresToLock: rider.repeatSaveFailuresToLock || null,
        escapeCheckAbility: rider.escapeCheckAbility || null,
        escapeCheckDc: rider.escapeCheckDc ?? null,
        groundContact: Boolean(rider.groundContact || (
          (action.createsDifficultTerrain || action.creates_difficult_terrain)
          && rider.effectId === "restrained"
        )),
        endsOnTeleport: Boolean(rider.endsOnTeleport || rider.groundContact),
        sourceEffectImmunityRounds: rider.sourceEffectImmunityOnEnd ? IMMUNITY_ROUNDS_24H : 0,
      });
    } catch (error) {
      console.error("Failed browser failed-save timed rider application", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = {
    apply, isImmune, grantImmunity, immunityId, IMMUNITY_ROUNDS_24H,
  };
})();
