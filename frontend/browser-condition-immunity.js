(() => {
  "use strict";

  function immune(state, conditionId) {
    if (state.template.condition_immunities?.includes(conditionId) === true) return true;
    return conditionId === "poisoned" && state.active_effect_ids.includes("petrified");
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
