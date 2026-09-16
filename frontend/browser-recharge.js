(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function resolveStartOfTurn(sequence, round, member) {
    try {
      if (!member?.state?.template) throw new Error("Recharge resolution requires a combatant state/template.");
      if (!D()?.roll) throw new Error("Recharge resolution requires the canonical browser dice provider.");
      const events = [];
      const rules = member.state.template.recharge_rules || [];
      for (const rule of rules) {
        const resourceId = rule.resourceId;
        if (!resourceId || !(resourceId in member.state.resources)) {
          throw new Error(`Recharge rule references missing resource: ${resourceId || "<empty>"}.`);
        }
        if (member.state.resources[resourceId] > 0) continue;
        const dieSize = rule.dieSize || 6;
        const roll = D().roll(dieSize);
        const restored = roll >= rule.minimumRoll;
        if (restored) member.state.resources[resourceId] = 1;
        events.push({
          sequence: sequence++, round_number: round, event_type: "recharge",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          resource_id: resourceId, resource_remaining: member.state.resources[resourceId],
          recharge_roll: { notation: `1d${dieSize}`, rolls: [roll], selected_roll: roll, modifier: 0, mode: "normal", total: roll },
          recharge_minimum_roll: rule.minimumRoll, recharge_succeeded: restored,
          description: `${member.state.template.name} rolls ${roll} for Recharge ${rule.minimumRoll}-${dieSize}: ${restored ? "recharged" : "not recharged"}.`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser Recharge start-of-turn resolution", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RECHARGE = { resolveStartOfTurn };
})();