(() => {
  "use strict";

  const SENSE_BLINDSIGHT = "blindsight";
  const SENSE_TRUESIGHT = "truesight";
  const DEAFENED = "deafened";
  const BLINDSIGHT_REQUIRES_HEARING = "blindsight_requires_hearing";

  function senseSource(observer) {
    const nested = observer && observer.template;
    if (nested && (
      nested.blindsight_ft != null
      || nested.truesight_ft != null
      || nested[BLINDSIGHT_REQUIRES_HEARING] != null
    )) {
      return nested;
    }
    return observer || {};
  }

  function sourceSenseRangeFt(observer, senseId) {
    try {
      const template = senseSource(observer);
      if (senseId === SENSE_BLINDSIGHT) return Math.max(0, Number(template.blindsight_ft || 0));
      if (senseId === SENSE_TRUESIGHT) return Math.max(0, Number(template.truesight_ft || 0));
      return 0;
    } catch (error) {
      console.error("Failed to read source sense range.", { senseId, error });
      throw error;
    }
  }

  function flagEnabled(observer, flagName) {
    if (Boolean(observer && observer[flagName])) return true;
    const source = senseSource(observer);
    return Boolean(source && source[flagName]);
  }

  function hasCondition(observer, conditionId) {
    const effects = (observer && observer.active_effect_ids) || [];
    if (!effects.includes(conditionId)) return false;
    const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
    if (rules && rules.has && observer && observer.template) return rules.has(observer, conditionId);
    return true;
  }

  function senseIsSuppressed(observer, senseId) {
    try {
      const modifiers = (observer && observer.active_modifiers) || [];
      if (modifiers.some((item) => item.suppressed_sense_id === senseId)) return true;
      if (
        senseId === SENSE_BLINDSIGHT
        && flagEnabled(observer, BLINDSIGHT_REQUIRES_HEARING)
        && hasCondition(observer, DEAFENED)
      ) {
        return true;
      }
      const grants = (senseSource(observer).sense_suppressors) || [];
      return grants.some((grant) => grant.sense_id === senseId
        && (grant.suppressed_while_conditions || []).some((conditionId) => hasCondition(observer, conditionId)));
    } catch (error) {
      console.error("Failed to resolve sense suppression.", { senseId, error });
      throw error;
    }
  }

  function effectiveSenseRangeFt(observer, senseId) {
    try {
      return senseIsSuppressed(observer, senseId) ? 0 : sourceSenseRangeFt(observer, senseId);
    } catch (error) {
      console.error("Failed to resolve effective sense range.", { senseId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_EFFECTIVE_SENSES = {
    BLINDSIGHT_REQUIRES_HEARING,
    DEAFENED,
    SENSE_BLINDSIGHT,
    SENSE_TRUESIGHT,
    effectiveSenseRangeFt,
    senseIsSuppressed,
    sourceSenseRangeFt,
  };
})();
