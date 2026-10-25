(() => {
  "use strict";

  function legalAction(action, target, distance, sourceId, actor = null) {
    try {
      const Q = window.IRON_PIT_BROWSER_CONDITION_RULES || {
        has: (state, id) => (state.active_effect_ids || []).includes(id),
        canSee: () => true,
      };
      const S = window.IRON_PIT_BROWSER_STATE;
      const timed = window.IRON_PIT_BROWSER_FAILED_SAVE_TIMED_EFFECTS;
      const shared = window.IRON_PIT_BROWSER_SAVE_IMMUNITY;
      if (action.requiredTargetCondition
        && !Q.has(target.state, action.requiredTargetCondition)) return false;
      if ((action.prohibitedTargetSourceEffectIds || []).length
        && (target.state.timed_effects || []).some(
          (effect) => action.prohibitedTargetSourceEffectIds.includes(effect.source_effect_id),
        )) return false;
      if (actor && action.requiresTargetSight
        && !Q.canSee(actor.state, target.state, distance)) return false;
      if (action.requiresTargetToSeeSource
        && (!actor || !Q.canSee(target.state, actor.state, S.distance(actor, target)))) return false;
      if (distance > action.range) return false;
      if (sourceId && timed?.isImmune(target, action, sourceId)) return false;
      if ((action.sourceEffectImmunityKeysBlocking || []).length) {
        if (!shared?.hasSharedImmunity) {
          throw new Error("Shared save-immunity lookup runtime is unavailable.");
        }
        if (shared.hasSharedImmunity(
          target.state, action.sourceEffectImmunityKeysBlocking,
        )) return false;
      }
      if (action.requiresTargetHearing
        && target.state.active_effect_ids.includes("deafened")) return false;
      const type = String(target.state.template.creature_type || "")
        .split(" (")[0].trim().toLowerCase();
      if ((action.requiredTargetCreatureTypes || []).length
        && !(action.requiredTargetCreatureTypes || []).some(
          (kind) => String(kind).toLowerCase() === type,
        )) return false;
      if ((action.excludedTargetCreatureTypes || []).some(
        (kind) => String(kind).toLowerCase() === type,
      )) return false;
      return !action.targetMaxSize || S.sizeAtMost(target, action.targetMaxSize);
    } catch (error) {
      console.error("Browser save-action legality failed", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolveOnHitConditionSave(
    target, attack, sourceTemplate = null, round = null, setup = null, attacker = null,
  ) {
    try {
      const impl = window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE;
      if (impl?.resolve) {
        return impl.resolve(
          target, attack, sourceTemplate, round, setup, attacker,
        );
      }
      const effect = attack.onHitConditionSave;
      if (!effect || target.state.is_dead || !target.state.is_alive) return null;
      const S = window.IRON_PIT_BROWSER_STATE;
      const I = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || {
        immune: () => false,
      };
      if (effect.maxTargetSize
        && !S.sizeAtMost(target, effect.maxTargetSize)) return null;
      if (I.immune(
        target.state, effect.conditionId, sourceTemplate, { actor: target, setup },
      )) return null;
      if (effect.durationRounds || effect.repeatSaveTiming
        || (effect.excludedCreatureTypes || []).length
        || (effect.excludedCreatureSubtypes || []).length) {
        throw new Error("On-hit condition save lifecycle runtime is not loaded.");
      }
      const effectTags = effect.conditionId === "poisoned" ? ["poison"] : [];
      const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
        target.state, effect.saveAbility, effect.dc, {
          conditionId: effect.conditionId,
          effectTags,
          roundNumber: round,
          encounterRoller: target,
          setup,
        },
      );
      let appliedCondition = null;
      if (!save.succeeded
        && !target.state.active_effect_ids.includes(effect.conditionId)) {
        target.state.active_effect_ids.push(effect.conditionId);
        appliedCondition = effect.conditionId;
      }
      return {
        saveRoll: save.roll,
        saveAbility: effect.saveAbility,
        saveDc: effect.dc,
        saveSucceeded: save.succeeded,
        appliedCondition,
      };
    } catch (error) {
      console.error("Browser on-hit condition-save delegation failed", {
        attackId: attack?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_ACTION_SUPPORT = {
    legalAction, resolveOnHitConditionSave,
  };
})();
