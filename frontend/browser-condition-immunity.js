(() => {
  "use strict";

  function immune(state, conditionId) {
    if (state.template.condition_immunities?.includes(conditionId) === true) return true;
    if (state.template.mindless_rage && state.active_effect_ids.includes("rage")
        && ["charmed", "frightened"].includes(conditionId)) return true;
    if (conditionId === "poisoned") {
      const active = [...(state.active_effect_ids || []), ...(state.active_buff_effect_ids || [])];
      return active.includes("petrified") || active.includes("protection-from-poison");
    }
    return false;
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
