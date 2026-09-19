(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;

  function eventAppliedDamage(event) {
    return Boolean(event?.target_id && event?.damage_roll && event.damage_roll.total > 0);
  }

  function memberById(setup, combatantId) {
    if (!setup || !combatantId) return null;
    return [...setup.heroes, ...setup.monsters]
      .find((member) => member.combatant_id === combatantId) || null;
  }

  function meleeReactionChoice(reactor, source, feature) {
    const distance = F().attackDistance(reactor, source);
    if (distance > feature.max_source_distance_ft) return null;
    const attacks = reactor.state.template.attacks || [];
    for (const attack of attacks) {
      if (attack.kind !== feature.attack_kind) continue;
      if (!F().targetAllowed(reactor, source, attack)) continue;
      if (attack.kind === "melee" && distance <= (attack.reach || 5)) {
        return { attack, distance };
      }
    }
    return null;
  }

  function resolveAfterDamage(sequence, round, source, triggeringEvent, setup, turnKey = null) {
    try {
      if (!eventAppliedDamage(triggeringEvent)) return { events: [], sequence };
      if (!source || triggeringEvent.actor_id !== source.combatant_id) {
        throw new Error("Post-damage reaction source does not match the triggering event actor.");
      }
      const reactor = memberById(setup, triggeringEvent.target_id);
      if (!reactor || reactor.combatant_id === source.combatant_id) return { events: [], sequence };
      const feature = reactor.state.template.damage_triggered_reaction_attack;
      if (!feature || !E().available(reactor.state, "reaction")) return { events: [], sequence };
      if (source.state.is_dead || !source.state.is_alive) return { events: [], sequence };

      const choice = meleeReactionChoice(reactor, source, feature);
      if (!choice) return { events: [], sequence };

      E().spend(reactor.state, "reaction");
      const event = A().resolveAttack(
        sequence, round, reactor, source, choice.attack, choice.distance,
        {
          spendAction: false,
          featureId: feature.source_id,
          setup,
          turnKey,
          offTurn: true,
        },
      );
      const nested = resolveAfterDamage(sequence + 1, round, reactor, event, setup, turnKey);
      return { events: [event, ...nested.events], sequence: nested.sequence };
    } catch (error) {
      console.error("Post-damage reaction dispatch failed", {
        source: source?.combatant_id,
        target: triggeringEvent?.target_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_REACTIONS = {
    eventAppliedDamage,
    resolveAfterDamage,
  };
})();
