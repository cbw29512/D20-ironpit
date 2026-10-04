(() => {
  "use strict";

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
      });
    } catch (error) {
      console.error("Failed browser failed-save timed rider application", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS = { apply };
})();
