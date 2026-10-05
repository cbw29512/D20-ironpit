(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function creatureMatchesKind(template, kind) {
    const expected = String(kind || "").trim().toLowerCase();
    if (!expected) return false;
    const raw = String(template?.creature_type || "");
    const base = raw.split(" (")[0].trim().toLowerCase();
    if (base === expected) return true;
    const open = raw.indexOf("(");
    const close = raw.lastIndexOf(")");
    if (open < 0 || close <= open) return false;
    return raw.slice(open + 1, close).split(",").some((part) => part.trim().toLowerCase() === expected);
  }

  function resolve(target, attack, sourceTemplate = null, round = null, setup = null, attacker = null) {
    const effect = attack.onHitConditionSave;
    if (!effect || target.state.is_dead || !target.state.is_alive) return null;
    if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) return null;
    const kinds = [...(effect.excludedCreatureTypes || []), ...(effect.excludedCreatureSubtypes || [])];
    if (kinds.some((kind) => creatureMatchesKind(target.state.template, kind))) return null;
    if (I().immune(target.state, effect.conditionId, sourceTemplate)) return null;
    const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(target.state, effect.saveAbility, effect.dc, {
      conditionId: effect.conditionId,
      effectTags: effect.conditionId === "poisoned" ? ["poison"] : [],
      roundNumber: round,
      encounterRoller: target,
      setup,
    });
    let appliedCondition = null;
    if (!save.succeeded) {
      const timed = effect.durationRounds || effect.repeatSaveTiming;
      if (timed) {
        if (!T()?.apply) throw new Error("Timed on-hit condition save requires browser-timed-conditions.js.");
        appliedCondition = T().apply(target.state, effect.conditionId, attacker?.combatant_id || sourceTemplate?.id || "on-hit-save", {
          sourceEffectId: attack.name || attack.id,
          sourceTemplate,
          appliedRound: round,
          expiresRound: effect.durationRounds != null && round != null ? round + effect.durationRounds : null,
          expiryTiming: effect.durationRounds != null ? "target_turn_end" : null,
          repeatSaveAbility: effect.repeatSaveTiming ? effect.saveAbility : null,
          repeatSaveDc: effect.repeatSaveTiming ? effect.dc : null,
          repeatSaveTiming: effect.repeatSaveTiming || null,
          useDefaultPoisonRecovery: false,
        }) || null;
      } else if (!target.state.active_effect_ids.includes(effect.conditionId)) {
        target.state.active_effect_ids.push(effect.conditionId);
        appliedCondition = effect.conditionId;
      }
    }
    return {
      saveRoll: save.roll, saveAbility: effect.saveAbility, saveDc: effect.dc,
      saveSucceeded: save.succeeded, appliedCondition,
    };
  }

  window.IRON_PIT_BROWSER_ON_HIT_CONDITION_SAVE = { resolve, creatureMatchesKind };
})();
