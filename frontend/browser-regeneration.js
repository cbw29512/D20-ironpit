(() => {
  "use strict";

  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;

  function apply(state) {
    const trait = state.template.regeneration;
    if (!trait) return { healed: 0, died: false, suppressed: false };
    const taken = new Set(state.damage_types_taken_since_regen || []);
    state.damage_types_taken_since_regen = [];
    const suppressed = (trait.suppressed_by_damage_types || []).some((item) => taken.has(String(item)));
    if (suppressed || (trait.requires_positive_hp && state.current_hp <= 0)) {
      if (trait.survives_zero_until_turn && state.current_hp <= 0 && !state.is_dead) {
        state.current_hp = 0;
        state.is_alive = false;
        state.is_dead = true;
        state.is_unconscious = false;
        state.is_stable = false;
        return { healed: 0, died: true, suppressed };
      }
      return { healed: 0, died: false, suppressed };
    }
    const before = state.current_hp;
    if (typeof Z().restoreHitPoints === "function") {
      Z().restoreHitPoints(state, trait.amount);
    } else {
      if (state.is_dead || trait.amount <= 0) return { healed: 0, died: false, suppressed: false };
      const maximum = window.IRON_PIT_BROWSER_STATE.effectiveMaxHp(state);
      state.current_hp = Math.min(maximum, state.current_hp + trait.amount);
      if (state.current_hp > before) {
        state.is_alive = true;
        state.is_unconscious = false;
        state.is_stable = false;
        state.death_save_successes = 0;
        state.death_save_failures = 0;
      }
    }
    return { healed: state.current_hp - before, died: false, suppressed: false };
  }

  function resolve(sequence, round, member) {
    try {
      const trait = member.state.template.regeneration;
      if (!trait) return { events: [], sequence };
      const hpBefore = member.state.current_hp;
      const result = apply(member.state);
      let description = "";
      if (result.died) {
        description = `${member.state.template.name} starts the turn at 0 HP without ${trait.source_name || "Regeneration"} and dies.`;
      } else if (result.suppressed) {
        description = `${member.state.template.name}'s ${trait.source_name || "Regeneration"} does not function this turn.`;
      } else if (result.healed) {
        description = `${member.state.template.name} regains ${result.healed} hit points from ${trait.source_name || "Regeneration"}.`;
      } else {
        return { events: [], sequence };
      }
      return {
        events: [{
          sequence, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          feature_id: String(trait.source_name || "Regeneration").toLowerCase().replaceAll(" ", "-"),
          hp_before: hpBefore, hp_after: member.state.current_hp,
          is_dead: member.state.is_dead, animation: "feature", description,
        }],
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Start-of-turn Regeneration failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REGENERATION = { apply, resolve };
})();
