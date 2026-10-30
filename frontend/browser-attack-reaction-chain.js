(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const MAX_DEPTH = 8;

  function memberById(setup, id) {
    try {
      const matches = [...setup.heroes, ...setup.monsters].filter((member) => member.combatant_id === id);
      if (matches.length !== 1) throw new Error("Expected one reaction-chain combatant " + id + ".");
      return matches[0];
    } catch (error) {
      console.error("Failed browser reaction-chain combatant lookup.", { id, error });
      throw error;
    }
  }

  function plan(event, attacker, setup) {
    try {
      if (!event.defensive_reaction_id) return null;
      if (!event.target_id || event.hit !== false) throw new Error("Defensive reaction evidence requires a missed target.");
      const reactor = memberById(setup, event.target_id), rule = reactor.state.template.parry_reaction;
      if (!rule || (rule.source_feature || "parry") !== event.defensive_reaction_id) throw new Error("Defensive reaction evidence does not match runtime state.");
      if (!rule.counterattack_attack_id || reactor.state.is_dead || !reactor.state.is_alive || attacker.state.is_dead || !attacker.state.is_alive) return null;
      const matches = (reactor.state.template.attacks || []).filter((attack) => attack.id === rule.counterattack_attack_id);
      if (matches.length !== 1) throw new Error("Counterattack binding is missing or ambiguous.");
      const attack = matches[0], distance = S().distance(reactor, attacker);
      if (distance > (rule.counterattack_range_ft || 5)) return null;
      const reach = attack.kind === "melee" || attack.kind === "melee_or_ranged" ? (attack.reach || 5) : (attack.longRange || attack.normalRange || 0);
      if (distance > reach) return null;
      return { reactor, attack, distance, rule };
    } catch (error) {
      console.error("Failed browser counterattack planning.", { reaction: event?.defensive_reaction_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, attacker, target, attack, distance, setup, extra = {}, depth = 0) {
    try {
      if (depth > MAX_DEPTH) throw new Error("Maximum browser immediate reaction depth exceeded.");
      const event = A().resolveAttack(sequence++, round, attacker, target, attack, distance, { ...extra, setup });
      const events = [event], counter = plan(event, attacker, setup);
      if (!counter) return { events, sequence };
      const more = resolve(sequence, round, counter.reactor, attacker, counter.attack, counter.distance, setup, {
        spendAction: false, featureId: counter.rule.source_feature || "parry", turnKey: extra.turnKey || null,
        ignoreCloseThreat: false, allowReckless: false, offTurn: true,
      }, depth + 1);
      events.push(...more.events);
      return { events, sequence: more.sequence };
    } catch (error) {
      console.error("Failed browser attack reaction chain.", { attacker: attacker?.combatant_id, target: target?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_REACTION_CHAIN = { resolve };
})();
