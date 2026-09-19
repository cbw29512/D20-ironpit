(() => {
  "use strict";

  const MA = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function available(state, turnKey) {
    return (state.resources["action-surge"] || 0) > 0
      && !state.action_available
      && !state.turn_terminated
      && !state.is_dead
      && !Q().incapacitated(state)
      && state.feature_last_turn_keys["action-surge"] !== turnKey;
  }
  function use(sequence, round, member, turnKey) {
    if (!available(member.state, turnKey)) throw new Error("Action Surge is unavailable.");
    member.state.resources["action-surge"] -= 1;
    member.state.action_available = true;
    member.state.feature_last_turn_keys["action-surge"] = turnKey;
    return {
      sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, feature_id: "action-surge",
      resource_remaining: member.state.resources["action-surge"], animation: "action-surge",
      description: `${member.state.template.name} uses Action Surge and gains one additional Action.`,
    };
  }
  function resolveAttack(sequence, round, member, setup, turnKey) {
    if (!available(member.state, turnKey)) return null;
    const selector = MA();
    if (!selector) throw new Error("Action Surge requires the Main Action selector.");
    const context = { sequence, round, member, setup, turnKey };
    const candidates = selector.discoverCandidates("actionSurgeAttack", context);
    const selected = selector.selectCandidate("actionSurgeAttack", candidates);
    if (!selected) return null;

    const events = [use(sequence++, round, member, turnKey)];
    const resolved = selector.resolveCandidate("actionSurgeAttack", selected, {
      ...context,
      sequence,
    });
    events.push(...resolved.events);
    return { events, sequence: resolved.sequence };
  }

  window.IRON_PIT_BROWSER_ACTION_SURGE = { available, resolveAttack, use };
})();