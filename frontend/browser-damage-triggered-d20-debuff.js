(() => {
  "use strict";

  const key = (value) => String(value ?? "").toLowerCase();

  function appliedDamageOfType(amount, damageTypes = [], damageComponents = [], triggerDamageType) {
    const wanted = key(triggerDamageType);
    const components = [...(damageComponents || [])];
    if (components.length) {
      return components
        .filter((part) => key(part.damage_type) === wanted)
        .reduce((sum, part) => sum + Math.max(0, Number(part.applied_total || 0)), 0);
    }
    const present = new Set((damageTypes || []).map(key));
    if (!present.has(wanted)) return 0;
    if (present.size !== 1) throw new Error("Multi-type damage triggers require applied damage components.");
    return Math.max(0, Number(amount || 0));
  }

  function apply(state, amount, damageTypes = [], damageComponents = []) {
    try {
      const applied = [];
      state.active_damage_triggered_d20_debuffs ||= [];
      for (const rule of state.template.damage_triggered_d20_debuffs || []) {
        const typed = appliedDamageOfType(
          amount, damageTypes, damageComponents, rule.triggerDamageType,
        );
        if (typed < (rule.triggerDamageMinimum || 1)) continue;
        const active = {
          sourceId: rule.sourceId,
          sourceName: rule.sourceName,
          attackRollDisadvantage: Boolean(rule.attackRollDisadvantage),
          abilityCheckDisadvantage: Boolean(rule.abilityCheckDisadvantage),
          expiresAfterTargetTurnCount: (state.turns_started_count || 0) + (rule.durationTargetTurns || 1),
        };
        state.active_damage_triggered_d20_debuffs =
          state.active_damage_triggered_d20_debuffs.filter((item) => item.sourceId !== rule.sourceId);
        state.active_damage_triggered_d20_debuffs.push(active);
        applied.push(rule.sourceName);
      }
      return applied;
    } catch (error) {
      console.error("Browser damage-triggered D20 debuff activation failed.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function attackDisadvantage(state) {
    try {
      return (state.active_damage_triggered_d20_debuffs || [])
        .filter((item) => item.attackRollDisadvantage).length;
    } catch (error) {
      console.error("Browser damage-triggered attack Disadvantage lookup failed.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function abilityCheckDisadvantage(state) {
    try {
      return (state.active_damage_triggered_d20_debuffs || [])
        .filter((item) => item.abilityCheckDisadvantage).length;
    } catch (error) {
      console.error("Browser damage-triggered ability-check Disadvantage lookup failed.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  function expireTargetTurn(state) {
    try {
      const active = state.active_damage_triggered_d20_debuffs || [];
      const expired = active
        .filter((item) => (state.turns_started_count || 0) >= item.expiresAfterTargetTurnCount)
        .map((item) => item.sourceName);
      state.active_damage_triggered_d20_debuffs = active
        .filter((item) => (state.turns_started_count || 0) < item.expiresAfterTargetTurnCount);
      return expired;
    } catch (error) {
      console.error("Browser damage-triggered D20 debuff expiry failed.", {
        combatant: state?.template?.name, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_TRIGGERED_D20_DEBUFF = {
    abilityCheckDisadvantage, apply, attackDisadvantage, expireTargetTurn,
  };
})();
