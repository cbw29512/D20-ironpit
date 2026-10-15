(() => {
  "use strict";

  function validate(rule) {
    try {
      if (!rule || typeof rule.sourceId !== 'string' || !rule.sourceId.trim() || typeof rule.sourceName !== 'string' || !rule.sourceName.trim()) throw new Error("Visual source identity required.");
      if (!Number.isInteger(rule.rangeFt) || rule.rangeFt <= 0) throw new Error("Invalid visual range.");
      if (!Number.isInteger(rule.saveDc) || rule.saveDc < 1 || rule.saveDc > 40) throw new Error("Invalid visual DC.");
      if (!["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"].includes(rule.saveAbility || "constitution")) {
        throw new Error("Invalid visual save ability.");
      }
      if (rule.immediatePetrificationMargin != null &&
          (!Number.isInteger(rule.immediatePetrificationMargin) || rule.immediatePetrificationMargin <= 0)) {
        throw new Error("Invalid immediate failure margin.");
      }
      if ((rule.initialDebuff || "restrained") === (rule.terminalDebuff || "petrified")) throw new Error("Distinct debuff stages required.");
      return rule;
    } catch (error) {
      console.error("Invalid visual rule.", error);
      throw error;
    }
  }

  function decide(rule, facts) {
    try {
      validate(rule);
      if (!facts || !Number.isInteger(facts.distanceFt) || facts.distanceFt < 0) {
        throw new Error("Invalid visual distance.");
      }
      for (const key of ["sourceActive", "targetActive", "sourceSeesTarget", "targetSeesSource", "targetImmune", "targetSurprised"]) {
        if (typeof facts[key] !== "boolean") throw new Error("Visual eligibility flags must be booleans.");
      }
      if (facts.distanceFt > rule.rangeFt || !facts.sourceActive || !facts.targetActive ||
          !facts.sourceSeesTarget || !facts.targetSeesSource || facts.targetImmune) return "ineligible";
      if (!facts.targetSurprised) return "averted";
      return "save_required";
    } catch (error) {
      console.error("Visual eligibility failed.", error);
      throw error;
    }
  }

  function resolveStage(rule, saveTotal, previousStage = null) {
    try {
      validate(rule);
      if (!Number.isInteger(saveTotal)) throw new Error("Visual save total must be an integer.");
      const initial = rule.initialDebuff || "restrained";
      const terminal = rule.terminalDebuff || "petrified";
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

  window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY = { validate, decide, resolveStage };
})();
