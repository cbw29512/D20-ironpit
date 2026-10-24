(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ABILITY_CHECKS;
  const E = () => window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;

  function disadvantage(state, ability, setup = null) {
    try {
      let count = 0;
      if ((state.active_effect_ids || []).includes("poisoned")) count += 1;
      if (window.IRON_PIT_BROWSER_CONDITION_RULES.has(state, "frightened", setup)) count += 1;
      count += X()?.abilityCheckDisadvantageSources?.(state, ability) || 0;
      return count;
    } catch (error) {
      console.error("Contested movement disadvantage lookup failed.", error);
      throw error;
    }
  }

  function check(member, ability, setup = null) {
    const mode = A().mode(member.state, 0, disadvantage(member.state, ability, setup), { ability });
    return R().d20(
      E().abilityCheckBonus(member.state, ability) + (X()?.d20Modifier(member.state) || 0),
      mode,
    );
  }

  function resolve(source, target, attack, setup, round) {
    try {
      const effect = attack.onHitContestedMovement;
      if (!effect || target.state.is_dead || !target.state.is_alive) return null;
      if (effect.maxTargetSize && !window.IRON_PIT_BROWSER_STATE.sizeAtMost(target, effect.maxTargetSize)) return null;
      let sourceRoll = check(source, effect.sourceAbility, setup);
      let targetRoll = check(target, effect.targetAbility, setup);
      sourceRoll = A().resolve(source.state, effect.sourceAbility, sourceRoll, targetRoll.total, {
        roller: source, setup, round,
      }).roll;
      const targetResolved = A().resolve(target.state, effect.targetAbility, targetRoll, sourceRoll.total, {
        roller: target, setup, round,
      });
      targetRoll = targetResolved.roll;
      const targetSucceeded = targetResolved.succeeded;
      // Contested roll remains a RAW log result; the Pit suppresses displacement.
      const movementFt = 0;
      return {
        sourceRoll, targetRoll,
        sourceAbility: effect.sourceAbility,
        targetAbility: effect.targetAbility,
        targetSucceeded,
        movementFt,
        direction: effect.direction,
      };
    } catch (error) {
      console.error("On-hit contested movement failed.", {
        source: source?.combatant_id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONTESTED_MOVEMENT = { resolve };
})();
