(() => {
  "use strict";

  function immune(state, conditionId) {
    return state.template.condition_immunities?.includes(conditionId) === true;
  }

  window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = { immune };
})();
