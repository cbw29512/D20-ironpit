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

  function abilityModifierDelta(state, ability) {
    if (ability == null || !(state.ability_score_reductions?.[ability] > 0)) return 0;
    const base = state.template.ability_scores?.[ability];
    if (!Number.isInteger(base)) throw new Error("Missing source ability score.");
    return effectiveModifier(state, ability) - Math.floor((base - 10) / 2);
  }

  function apply(state, ability, amount, { zeroKills = false, affectedStates = [] } = {}) {
    try {
      // zeroKills is a deprecated call-site option: zero in ANY ability always kills.
      if (!Number.isInteger(amount) || amount < 0) throw new Error("Invalid ability reduction amount.");
      const before = effectiveScore(state, ability);
      if (state.is_dead || amount === 0 || before === 0) {
        return { ability, scoreBefore: before, scoreAfter: before, applied: 0, deathOutcome: null };
      }
      const after = Math.max(0, before - amount);
      const applied = before - after;
      const zero = after === 0 && applied ? window.IRON_PIT_BROWSER_TERMINAL_EFFECTS : null;
      // Fail closed before changing state if the terminal-death handler is absent.
      if (after === 0 && applied && !zero?.applyTerminalDeath) {
        throw new Error("Terminal effect runtime is required.");
      }
      if (applied > 0) {
        state.ability_score_reductions ||= {};
        state.ability_score_reductions[ability] = (state.ability_score_reductions[ability] || 0) + applied;
      }
      const deathOutcome = after === 0 && applied ? zero.applyTerminalDeath(state, affectedStates) : null;
      return { ability, scoreBefore: before, scoreAfter: after, applied, deathOutcome };
    } catch (error) {
      console.error("Browser ability-score reduction failed", { combatant: state?.template?.name, ability, error });
      throw error;
    }
  }

  function applyOnHit(state, effect, affectedStates = []) {
    try {
      if (!effect || !ABILITIES.has(effect.ability)
        || !Number.isInteger(effect.diceCount) || effect.diceCount < 1 || effect.diceCount > 40
        || !Number.isInteger(effect.diceSize) || effect.diceSize < 2 || effect.diceSize > 100) {
        throw new Error("Invalid on-hit ability-score reduction declaration.");
      }
      if (typeof window.IRON_PIT_DICE?.rollMany !== "function") {
        throw new Error("Browser dice runtime is required for ability reduction.");
      }
      if (state.is_dead) return null;
      const rolls = window.IRON_PIT_DICE.rollMany(effect.diceCount, effect.diceSize);
      const result = apply(state, effect.ability, rolls.reduce((sum, roll) => sum + roll, 0), { affectedStates });
      return { ...result, source: effect.source, rolls };
    } catch (error) {
      console.error("On-hit ability-score drain failed", { combatant: state?.template?.name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ABILITY_SCORE_REDUCTION = { effectiveScore, effectiveModifier, abilityModifierDelta, apply, applyOnHit };
})();