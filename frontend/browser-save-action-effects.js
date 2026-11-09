(() => {
  "use strict";

  function saveGrappleAllowed(actor, target, action, setup) {
    try {
      const sizes = window.IRON_PIT_BROWSER_STATE;
      if (action.grappleMaxTargetSize) {
        if (!sizes?.sizeAtMost) throw new Error("Universal size gate is unavailable.");
        if (!sizes.sizeAtMost(target, action.grappleMaxTargetSize)) return false;
      }
      if (action.grappleMaxActiveGrapples == null) return true;
      if (!setup) throw new Error("Capacity-limited save Grapple requires encounter setup.");
      const cost = (member) => (
        ["large", "huge", "gargantuan"].includes(member.state.template.size)
          ? (action.grappleLargeTargetSlotCost || 1) : 1
      );
      let occupied = 0;
      for (const member of [...setup.heroes, ...setup.monsters]) {
        if (member.combatant_id === actor.combatant_id
          || !member.state.is_alive || member.state.is_dead) continue;
        const held = (member.state.grapple_sources || []).some(
          (source) => source.source_id === actor.combatant_id,
        );
        if (!held) continue;
        if (member.combatant_id === target.combatant_id) return false;
        occupied += cost(member);
      }
      return occupied + cost(target) <= action.grappleMaxActiveGrapples;
    } catch (error) {
      console.error("Failed source-owned save Grapple capacity gate", {
        actor: actor?.combatant_id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

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
        && action.grappleEscapeDc
        && saveGrappleAllowed(actor, target, action, options.setup || null)) {
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
          null,
          { preventsBreathing: Boolean(action.grapplePreventsBreathing) },
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
