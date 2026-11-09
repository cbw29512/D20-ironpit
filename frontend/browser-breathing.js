(() => {
  "use strict";

  // Immutable card: ruleset, Constitution, special Hold Breath, and needs_air.
  // Mutable state: two countdowns and a post-zero recovery lock per fight.
  function unable(state) {
    return state.template.needs_air !== false
      && (state.grapple_sources || []).some((source) => source.prevents_breathing);
  }

  function reset(state) {
    state.breath_hold_rounds_remaining = null;
    state.breath_survival_rounds_remaining = null;
    state.suffocating_at_zero = false;
  }

  function blocksRecovery(state) {
    return Boolean(state.suffocating_at_zero && unable(state));
  }

  function budget(state) {
    const scores = state.template.ability_scores;
    const con = scores?.constitution;
    if (!Number.isInteger(con) || con < 1 || con > 30) {
      throw new Error(`${state.template.name}: suffocation requires a certified Constitution score.`);
    }
    const modifier = Math.floor((con - 10) / 2);
    const override = state.template.breath_hold_rounds;
    if (override != null && (!Number.isInteger(override) || override < 1)) {
      throw new Error(`${state.template.name}: invalid source Hold Breath duration.`);
    }
    return {
      hold: override == null ? Math.max(5, (1 + modifier) * 10) : override,
      survival: Math.max(1, modifier),
    };
  }

  function sourceName(state, setup) {
    const source = state.grapple_sources.find((item) => item.prevents_breathing);
    const owner = [...setup.heroes, ...setup.monsters].find((item) =>
      item.combatant_id === source.source_id);
    const action = (owner?.state?.template?.saving_throw_actions || []).find((item) =>
      item.id === source.linked_effect_id);
    return action?.name || source.linked_effect_id || "Grapple";
  }

  function startTurn(sequence, round, member, setup) {
    const state = member.state;
    try {
      if (!unable(state)) {
        reset(state);
        return { events: [], sequence };
      }
      if (state.template.ruleset !== "2014") {
        throw new Error("2024 suffocation requires its separate exhaustion lifecycle.");
      }
      if (state.is_dead || state.suffocating_at_zero) return { events: [], sequence };
      if (state.breath_hold_rounds_remaining == null) {
        const time = budget(state);
        state.breath_hold_rounds_remaining = time.hold;
        state.breath_survival_rounds_remaining = time.survival;
      }
      let description = "";
      if (state.breath_hold_rounds_remaining > 0) {
        state.breath_hold_rounds_remaining -= 1;
        if (state.breath_hold_rounds_remaining > 0) return { events: [], sequence };
        description = `${state.template.name} exhausts held breath while caught in ${sourceName(state, setup)}.`;
      } else if (state.breath_survival_rounds_remaining > 0) {
        state.breath_survival_rounds_remaining -= 1;
        return { events: [], sequence };
      } else {
        const before = state.current_hp;
        const zero = window.IRON_PIT_BROWSER_ZERO_HP;
        if (!zero?.reduceToZero) throw new Error("Suffocation requires browser zero-HP runtime.");
        const outcome = zero.reduceToZero(state, [...setup.heroes, ...setup.monsters].map((m) => m.state));
        if (state.current_hp === 0 && !state.is_dead) {
          state.is_stable = false;
          state.is_unconscious = true;
          state.suffocating_at_zero = true;
        }
        description = `${state.template.name} suffocates under ${sourceName(state, setup)}: ${before} to ${state.current_hp} HP (${outcome}).`;
      }
      return { events: [{
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: state.template.name,
        target_id: member.combatant_id, target_name: state.template.name,
        feature_id: "suffocation", animation: "condition",
        description, hp_after: state.current_hp,
      }], sequence: sequence + 1 };
    } catch (error) {
      console.error("Browser 2014 breathing turn failed", {
        combatant: member?.combatant_id, round, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BREATHING = { unable, reset, blocksRecovery, startTurn };
})();
