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

  function resolveTypedDrain(attacker, target, attack, components) {
    try {
      const spec = attack.onHitTypedDrain;
      if (!spec) return null;
      if (!spec.damageType) throw new Error("Typed drain must name a damage component.");
      const amount = (components || []).reduce((sum, part) => {
        const type = part.damageType || part.damage_type;
        const value = part.appliedTotal ?? part.applied_total ?? 0;
        if (!Number.isInteger(value) || value < 0) throw new Error("Invalid typed-damage component.");
        return sum + (type === spec.damageType ? value : 0);
      }, 0);
      if (!amount) return { damageTaken: 0, maximumReduced: 0, healed: 0, killedByZeroMaximum: false };
      const wasDead = Boolean(target.state.is_dead);
      const rawMaximumAfter = target.state.template.max_hp + (target.state.max_hp_bonus || 0)
        - (target.state.hit_point_maximum_reduction || 0) - amount;
      const maximumReduced = spec.reduceTargetMaximumHp
        ? applyReduction(target.state, amount, { zeroMaxHpKills: spec.zeroMaximumHpKills === true }) : 0;
      const heal = window.IRON_PIT_BROWSER_HEALING?.restore;
      if (spec.healAttacker && !heal) throw new Error("Typed damage self-healing requires shared healing runtime.");
      const healed = spec.healAttacker ? heal(attacker.state, amount) : 0;
      return { damageTaken: amount, maximumReduced, healed,
        killedByZeroMaximum: Boolean(spec.zeroMaximumHpKills && !wasDead
          && maximumReduced > 0 && rawMaximumAfter <= 0 && target.state.is_dead) };
    } catch (error) {
      console.error("Typed on-hit HP transfer failed.", { attack: attack?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAXIMUM_HP = { applyReduction, resolve, resolveTypedDrain };
})();
