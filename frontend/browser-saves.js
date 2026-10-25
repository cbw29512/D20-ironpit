(() => {
  "use strict";

  const support = window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT;
  const attempts = window.IRON_PIT_BROWSER_SAVE_ACTION_ATTEMPT;
  const damage = window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY;
  const effects = window.IRON_PIT_BROWSER_SAVE_ACTION_EFFECTS;
  const events = window.IRON_PIT_BROWSER_SAVE_EVENT;
  if (!support?.legalAction || !support?.resolveOnHitConditionSave) {
    throw new Error("Browser save-action support runtime is unavailable.");
  }
  if (!attempts?.resolveAttempt || !damage?.resolveAndApply
    || !effects?.apply || !events?.build) {
    throw new Error("Browser save-action split runtimes are unavailable.");
  }
  function resolveAction(
    sequence, round, actor, target, action, distance, options = {},
  ) {
    try {
      const spendAction = options.spendAction !== false;
      const checkResource = options.checkResource !== false;
      const economy = window.IRON_PIT_ACTION_ECONOMY || {
        available: (state, cost) =>
          cost === "action" && state.action_available,
        spend: (state) => { state.action_available = false; },
      };
      const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES || {
        canSee: () => true,
      };
      if (action.openingInitiativeOnly
        && !window.IRON_PIT_BROWSER_CHARGE?.openingEligible(
          round, actor, options.setup,
        )) {
        throw new Error(
          `${action.name} requires an initiative-winning opening turn.`,
        );
      }
      const actionCost = action.actionCost || "action";
      if (spendAction && !economy.available(actor.state, actionCost)) {
        throw new Error(`${actionCost} is unavailable for ${action.name}.`);
      }
      if (checkResource && action.resourceId
        && (actor.state.resources[action.resourceId] || 0)
          < (action.resourceCost || 1)) {
        throw new Error(`${action.name} resource is unavailable.`);
      }
      if (!support.legalAction(
        action, target, distance, actor.combatant_id, actor,
      )) {
        throw new Error(
          `${action.name} has no legal target at ${distance} feet.`,
        );
      }
      if (action.requiresTargetSight
        && !conditions.canSee(actor.state, target.state, distance)) {
        throw new Error(
          `${action.name} requires the actor to see the target.`,
        );
      }

      const attempt = attempts.resolveAttempt(
        actor, target, action, round, options,
      );
      action = attempt.action;

      let resourceRemaining = options.resourceRemaining ?? null;
      if (action.resourceId && options.spendResource !== false) {
        actor.state.resources[action.resourceId] -= action.resourceCost || 1;
        resourceRemaining = actor.state.resources[action.resourceId];
      }
      if (spendAction) economy.spend(actor.state, actionCost);

      const snapshot = {
        hpBefore: target.state.current_hp,
        temporaryHpBefore: target.state.temporary_hp,
        deathSuccessBefore: target.state.death_save_successes,
        deathFailureBefore: target.state.death_save_failures,
        concentrationBefore: target.state.concentration?.effect_id || null,
        resourceRemaining,
      };
      const damageResult = damage.resolveAndApply(
        target,
        action,
        attempt.save.succeeded,
        {
          sharedDamageRolls: options.sharedDamageRolls,
          setup: options.setup || null,
        },
      );
      const effectResult = effects.apply(
        actor,
        target,
        action,
        attempt.save,
        round,
        { setup: options.setup || null },
      );
      return events.build(
        sequence,
        round,
        actor,
        target,
        action,
        attempt,
        damageResult,
        effectResult,
        snapshot,
      );
    } catch (error) {
      console.error("Browser save-action resolution failed", {
        actionId: action?.id,
        actor: actor?.combatant_id,
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVES = {
    legalAction: support.legalAction,
    resolveAction,
    resolveOnHitConditionSave: support.resolveOnHitConditionSave,
    resolveSavingThrow: support.resolveSavingThrow,
    saveMode: support.saveMode,
  };
})();
