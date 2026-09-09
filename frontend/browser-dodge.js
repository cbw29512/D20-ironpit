(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const DODGE_EFFECT_ID = "dodge";

  function benefitsActive(state) {
    try {
      if (!state.active_effect_ids.includes(DODGE_EFFECT_ID)) return false;
      if (Q()?.incapacitated(state)) return false;
      if (G()?.speedIsZero(state)) return false;
      const speed = M()?.effectiveSpeed(state) ?? state.template.speed_ft;
      return speed > 0;
    } catch (error) {
      console.error("Failed to evaluate browser Dodge benefits", { name: state?.template?.name, error });
      throw error;
    }
  }

  function dexSaveAdvantageSources(state, ability) {
    try {
      return ability === "dexterity" && benefitsActive(state) ? 1 : 0;
    } catch (error) {
      console.error("Failed to evaluate browser Dodge save Advantage", { name: state?.template?.name, error });
      throw error;
    }
  }

  function take(sequence, round, actor) {
    try {
      if (!E()?.available(actor.state, "action")) throw new Error("Action is not available for Dodge.");
      E().spend(actor.state, "action");
      if (!actor.state.active_effect_ids.includes(DODGE_EFFECT_ID)) {
        actor.state.active_effect_ids.push(DODGE_EFFECT_ID);
      }
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: actor.combatant_id,
        actor_name: actor.state.template.name,
        applied_condition_ids: [DODGE_EFFECT_ID],
        feature_id: DODGE_EFFECT_ID,
        animation: "dodge",
        description: `${actor.state.template.name} takes the Dodge action.`,
      };
    } catch (error) {
      console.error("Failed to resolve browser Dodge action", { id: actor?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DODGE = { benefitsActive, dexSaveAdvantageSources, take };
})();
