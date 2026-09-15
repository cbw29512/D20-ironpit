(() => {
  "use strict";

  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;
  const D = () => window.IRON_PIT_DICE;

  function resolveStartTurn(sequence, round, member) {
    try {
      if (!RES()) throw new Error("Browser resource API is not loaded.");
      if (!D()) throw new Error("Browser dice provider is not loaded.");
      const events = [];
      const definitions = member.state.template.resourceDefinitions || {};
      for (const [resourceId, definition] of Object.entries(definitions)) {
        const recharge = definition.recharge;
        if (!recharge) continue;
        if (recharge.trigger !== "start_of_turn") {
          throw new Error(`Unsupported recharge trigger ${recharge.trigger}.`);
        }
        const before = RES().current(member.state, resourceId);
        if (before >= definition.maxUses) continue;
        const rolled = D().roll(recharge.dieSize);
        const succeeded = rolled >= recharge.minimumRoll;
        if (succeeded) member.state.resources[resourceId] = definition.maxUses;
        const after = member.state.resources[resourceId];
        const label = recharge.minimumRoll === recharge.dieSize
          ? `Recharge ${recharge.minimumRoll}`
          : `Recharge ${recharge.minimumRoll}-${recharge.dieSize}`;
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          feature_id: `recharge:${resourceId}`,
          resource_roll: {
            notation: `1d${recharge.dieSize}`, rolls: [rolled], selected_roll: rolled,
            modifier: 0, mode: "normal", total: rolled,
          },
          resource_remaining: after, animation: "recharge",
          description: `${member.state.template.name} rolls ${rolled} for ${label}. ${succeeded
            ? `${definition.name} recharges (${before}->${after}).`
            : `${definition.name} remains expended.`}`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser start-turn Recharge", { combatant: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RECHARGE = { resolveStartTurn };
})();
