(() => {
  "use strict";

  const CONDITIONS = Object.freeze([
    "blinded", "charmed", "deafened", "exhaustion", "frightened", "grappled",
    "incapacitated", "invisible", "paralyzed", "petrified", "poisoned", "prone",
    "restrained", "stunned", "unconscious",
  ]);
  const COUNTER_KINDS = new Set(["condition-immunity", "debuff-counter"]);
  const R = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  function isBloodied(state) {
    try {
      const policy = window.IRON_PIT_BROWSER_HEALING_POLICY;
      if (policy?.bloodied) return policy.bloodied(state);
      const maximum = window.IRON_PIT_BROWSER_STATE?.effectiveMaxHp(state) || Number(state.template.max_hp || 0);
      return state.current_hp * 2 <= maximum;
    } catch (error) {
      console.error("Failed browser bloodied check", { error });
      throw error;
    }
  }

  function activeConditionIds(state) {
    try {
      const seen = [];
      for (const effectId of state.active_effect_ids || []) {
        if (CONDITIONS.includes(effectId) && !seen.includes(effectId) && R().has(state, effectId)) {
          seen.push(effectId);
        }
      }
      return seen;
    } catch (error) {
      console.error("Failed browser active-condition scan", { error });
      throw error;
    }
  }

  function suppressedConditionIds(state) {
    try {
      const seen = [];
      for (const effectId of state.active_effect_ids || []) {
        if (CONDITIONS.includes(effectId) && !seen.includes(effectId) && !R().has(state, effectId)) {
          seen.push(effectId);
        }
      }
      return seen;
    } catch (error) {
      console.error("Failed browser suppressed-condition scan", { error });
      throw error;
    }
  }

  function counteredConditionIds(action) {
    try {
      const answered = new Set();
      for (const effect of action.failedSaveModifierEffects || action.failed_save_modifier_effects || []) {
        const kind = effect.kind;
        const conditionId = effect.conditionId || effect.condition_id;
        const counter = effect.debuffCounter || effect.debuff_counter;
        if (kind === "condition-immunity" && conditionId) answered.add(String(conditionId));
        if (kind === "debuff-counter" && counter?.debuff_id) answered.add(String(counter.debuff_id));
      }
      return answered;
    } catch (error) {
      console.error("Failed browser countered-condition read", { action: action?.id, error });
      throw error;
    }
  }

  function failedSaveIsBeneficial(action) {
    try {
      if ((action.damageDiceCount || action.damage_dice_count || 0) > 0) return false;
      if ((action.damageComponents || action.damage_components || []).length) return false;
      if (action.failedSaveTimedEffect || action.failed_save_timed_effect) return false;
      const effects = action.failedSaveModifierEffects || action.failed_save_modifier_effects || [];
      const kinds = new Set(effects.map((effect) => String(effect.kind)));
      return kinds.size > 0 && [...kinds].every((kind) => COUNTER_KINDS.has(kind));
    } catch (error) {
      console.error("Failed browser beneficial-save check", { action: action?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEBUFF_ANSWERS = {
    activeConditionIds, counteredConditionIds, failedSaveIsBeneficial, isBloodied, suppressedConditionIds,
  };
})();
