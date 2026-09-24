(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function memberById(setup, id) {
    try {
      if (!id) return null;
      return [...(setup?.heroes || []), ...(setup?.monsters || [])]
        .find((member) => member.combatant_id === id) || null;
    } catch (error) {
      console.error("Failed browser zero-HP reward target lookup.", { id, error });
      throw error;
    }
  }

  function resolve(sequence, round, source, triggeringEvent, setup) {
    try {
      const grant = source?.state?.template?.zero_hp_temporary_hp_grant;
      if (!grant) return null;
      if (triggeringEvent?.actor_id !== source.combatant_id) {
        throw new Error("Zero-HP reward source must match the triggering event actor.");
      }
      if (!Number.isFinite(triggeringEvent.hp_before) || !Number.isFinite(triggeringEvent.hp_after)) {
        return null;
      }
      if (triggeringEvent.hp_before <= 0 || triggeringEvent.hp_after !== 0) return null;

      const target = memberById(setup, triggeringEvent.target_id);
      if (!target || target.side === source.side) return null;

      const before = source.state.temporary_hp || 0;
      const after = S().grantTemporaryHp(source.state, grant.temporary_hp);
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: source.combatant_id,
        actor_name: source.state.template.name,
        target_id: source.combatant_id,
        target_name: source.state.template.name,
        temporary_hp_before: before,
        temporary_hp_after: after,
        feature_id: grant.source_id,
        animation: "temporary-hp",
        description: `${source.state.template.name}'s ${grant.source_name} grants ${grant.temporary_hp} Temporary HP.`,
      };
    } catch (error) {
      console.error("Browser zero-HP Temporary HP reward failed.", {
        source: source?.combatant_id,
        eventSequence: triggeringEvent?.sequence,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ZERO_HP_REWARDS = { memberById, resolve };
})();
