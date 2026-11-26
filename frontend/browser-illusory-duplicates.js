(() => {
  "use strict";
  function effectiveModifier(state, ability) {
    const runtime = window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION;
    if (runtime?.effectiveModifier) return runtime.effectiveModifier(state, ability);
    const score = state.template.ability_scores?.[ability];
    if (!Number.isInteger(score)) throw new Error("Illusory duplicates require a source ability score.");
    return Math.floor((score - 10) / 2);
  }
  function intercept(attacker, defender, distance) {
    try {
      const rules = window.IRON_PIT_BROWSER_CONDITION_RULES;
      if (!rules?.canSee?.(attacker, defender, distance)) return null;
      for (const effect of defender.timed_effects || []) {
        const remaining = Number(effect.illusory_duplicates_remaining || 0);
        if (remaining <= 0 || !effect.source_effect_id) continue;
        const actions = (defender.template.timed_self_buff_actions || []).filter((action) =>
          action.id === effect.source_effect_id && action.illusoryDuplicateDefense,
        );
        if (actions.length !== 1) throw new Error("A live duplicate effect requires one declarative source action.");
        const action = actions[0], rule = action.illusoryDuplicateDefense;
        const senses = window.IRON_PIT_BROWSER_EFFECTIVE_SENSES;
        if (!senses) throw new Error("Illusory duplicates require effective-senses runtime.");
        if ((rule.bypassAttackerSenses || []).some((sense) =>
          senses.effectiveSenseRangeFt(attacker, sense) >= distance)) return null;
        const uniform = rule.redirectionMode === "uniform_original_and_duplicates";
        const sides = uniform ? remaining + 1 : 20;
        const thresholds = rule.redirectMinimumByDuplicates || [];
        if (!uniform && remaining >= thresholds.length)
          throw new Error("Duplicate count exceeds its source threshold table.");
        const result = window.IRON_PIT_DICE.roll(sides);
        const redirectionRoll = { notation: `1d${sides}`, rolls: [result], modifier: 0,
          selected_roll: result, mode: "normal", total: result };
        if (uniform ? result === 1 : result < thresholds[remaining]) return null;
        return { effect, featureId: action.id, featureName: action.name, redirectionRoll,
          targetAc: rule.armorClassMode === "source_armor_class"
            ? Number(defender.template.armor_class)
            : Number(rule.armorClassBase) + effectiveModifier(defender, rule.armorClassAbility) };
      }
      return null;
    } catch (error) {
      console.error("Browser illusory duplicate interception failed.", { error });
      throw error;
    }
  }
  function consumeHit(defender, interception) {
    const effect = interception.effect;
    if (!(defender.timed_effects || []).includes(effect)
      || Number(effect.illusory_duplicates_remaining || 0) <= 0)
      throw new Error("The intercepted duplicate is no longer active.");
    effect.illusory_duplicates_remaining -= 1;
    if (effect.illusory_duplicates_remaining === 0) {
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!timed?.removeGroup) throw new Error("Duplicate exhaustion requires timed-effect cleanup.");
      timed.removeGroup(defender, effect);
    }
    return effect.illusory_duplicates_remaining;
  }
  window.IRON_PIT_BROWSER_ILLUSORY_DUPLICATES = { consumeHit, intercept };
})();
