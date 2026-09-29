(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(sequence, round, source, triggeringEvent, appliedDamage) {
    try {
      const rule = source?.state?.template?.source_damage_temporary_hp;
      if (!rule || appliedDamage <= 0) return { events: [], sequence };
      if (triggeringEvent.actor_id !== source.combatant_id) {
        throw new Error("Damage-triggered Temporary HP source must match the event actor.");
      }
      if (!(rule.trigger_action_ids || []).includes(triggeringEvent.feature_id)) {
        return { events: [], sequence };
      }

      const scores = source.state.template.ability_scores;
      const score = scores?.[rule.ability];
      if (!Number.isFinite(score)) {
        throw new Error("Damage-triggered Temporary HP ability score is unavailable.");
      }
      const modifier = Math.floor((score - 10) / 2);
      const amount = Math.max(
        rule.minimum || 0,
        (rule.flat_bonus || 0) + (rule.ability_multiplier || 1) * modifier,
      );
      if (amount <= 0) return { events: [], sequence };

      const stateRuntime = S();
      if (!stateRuntime?.grantTemporaryHp) {
        throw new Error("Browser Temporary HP runtime is not loaded.");
      }
      const before = source.state.temporary_hp || 0;
      const after = stateRuntime.grantTemporaryHp(source.state, amount);
      return {
        events: [{
          sequence,
          round_number: round,
          event_type: "feature",
          actor_id: source.combatant_id,
          actor_name: source.state.template.name,
          target_id: source.combatant_id,
          target_name: source.state.template.name,
          hp_before: source.state.current_hp,
          hp_after: source.state.current_hp,
          temporary_hp_before: before,
          temporary_hp_after: after,
          feature_id: rule.source_id,
          animation: "feature",
          description: `${source.state.template.name} gains ${amount} Temporary HP from ${rule.source_name} after dealing damage.`,
        }],
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Browser source damage Temporary HP trigger failed", {
        source: source?.combatant_id,
        eventSequence: triggeringEvent?.sequence,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SOURCE_DAMAGE_TRIGGERS = { resolve };
})();
