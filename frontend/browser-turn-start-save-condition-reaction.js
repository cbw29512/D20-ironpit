(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const SAVES = () => window.IRON_PIT_BROWSER_SAVING_THROWS;
  const TIMED = () => window.IRON_PIT_BROWSER_TIMED;
  const IMMUNITY = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;

  function eligible(reactor, target, reaction) {
    if (!E().available(reactor.state, "reaction")) return false;
    if (reactor.side === target.side) return false;
    if (!reactor.state.is_alive || reactor.state.is_dead) return false;
    if (!target.state.is_alive || target.state.is_dead) return false;
    if (!IMMUNITY()?.immune) throw new Error("Universal condition immunity is required for turn-start reactions.");
    if (IMMUNITY().immune(target.state, reaction.conditionId)) return false;
    if (Q().has(target.state, reaction.conditionId)) return false;
    const distance = S().distance(reactor, target);
    if (distance > reaction.rangeFt) return false;
    if (reaction.requiresSourceCanSeeTarget && !Q().canSee(reactor.state, target.state, distance)) return false;
    if (reaction.requiresTargetCanSeeSource && !Q().canSee(target.state, reactor.state, distance)) return false;
    return true;
  }

  function resolve(sequence, round, target, setup) {
    const events = [];
    try {
      const reactors = [...setup.heroes, ...setup.monsters]
        .filter((member) => member.combatant_id !== target.combatant_id);
      for (const reactor of reactors) {
        const reaction = reactor.state.template.turnStartSaveConditionReaction;
        if (!reaction || !eligible(reactor, target, reaction)) continue;
        const resolver = SAVES()?.resolveSavingThrow;
        if (!resolver) throw new Error("Universal saving throws are required for turn-start reactions.");
        E().spend(reactor.state, "reaction");
        const outcome = resolver(target.state, reaction.saveAbility, reaction.saveDc);
        const applied = [];
        if (!outcome.succeeded) {
          if (!TIMED()?.apply) throw new Error("Universal timed conditions are required for turn-start reactions.");
          const conditionApplied = TIMED().apply(
            target.state,
            reaction.conditionId,
            reactor.combatant_id,
            {
              sourceEffectId: reaction.sourceId,
              sourceTemplate: reactor.state.template,
              expiryTiming: reaction.expiryTiming,
              appliedRound: round,
            },
          );
          if (conditionApplied) applied.push(reaction.conditionId);
        }
        events.push({
          sequence,
          round_number: round,
          event_type: "feature",
          actor_id: reactor.combatant_id,
          actor_name: reactor.state.template.name,
          target_id: target.combatant_id,
          target_name: target.state.template.name,
          feature_id: reaction.sourceId,
          save_ability: reaction.saveAbility,
          save_dc: reaction.saveDc,
          saving_throw_roll: outcome.roll,
          save_succeeded: outcome.succeeded,
          applied_condition_ids: applied,
          animation: "fear",
          description: `${reactor.state.template.name} uses ${reaction.sourceName}: ${target.state.template.name} ${outcome.succeeded ? "succeeds" : "fails"} the DC ${reaction.saveDc} ${reaction.saveAbility} save${outcome.succeeded ? "" : " and is Frightened until the end of its turn"}.`,
        });
        sequence += 1;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser turn-start save-condition Reaction failed", { target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_SAVE_CONDITION_REACTION = { resolve, eligible };
})();
