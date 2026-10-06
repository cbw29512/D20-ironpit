(() => {
  "use strict";

  function applyReduction(state, amount, options = {}) {
    try {
      if (!Number.isInteger(amount) || amount < 0) throw new Error("Maximum-HP reduction must be a nonnegative integer.");
      if (!amount) return 0;
      if ((state.timed_effects || []).some((effect) => effect.prevent_hit_point_maximum_reduction)) return 0;
      state.hit_point_maximum_reduction = (state.hit_point_maximum_reduction || 0) + amount;
      const rawMaximum = (state.template.max_hp || 0) + (state.max_hp_bonus || 0)
        - state.hit_point_maximum_reduction;
      if (options.zeroMaxHpKills && rawMaximum <= 0) {
        state.current_hp = 0;
        state.is_alive = false;
        state.is_dead = true;
        state.is_unconscious = false;
        state.is_stable = false;
        state.death_save_successes = 0;
        state.death_save_failures = 0;
        return amount;
      }
      const maximum = window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state);
      state.current_hp = Math.min(state.current_hp, maximum);
      return amount;
    } catch (error) {
      console.error("Maximum-HP reduction failed.", error);
      throw error;
    }
  }

  function resolve(target, attack, damageTaken) {
    try {
      const effect = attack.onHitMaximumHpSave;
      if (!effect || target.state.is_dead || !target.state.is_alive) return null;
      if (!Number.isInteger(damageTaken) || damageTaken < 0) {
        throw new Error("Damage taken cannot be negative for a maximum-HP reduction rider.");
      }
      const save = window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
        target.state, effect.saveAbility, effect.dc,
      );
      let reductionApplied = 0;
      let killedByZeroMaximum = false;
      if (!save.succeeded && effect.reduction === "damage_taken" && damageTaken) {
        reductionApplied = applyReduction(target.state, damageTaken, {
          zeroMaxHpKills: Boolean(effect.zeroMaxHpKills),
        });
        killedByZeroMaximum = Boolean(target.state.is_dead);
      }
      return {
        saveRoll: save.roll,
        saveAbility: effect.saveAbility,
        saveDc: effect.dc,
        saveSucceeded: save.succeeded,
        reductionApplied,
        killedByZeroMaximum,
      };
    } catch (error) {
      console.error("On-hit maximum-HP save failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAXIMUM_HP = { applyReduction, resolve };
})();
