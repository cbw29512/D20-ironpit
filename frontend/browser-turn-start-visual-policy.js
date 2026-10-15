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
      for (const key of ["sourceActive", "targetActive", "sourceSeesTarget", "targetSeesSource", "targetImmune", "targetSurprised", "avertsEyes"]) {
        if (typeof facts[key] !== "boolean") throw new Error("Visual eligibility flags must be booleans.");
      }
      if (facts.distanceFt > rule.rangeFt || !facts.sourceActive || !facts.targetActive ||
          !facts.sourceSeesTarget || !facts.targetSeesSource || facts.targetImmune) return "ineligible";
      if (facts.avertsEyes === true && !facts.targetSurprised) return "averted";
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
      if (previousStage !== null && previousStage !== "restrained") throw new Error("Invalid visual stage.");
      if (saveTotal >= rule.saveDc) return "clear";
      if (previousStage === "restrained") return "petrified";
      const margin = rule.immediatePetrificationMargin;
      return margin != null && rule.saveDc - saveTotal >= margin ? "petrified" : "restrained";
    } catch (error) {
      console.error("Visual save progression failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_VISUAL_POLICY = { validate, decide, resolveStage };
})();
