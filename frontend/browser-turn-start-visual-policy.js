(() => {
  "use strict";

  function validate(rule) {
    try {
      if (!rule || typeof rule.sourceId !== 'string' || !rule.sourceId.trim() || typeof rule.sourceName !== 'string' || !rule.sourceName.trim()) throw new Error("Visual source identity required.");
      if (!Number.isInteger(rule.rangeFt) || rule.rangeFt <= 0) throw new Error("Invalid visual range.");
      if (!Number.isInteger(rule.saveDc) || rule.saveDc < 1 || rule.saveDc > 40) throw new Error("Invalid visual DC.");
      if (!["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"].includes(rule.saveAbility === undefined ? "constitution" : rule.saveAbility)) {
        throw new Error("Invalid visual save ability.");
      }
      if (rule.immediatePetrificationMargin != null &&
          (!Number.isInteger(rule.immediatePetrificationMargin) || rule.immediatePetrificationMargin <= 0)) {
        throw new Error("Invalid immediate failure margin.");
      }
      for (const key of ["initialDebuff", "terminalDebuff"]) {
        if (rule[key] !== undefined && (typeof rule[key] !== "string" || !rule[key].trim())) throw new Error("Invalid visual debuff stage.");
      }
      if (rule.failedSaveTimedEffect != null) {
        const timed = rule.failedSaveTimedEffect;
        if (!timed || typeof timed.effectId !== "string" || !timed.effectId.trim()
            || timed.repeatSaveDc !== rule.saveDc || !timed.repeatSaveAbility
            || !timed.repeatSaveTiming || !timed.sourceEffectImmunityOnEnd
            || rule.sourceEffectImmunityOnSuccess !== true || rule.immediatePetrificationMargin != null) {
          throw new Error("Timed visual save requires exact repeat-save and source immunity parameters.");
        }
      }
      if (rule.requiredTargetCreatureTypes !== undefined && (!Array.isArray(rule.requiredTargetCreatureTypes)
          || rule.requiredTargetCreatureTypes.some(x => typeof x !== "string" || !x.trim()))) {
        throw new Error("Invalid qualified visual creature types.");
      }
      for (const key of ["requiresSourceSight", "requiresSourceNotIncapacitated",
        "requiresTrueFormVisibility", "sourceEffectImmunityOnSuccess"]) {
        if (rule[key] !== undefined && typeof rule[key] !== "boolean") throw new Error("Invalid visual source qualifier.");
      }
      if ((rule.initialDebuff === undefined ? "restrained" : rule.initialDebuff) ===
          (rule.terminalDebuff === undefined ? "petrified" : rule.terminalDebuff)) throw new Error("Distinct debuff stages required.");
      return rule;
    } catch (error) {
      console.error("Invalid visual rule.", error);
      throw error;
    }
  }

  function initiativePrecedes(turnOrder, sourceId, targetId) {
    try {
      if (!Array.isArray(turnOrder) || !turnOrder.length
          || turnOrder.some(id => typeof id !== "string" || !id.trim())
          || new Set(turnOrder).size !== turnOrder.length
          || typeof sourceId !== "string" || !sourceId.trim()
          || typeof targetId !== "string" || !targetId.trim()
          || sourceId === targetId) {
        throw new Error("Gaze priority requires unique, valid resolved initiative members.");
      }
      const source = turnOrder.indexOf(sourceId);
      const target = turnOrder.indexOf(targetId);
      if (source < 0 || target < 0) throw new Error("Gaze source or target missing from initiative.");
      return source < target;
    } catch (error) {
      console.error("Failed source-neutral gaze initiative priority", { sourceId, targetId, error });
      throw error;
    }
  }

  function decide(rule, facts) {
    try {
      validate(rule);
      if (!facts || !Number.isInteger(facts.distanceFt) || facts.distanceFt < 0) {
        throw new Error("Invalid visual distance.");
      }
      for (const key of ["sourceActive", "targetActive", "sourceSeesTarget", "targetSeesSource", "targetImmune", "sourcePrecedesTarget"]) {
        if (typeof facts[key] !== "boolean") throw new Error("Visual eligibility flags must be booleans.");
      }
      for (const key of ["sourceTrueFormVisible", "targetTypeAllowed"]) {
        if (facts[key] !== undefined && typeof facts[key] !== "boolean") throw new Error("Invalid visual qualifier.");
      }
      if (facts.distanceFt > rule.rangeFt || !facts.sourceActive || !facts.targetActive
          || (rule.requiresSourceSight !== false && !facts.sourceSeesTarget)
          || !facts.targetSeesSource || facts.targetImmune || facts.targetTypeAllowed === false
          || (rule.requiresTrueFormVisibility === true && facts.sourceTrueFormVisible !== true)) return "ineligible";
      return facts.sourcePrecedesTarget ? "save_required" : "averted";
    } catch (error) {
      console.error("Visual eligibility failed.", error);
      throw error;
    }
  }

  function resolveStage(rule, saveTotal, previousStage = null) {
    try {
      validate(rule);
      if (!Number.isInteger(saveTotal)) throw new Error("Visual save total must be an integer.");
      const initial = rule.initialDebuff === undefined ? "restrained" : rule.initialDebuff;
      const terminal = rule.terminalDebuff === undefined ? "petrified" : rule.terminalDebuff;
      if (previousStage !== null && previousStage !== initial) throw new Error("Invalid visual stage.");
      const outcome = window.IRON_PIT_BROWSER_STAGED_SAVE_DEBUFF.resolve({
        saveTotal, dc: rule.saveDc, initialEffect: initial, terminalEffect: terminal,
        previousEffect: previousStage, immediateFailureMargin: rule.immediatePetrificationMargin ?? null,
      });
      return outcome ?? "clear";
    } catch (error) {
      console.error("Visual save progression failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY = { validate, decide, initiativePrecedes, resolveStage };
})();
