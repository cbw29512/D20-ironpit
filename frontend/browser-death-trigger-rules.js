(() => {
  "use strict";
  const BUFF = "death-trigger";
  function ready(state) {
    return Boolean(state?.is_dead && (state.active_buff_effect_ids || []).includes(BUFF)
      && !(state.feature_use_counts || {})[BUFF]);
  }
  function consume(state) {
    if (!ready(state)) return false;
    state.feature_use_counts = state.feature_use_counts || {};
    state.feature_use_counts[BUFF] = 1;
    return true;
  }
  window.IRON_PIT_BROWSER_DEATH_TRIGGER_RULES = { ready, consume, BUFF };
})();
