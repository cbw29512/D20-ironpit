(() => {
  "use strict";

  function active(defender) {
    try {
      for (const action of defender.state.template.timed_self_buff_actions || []) {
        if (!action.meleeHitRetaliation) continue;
        if ((defender.state.timed_effects || []).some((effect) => effect.source_effect_id === action.id)) {
          return { action, rule: action.meleeHitRetaliation };
        }
      }
      return null;
    } catch (error) {
      console.error("Failed to read melee-hit retaliation", { defender: defender?.combatant_id, error });
      throw error;
    }
  }

  function apply(attacker, defender, options = {}) {
    try {
      if (!options.melee || attacker.state.is_dead || !attacker.state.is_alive) return 0;
      const bound = active(defender);
      if (!bound) return 0;
      const distance = window.IRON_PIT_BROWSER_STATE.distance(attacker, defender);
      if (distance > (bound.rule.rangeFt || 5)) return 0;
      const rolls = window.IRON_PIT_DICE.rollMany(bound.rule.diceCount, bound.rule.diceSize);
      const raw = rolls.reduce((sum, value) => sum + value, 0);
      const applied = window.IRON_PIT_BROWSER_ATTACK.adjustedDamage(attacker.state, raw, bound.rule.damageType);
      if (applied) {
        const states = options.setup
          ? [...options.setup.heroes, ...options.setup.monsters].map((member) => member.state)
          : options.affectedStates || [];
        window.IRON_PIT_BROWSER_ATTACK.applyDamage(attacker.state, applied, false, [bound.rule.damageType], states, options.setup || null);
      }
      return applied;
    } catch (error) {
      console.error("Failed melee-hit retaliation", { defender: defender?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MELEE_RETALIATION = { active, apply };
})();
