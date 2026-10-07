(() => {
  "use strict";

  function apply(state, damageBefore = {}) {
    try {
      const applied = [];
      for (const rule of state.template.damage_taken_timed_effects || []) {
        const type = rule.triggerDamageType;
        const before = Number(damageBefore[type] || 0);
        const after = Number(state.damage_taken_this_turn_by_type?.[type] || 0);
        if (after <= before) continue;
        const effect = window.IRON_PIT_BROWSER_TIMED?.apply(
          state, rule.effectId, state.template.id, {
            sourceEffectId: rule.sourceId,
            expiresAtStartOfSourceTurn: false,
            expiryTiming: "target_turn_end",
            expiresTargetTurnCount: (state.turns_started || 0) + (rule.targetTurns || 1),
            useDefaultPoisonRecovery: false,
            controlLimits: {
              attack_roll_disadvantage: Boolean(rule.attackRollDisadvantage),
              ability_check_disadvantage: Boolean(rule.abilityCheckDisadvantage),
            },
          },
        );
        if (effect) applied.push(effect);
      }
      return applied;
    } catch (error) {
      console.error("Browser damage-triggered timed effects failed.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TAKEN_EFFECTS = { apply };
})();
