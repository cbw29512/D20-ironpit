(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;

  function resolve(state, damageTaken, damageTypes = [], critical = false) {
    if (!state.template.traits?.includes("undead-fortitude")) return false;
    if (critical || damageTypes.includes("radiant")) return false;
    const bonus = state.template.saving_throw_bonuses?.constitution;
    if (!Number.isInteger(bonus)) throw new Error(`${state.template.name} lacks a Constitution saving throw bonus.`);
    const dc = 5 + damageTaken;
    if (R().d20(bonus).total < dc) return false;
    state.current_hp = 1;
    state.is_alive = true;
    state.is_dead = false;
    state.is_unconscious = false;
    state.is_stable = false;
    return true;
  }

  function resolveEffectBound(state) {
    try {
      const rule = state.template.effect_bound_survival_save;
      if (!rule || !state.active_effect_ids.includes(rule.required_effect_id)) return false;
      const saves = window.IRON_PIT_BROWSER_SAVES;
      if (!saves) throw new Error(`${rule.source_id} requires the saving throw runtime.`);
      const uses = state.survival_save_uses[rule.source_id] || 0;
      const dc = rule.initial_dc + uses * rule.dc_increment;
      const { roll, succeeded } = saves.resolveSavingThrow(state, rule.save_ability, dc);
      // Count attempts, including failures; immutable source data never accumulates DC.
      state.survival_save_uses[rule.source_id] = uses + 1;
      if (succeeded) {
        state.current_hp = rule.replacement_hp;
        state.is_alive = true; state.is_dead = false;
        state.is_unconscious = false; state.is_stable = false;
      }
      const evidence = roll ? `rolls [${roll.rolls.join(", ")}], modifier ${roll.modifier}, total ${roll.total}` : "automatic failure";
      state.pending_survival_save_logs.push(`${state.template.name} ${rule.source_id}: DC ${dc} ${rule.save_ability} save; `
        + `${evidence}; ${succeeded ? "succeeds" : "fails"}; HP ${state.current_hp}; next DC ${dc + rule.dc_increment}.`);
      return succeeded;
    } catch (error) {
      console.error("Effect-bound survival save failed", { combatant: state?.template?.id, error });
      throw error;
    }
  }

  function consumeLog(state) {
    try {
      const logs = state.pending_survival_save_logs || [];
      const result = logs.join(" ");
      logs.length = 0;
      return result ? ` ${result}` : "";
    } catch (error) {
      console.error("Survival save audit failed", { combatant: state?.template?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = { resolve, resolveEffectBound, consumeLog };
})();
