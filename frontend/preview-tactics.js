((root) => {
  "use strict";

  function prepareNimbleRetreat(state, actor, events) {
    try {
      const hasFeature = actor.template.bonus_action_features?.includes("nimble-escape");
      if (!hasFeature || state.distance > 5) return false;

      events.push({
        event_type: "disengage",
        actor_id: actor.template.id,
        feature_id: "nimble-escape",
        animation: "disengage",
        description: `${actor.template.name} uses Nimble Escape to take the Disengage action.`,
      });
      const before = state.distance;
      const moved = actor.template.speed_ft;
      state.distance += moved;
      events.push({
        event_type: "movement",
        actor_id: actor.template.id,
        animation: "retreat",
        description: `${actor.template.name} retreats ${moved} ft.`,
        movement_ft: moved,
        distance_before_ft: before,
        distance_after_ft: state.distance,
      });
      return true;
    } catch (error) {
      console.error("Preview Nimble Escape retreat failed", error);
      throw error;
    }
  }

  const api = { prepareNimbleRetreat };
  root.IRON_PIT_TACTICS = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
