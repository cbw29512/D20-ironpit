(() => {
  "use strict";

  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Melee retaliation damage requires the shared damage resolver.");
    return rules;
  };

  function activeAll(defender) {
    try {
      return (defender.state.template.timed_self_buff_actions || [])
        .filter((action) => action.meleeHitRetaliation && (
          action.activationTiming === "passive"
          || (defender.state.timed_effects || []).some((effect) => effect.source_effect_id === action.id)
        ))
        .map((action) => ({ action, rule: action.meleeHitRetaliation }));
    } catch (error) {
      console.error("Failed to read melee-hit retaliation", { defender: defender?.combatant_id, error });
      throw error;
    }
  }

  function active(defender) {
    return activeAll(defender)[0] || null;
  }

  function apply(attacker, defender, options = {}) {
    try {
      if ((!options.melee && !options.physicalContact) || attacker.state.is_dead || !attacker.state.is_alive) return 0;
      const distance = window.IRON_PIT_BROWSER_STATE.distance(attacker, defender);
      let total = 0;
      for (const { action, rule } of activeAll(defender)) {
        if (!options.melee && !rule.onContact) continue;
        if (distance > (rule.rangeFt || 5)) continue;
        const rolls = window.IRON_PIT_DICE.rollMany(rule.diceCount, rule.diceSize);
        const raw = rolls.reduce((sum, value) => sum + value, 0);
        const applied = DD().resolveDamage(attacker.state, raw, rule.damageType).applied;
        if (applied) {
          const states = options.setup
            ? [...options.setup.heroes, ...options.setup.monsters].map((member) => member.state)
            : options.affectedStates || [];
          window.IRON_PIT_BROWSER_ATTACK.applyDamage(attacker.state, applied, false, [rule.damageType], states, options.setup || null);
        }
        total += applied;
      }
      return total;
    } catch (error) {
      console.error("Failed melee-hit retaliation", { defender: defender?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MELEE_RETALIATION = { active, activeAll, apply };
})();
