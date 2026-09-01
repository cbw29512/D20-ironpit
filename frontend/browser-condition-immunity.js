(() => {
  "use strict";

  function immune(state, conditionId) {
    if (state.template.condition_immunities?.includes(conditionId) === true) return true;
    if (state.template.mindless_rage && state.active_effect_ids.includes("rage")
        && ["charmed", "frightened"].includes(conditionId)) return true;
    return conditionId === "poisoned" && state.active_effect_ids.includes("petrified");
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
