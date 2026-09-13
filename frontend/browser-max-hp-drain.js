(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(attackerState, defenderState, attack, components) {
    try {
      const effect = attack.maxHpDrain;
      if (!effect) return { reduced: 0, healed: 0 };
      const amount = (components || [])
        .filter((part) => part.damage_type === effect.damageType)
        .reduce((sum, part) => sum + (part.applied_total || 0), 0);
      if (amount <= 0) return { reduced: 0, healed: 0 };
      const before = S().effectiveMaxHp(defenderState), reduced = Math.min(amount, before);
      defenderState.max_hp_reduction = (defenderState.max_hp_reduction || 0) + reduced;
      const after = S().effectiveMaxHp(defenderState);
      defenderState.current_hp = Math.min(defenderState.current_hp, after);
      if (effect.zeroMaxHpKills && after === 0) {
        defenderState.current_hp = 0; defenderState.is_alive = false; defenderState.is_dead = true;
        defenderState.is_unconscious = false; defenderState.is_stable = false;
        defenderState.death_save_successes = 0; defenderState.death_save_failures = 0;
      }
      let healed = 0;
      if (effect.healAttacker && attackerState.is_alive && !attackerState.is_dead) {
        const maximum = S().effectiveMaxHp(attackerState);
        healed = Math.max(0, Math.min(reduced, maximum - attackerState.current_hp));
        attackerState.current_hp += healed;
      }
      return { reduced, healed };
    } catch (error) {
      console.error("Browser max-HP drain resolution failed", { attack: attack?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAX_HP_DRAIN = { resolve };
})();
