(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const FORCED_APPROACH_DISTANCE_FT = 5;

  function forcedRetreatActive(state) {
    return (state.timed_effects || []).some((effect) => effect.turn_behavior === "forced_retreat");
  }

  function forcedApproachActive(state) {
    return (state.timed_effects || []).some((effect) => effect.turn_behavior === "forced_approach_source");
  }

  function resolveForcedApproach(sequence, round, member, setup, turnKey) {
    try {
      const effects = (member.state.timed_effects || [])
        .filter((effect) => effect.turn_behavior === "forced_approach_source");
      if (!effects.length) return null;
      const sourceIds = [...new Set(effects.map((effect) => effect.source_id))];
      if (sourceIds.length !== 1) throw new Error("Compelled approach requires exactly one active source.");
      const sources = [...setup.heroes, ...setup.monsters]
        .filter((actor) => actor.combatant_id === sourceIds[0]);
      if (sources.length !== 1) throw new Error("Compelled approach source is not present in the encounter.");
      if (!R()?.moveToward) throw new Error("Browser reaction-aware movement runtime is not loaded.");
      return R().moveToward(
        sequence, round, member, sources[0], setup, FORCED_APPROACH_DISTANCE_FT,
        "speed", { turnKey, compelled: true },
      );
    } catch (error) {
      console.error("Browser compelled approach failed", { combatantId: member?.combatant_id, error });
      throw error;
    }
  }

  function event(sequence, round, member) {
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: member.combatant_id, target_name: member.state.template.name,
      feature_id: "forced-retreat", animation: "forced-retreat",
      description: `${member.state.template.name} spends the turn fleeing; Iron Pit keeps the card in its formation slot.`,
    };
  }

  function apply(targetState, conditionId, sourceId, spellId, saveAbility, saveDc, options = {}) {
    if (!spellId) throw new Error("Ongoing spell control requires a spell id.");
    if (!(saveDc > 0)) throw new Error("Ongoing spell control requires a valid save DC.");
    return T().apply(targetState, conditionId, sourceId, {
      sourceEffectId: spellId, appliedRound: options.appliedRound,
      expiryTiming: options.expiryTiming || null, repeatSaveAbility: saveAbility,
      repeatSaveDc: saveDc, repeatSaveTiming: "target_turn_end",
      allowedRemovalActionIds: options.allowedRemovalActionIds || [],
      turnBehavior: options.turnBehavior || "normal",
    });
  }

  window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = {
    apply, event, forcedApproachActive, forcedRetreatActive, resolveForcedApproach,
  };
})();
