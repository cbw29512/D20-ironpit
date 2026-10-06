(() => {
  "use strict";

  function limitsOf(effect) {
    return effect && effect.control_limits ? effect.control_limits : null;
  }

  function speedMultiplier(state) {
    try {
      return (state.timed_effects || []).reduce((value, effect) => {
        const limits = limitsOf(effect);
        return value * (limits && limits.speed_multiplier != null ? limits.speed_multiplier : 1);
      }, 1);
    } catch (error) {
      console.error("Timed speed multiplier lookup failed.", error);
      throw error;
    }
  }

  function actionBonusExclusive(state) {
    return (state.timed_effects || []).some((effect) => Boolean(limitsOf(effect)?.action_bonus_exclusive));
  }

  function maxAttacksPerTurn(state) {
    const caps = (state.timed_effects || [])
      .map((effect) => limitsOf(effect)?.max_attacks_per_turn)
      .filter((value) => Number.isInteger(value));
    return caps.length ? Math.min(...caps) : null;
  }

  function turnAttackAllowed(state, offTurn = false) {
    try {
      if (offTurn) return true;
      const cap = maxAttacksPerTurn(state);
      if (cap == null) return true;
      return (state.attacks_this_turn || 0) < cap;
    } catch (error) {
      console.error("Timed attack-cap lookup failed.", error);
      throw error;
    }
  }

  function registerTurnAttack(state, offTurn = false) {
    try {
      if (offTurn) return;
      if (!turnAttackAllowed(state, false)) {
        throw new Error(`${state.template?.name || "Combatant"} cannot make another attack this turn.`);
      }
      state.attacks_this_turn = (state.attacks_this_turn || 0) + 1;
    } catch (error) {
      console.error("Timed attack registration failed.", error);
      throw error;
    }
  }

  function armorClassBonus(state) {
    try {
      return (state.timed_effects || []).reduce((sum, effect) => sum + (limitsOf(effect)?.armor_class_bonus || 0), 0);
    } catch (error) {
      console.error("Timed armor-class bonus lookup failed.", error);
      throw error;
    }
  }

  function savingThrowFlat(state, ability) {
    try {
      const wanted = String(ability || "").trim().toLowerCase();
      return (state.timed_effects || []).reduce((sum, effect) => {
        const bonuses = limitsOf(effect)?.saving_throw_flat_bonuses || [];
        return sum + bonuses.reduce((inner, bonus) => {
          if (wanted && bonus.ability !== wanted) return inner;
          return inner + (bonus.flat_bonus || 0);
        }, 0);
      }, 0);
    } catch (error) {
      console.error("Timed saving-throw flat lookup failed.", { ability, error });
      throw error;
    }
  }

  function abilityD20Disadvantage(state, ability) {
    try {
      const wanted = String(ability || "").trim().toLowerCase();
      if (!wanted) return 0;
      return (state.timed_effects || []).filter((effect) => {
        const abilities = limitsOf(effect)?.d20_disadvantage_abilities || [];
        return abilities.includes(wanted);
      }).length;
    } catch (error) {
      console.error("Timed ability D20 Disadvantage lookup failed.", { ability, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TIMED_CONTROL = {
    abilityD20Disadvantage, actionBonusExclusive, armorClassBonus, maxAttacksPerTurn,
    registerTurnAttack, savingThrowFlat, speedMultiplier, turnAttackAllowed,
  };
})();
