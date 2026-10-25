(() => {
  "use strict";

  function apply(actor, target, action, save, round, options = {}) {
    try {
      const rider = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
      const shared = window.IRON_PIT_BROWSER_SAVE_IMMUNITY;
      let appliedConditions = [];
      if (save.succeeded && action.sourceEffectImmunityOnSuccess) {
        if (!rider?.grantImmunity) {
          throw new Error("Source save-immunity runtime is unavailable.");
        }
        rider.grantImmunity(
          target.state, action.id, actor.combatant_id, round, {
            sourceTemplate: actor.state.template,
            sourceIsMagical: Boolean(action.magicalEffect),
          },
        );
      }
      if (save.succeeded
        && (action.sourceEffectImmunityKeysOnSuccess || []).length) {
        if (!shared?.grantSharedImmunities) {
          throw new Error("Shared save-immunity grant runtime is unavailable.");
        }
        shared.grantSharedImmunities(
          target.state,
          action.sourceEffectImmunityKeysOnSuccess,
          actor.combatant_id,
          round,
          {
            sourceTemplate: actor.state.template,
            sourceIsMagical: Boolean(action.magicalEffect),
          },
        );
      }
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && action.failedSaveTimedEffect) {
        if (!rider?.apply) {
          throw new Error("Failed-save timed-effect runtime is unavailable.");
        }
        const applied = rider.apply(
          actor,
          target,
          action,
          action.failedSaveTimedEffect,
          round,
          options.setup || null,
          save.roll?.total ?? null,
        );
        if (Array.isArray(applied)) appliedConditions.push(...applied);
        else if (applied) appliedConditions.push(applied);
      }
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && action.grappleEscapeDc) {
        const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
        if (!grapple?.apply) {
          throw new Error("Save grapple runtime is unavailable.");
        }
        appliedConditions = grapple.apply(
          target.state,
          actor.combatant_id,
          action.grappleEscapeDc,
          action.range,
          Boolean(action.restrainsWhileGrappled),
          Boolean(action.magicalEffect),
        );
      }
      let pushedFt = 0;
      if (!save.succeeded && target.state.is_alive && !target.state.is_dead
        && (action.failedSavePushFt || 0) > 0) {
        const movement = window.IRON_PIT_BROWSER_FORCED_MOVEMENT;
        if (!options.setup || !movement?.pushStraightAway) {
          throw new Error(
            `${action.name} forced movement requires encounter setup.`,
          );
        }
        pushedFt = movement.pushStraightAway(
          target, actor, options.setup, action.failedSavePushFt,
        );
      }
      return { appliedConditions, pushedFt };
    } catch (error) {
      console.error("Browser failed-save effect application failed", {
        actionId: action?.id,
        actor: actor?.combatant_id,
        target: target?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_ACTION_EFFECTS = { apply };
})();
