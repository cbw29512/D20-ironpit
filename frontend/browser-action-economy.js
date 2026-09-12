(() => {
  "use strict";

  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => Boolean(state.is_unconscious),
  };

  function available(state, cost) {
    if (state.is_dead || Q().incapacitated(state)) return false;
    if (state.turn_terminated && cost !== "reaction") return false;
    if (cost === "action") return Boolean(state.action_available);
    if (cost === "bonus_action") return Boolean(state.bonus_action_available);
    if (cost === "reaction") return Boolean(state.reaction_available);
    throw new Error(`Unknown action cost: ${cost}`);
  }

  function spend(state, cost) {
    if (!available(state, cost)) throw new Error(`${cost} is not available.`);
    if (cost === "action") state.action_available = false;
    else if (cost === "bonus_action") state.bonus_action_available = false;
    else state.reaction_available = false;
  }

  function startTurnRecharges(sequence, round, member) {
    const events = [];
    for (const definition of member.state.template.resource_definitions || []) {
      const rule = definition.recharge;
      const current = member.state.resources?.[definition.id];
      if (!rule || current == null || current >= definition.maxUses) continue;
      const rolled = window.IRON_PIT_DICE.roll(rule.dieSize);
      const recovered = rolled >= rule.minimumRoll;
      if (recovered) member.state.resources[definition.id] = definition.maxUses;
      const threshold = rule.minimumRoll === rule.dieSize ? `${rule.minimumRoll}` : `${rule.minimumRoll}-${rule.dieSize}`;
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        feature_id: definition.id,
        resource_roll: { notation: `1d${rule.dieSize}`, rolls: [rolled], selected_roll: rolled, modifier: 0, mode: "normal", total: rolled },
        resource_remaining: member.state.resources[definition.id], animation: "recharge",
        description: `${member.state.template.name} rolls ${rolled} for ${definition.name} (Recharge ${threshold}): ${recovered ? "RECHARGED" : "not recharged"}.`,
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_ACTION_ECONOMY = {
    available, isIncapacitated: (state) => Q().incapacitated(state), spend, startTurnRecharges,
  };
})();
