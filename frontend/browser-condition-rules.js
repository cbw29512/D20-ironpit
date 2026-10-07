(() => {
  "use strict";

  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  function has(state, id) {
    if (!state.active_effect_ids.includes(id)) return false;
    const timed = (state.timed_effects || []).filter((effect) => effect.effect_id === id);
    if (timed.length) {
      return timed.some((effect) => !I().immune(state, id, null, { sourceIsMagical: Boolean(effect.source_is_magical) }));
    }
    return !I().immune(state, id);
  }

  const unconscious = (state) => Boolean(state.is_unconscious || has(state, "unconscious"));

  const invisibilitySuppressed = (state) => Boolean(
    (state.active_modifiers || []).some((item) => item.kind === "invisibility-benefits-suppressed")
  );

  function sourceSenseRangeFt(observer, senseId) {
    const senses = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
    if (senses && senses.sourceSenseRangeFt) return senses.sourceSenseRangeFt(observer, senseId);
    try {
      const template = observer?.template || observer || {};
      if (senseId === "blindsight") return Math.max(0, Number(template.blindsight_ft || 0));
      if (senseId === "truesight") return Math.max(0, Number(template.truesight_ft || 0));
      return 0;
    } catch (error) {
      console.error("Failed to read browser source sense range.", { senseId, error });
      throw error;
    }
  }

  function hearingBlindsightSuppressed(observer) {
    const flag = Boolean(observer?.blindsight_requires_hearing || observer?.template?.blindsight_requires_hearing);
    return flag && has(observer, "deafened");
  }

  function senseIsSuppressed(observer, senseId) {
    const senses = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
    if (senses && senses.senseIsSuppressed) return senses.senseIsSuppressed(observer, senseId);
    try {
      const modifiers = observer?.active_modifiers || [];
      if (modifiers.some((item) => item.suppressed_sense_id === senseId)) return true;
      if (senseId === "blindsight" && hearingBlindsightSuppressed(observer)) return true;
      const grants = observer?.template?.sense_suppressors || [];
      return grants.some((grant) => grant.sense_id === senseId
        && (grant.suppressed_while_conditions || []).some((conditionId) => has(observer, conditionId)));
    } catch (error) {
      console.error("Failed to resolve browser sense suppression.", { senseId, error });
      throw error;
    }
  }

  function effectiveSenseRangeFt(observer, senseId) {
    const senses = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
    if (senses && senses.effectiveSenseRangeFt) return senses.effectiveSenseRangeFt(observer, senseId);
    try {
      return senseIsSuppressed(observer, senseId) ? 0 : sourceSenseRangeFt(observer, senseId);
    } catch (error) {
      console.error("Failed to resolve browser effective sense range.", { senseId, error });
      throw error;
    }
  }

  function visibilityDistanceFt(observer, target, distanceFt) {
    try {
      if (distanceFt != null) return Number(distanceFt);
      const observerPosition = observer?.position;
      const targetPosition = target?.position;
      const geom = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
      if (!observerPosition || !targetPosition || !geom) return null;
      return geom.footprintDistanceFt(
        observerPosition,
        observer?.template?.size,
        targetPosition,
        target?.template?.size,
      );
    } catch (error) {
      console.error("Failed to resolve browser visibility distance.", error);
      throw error;
    }
  }

  function senseReaches(observer, senseId, distanceFt) {
    return distanceFt != null && effectiveSenseRangeFt(observer, senseId) >= Number(distanceFt);
  }

  function canSee(observer, target, distanceFt = null) {
    try {
      const resolved = visibilityDistanceFt(observer, target, distanceFt);
      const hidden = has(target, "invisible") && !invisibilitySuppressed(target);
      const blinded = has(observer, "blinded");
      if (senseReaches(observer, "blindsight", resolved)) return true;
      if (blinded) return false;
      if (hidden) return senseReaches(observer, "truesight", resolved);
      return true;
    } catch (error) {
      console.error("Failed to resolve browser visibility.", {
        observer: observer?.template?.name, target: target?.template?.name, error,
      });
      throw error;
    }
  }

  function incapacitated(state) {
    if (I().immune(state, "incapacitated")) return false;
    return unconscious(state) || has(state, "incapacitated") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  }

  const autoFailStrDex = (state) => unconscious(state) || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const attackAdvantage = (state) => unconscious(state) || has(state, "blinded") || has(state, "paralyzed") || has(state, "petrified") || has(state, "stunned");
  const autoCritical = (state) => unconscious(state) || has(state, "paralyzed");
  const suppressAttackAdvantage = (state) => Boolean(state.template?.suppress_attack_advantage_while_not_incapacitated) && !incapacitated(state);
  const speedZero = (state) => unconscious(state) || has(state, "paralyzed") || has(state, "petrified") || has(state, "restrained")
    || (state.template.ruleset === "2014" && has(state, "stunned"));

  window.IRON_PIT_BROWSER_CONDITION_RULES = {
    attackAdvantage, autoCritical, autoFailStrDex, canSee, effectiveSenseRangeFt, has,
    incapacitated, invisibilitySuppressed, senseIsSuppressed, sourceSenseRangeFt, speedZero,
    suppressAttackAdvantage, visibilityDistanceFt,
  };
})();
