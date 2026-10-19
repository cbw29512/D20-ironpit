(() => {
  "use strict";
  const ABILITIES = new Set([
    "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
  ]);

  function effectiveScore(state, ability) {
    if (!ABILITIES.has(ability)) throw new Error("Unknown ability score.");
    const base = state?.template?.ability_scores?.[ability];
    if (!Number.isInteger(base) || base < 1) throw new Error("Certified ability scores are required.");
    const reduction = (state.ability_score_reductions || {})[ability] || 0;
    if (!Number.isInteger(reduction) || reduction < 0) throw new Error("Invalid ability reduction state.");
    return Math.max(0, base - reduction);
  }

  function effectiveModifier(state, ability) {
    return Math.floor((effectiveScore(state, ability) - 10) / 2);
  }

  function apply(state, ability, amount, { zeroKills = false, affectedStates = [] } = {}) {
    if (!Number.isInteger(amount) || amount < 0) throw new Error("Invalid ability reduction amount.");
    const before = effectiveScore(state, ability);
    if (state.is_dead || amount === 0 || before === 0) {
      return { ability, scoreBefore: before, scoreAfter: before, applied: 0, deathOutcome: null };
    }
    const after = Math.max(zeroKills ? 0 : 1, before - amount);
    const applied = before - after;
    if (applied > 0) {
      state.ability_score_reductions ||= {};
      state.ability_score_reductions[ability] = (state.ability_score_reductions[ability] || 0) + applied;
    }
    let deathOutcome = null;
    if (zeroKills && after === 0 && applied) {
      const zero = window.IRON_PIT_BROWSER_ZERO_HP;
      if (!zero?.applyInstantDeath) throw new Error("Instant-death runtime is required for lethal ability reduction.");
      deathOutcome = zero.applyInstantDeath(state, affectedStates);
    }
    return { ability, scoreBefore: before, scoreAfter: after, applied, deathOutcome };
  }

  window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION = { effectiveScore, effectiveModifier, apply };
})();