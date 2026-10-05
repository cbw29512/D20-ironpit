(() => {
  "use strict";

  function events(sequence, round, member) {
    try {
      const A = window.IRON_PIT_BROWSER_DEBUFF_ANSWERS;
      if (!A) throw new Error("Turn-start condition audit requires browser-debuff-answers.js.");
      const rows = [];
      const state = member.state;
      for (const conditionId of A.activeConditionIds(state)) {
        rows.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: state.template.name,
          applied_condition_ids: [conditionId],
          feature_id: "turn-start-condition",
          animation: "condition",
          description: `${state.template.name} begins the turn ${conditionId}.`,
        });
      }
      for (const conditionId of A.suppressedConditionIds(state)) {
        rows.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: state.template.name,
          feature_id: "turn-start-condition-suppressed",
          animation: "condition-ended",
          description: `${state.template.name} begins the turn with ${conditionId} suppressed by an active buff.`,
        });
      }
      if (A.isBloodied(state)) {
        rows.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: state.template.name,
          feature_id: "turn-start-bloodied",
          animation: "condition",
          description: `${state.template.name} begins the turn Bloodied.`,
        });
      }
      return { events: rows, sequence };
    } catch (error) {
      console.error("Failed browser turn-start condition audit", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN_START_CONDITIONS = { events };
})();
