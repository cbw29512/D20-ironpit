(() => {
  "use strict";

  function noteSuppression(state, damageTypes = []) {
    const profile = state.template.regeneration;
    if (!profile || !damageTypes.length) return;
    if ((profile.suppressedByDamageTypes || []).some((type) => damageTypes.includes(type))) {
      state.regeneration_suppressed = true;
    }
  }

  function holdsAtZero(state) {
    return Boolean(state.template.regeneration?.survivesZeroUntilTurn);
  }

  function startTurn(sequence, round, member) {
    const state = member.state, profile = state.template.regeneration;
    if (!profile || state.is_dead) return null;
    const suppressed = Boolean(state.regeneration_suppressed);
    state.regeneration_suppressed = false;
    const hpBefore = state.current_hp;
    if (suppressed || (profile.requiresPositiveHp && hpBefore <= 0)) {
      if (hpBefore <= 0 && profile.survivesZeroUntilTurn) {
        state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false;
        return { event: {
          sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
          actor_name: state.template.name, feature_id: "regeneration", hp_before: 0, hp_after: 0,
          is_dead: true, animation: "regeneration",
          description: `${state.template.name}'s Regeneration is suppressed and it dies at the start of its turn.`,
        }, died: true };
      }
      return null;
    }
    if (hpBefore <= 0 && !profile.survivesZeroUntilTurn) return null;
    const effectiveMax = window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state);
    state.current_hp = Math.min(effectiveMax, hpBefore + profile.amount);
    const healed = state.current_hp - hpBefore;
    if (healed <= 0) return null;
    state.is_alive = true; state.is_dead = false; state.is_unconscious = false; state.is_stable = false;
    state.death_save_successes = 0; state.death_save_failures = 0;
    return { event: {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: state.template.name, feature_id: "regeneration", hp_before: hpBefore,
      hp_after: state.current_hp, is_dead: false, animation: "regeneration",
      description: `${state.template.name} regenerates ${healed} hit point${healed === 1 ? "" : "s"}.`,
    }, died: false };
  }

  window.IRON_PIT_BROWSER_REGENERATION = { holdsAtZero, noteSuppression, startTurn };
})();
