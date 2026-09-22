(() => {
  "use strict";

  const FEATURE_ID = "miss-to-hit-once-per-turn";

  function active(state) {
    return Boolean(state?.template?.miss_to_hit_once_per_turn);
  }

  function resolve(state, hit, turnKey) {
    try {
      if (hit || !active(state)) return { hit: Boolean(hit), used: false };
      if (!turnKey) return { hit: false, used: false };
      state.feature_last_turn_keys ||= {};
      if (state.feature_last_turn_keys[FEATURE_ID] === turnKey) {
        return { hit: false, used: false };
      }
      state.feature_last_turn_keys[FEATURE_ID] = turnKey;
      return { hit: true, used: true };
    } catch (error) {
      console.error("[Iron Pit] miss-to-hit resolution failed", error);
      return { hit: Boolean(hit), used: false };
    }
  }

  window.IRON_PIT_BROWSER_MISS_TO_HIT = { FEATURE_ID, active, resolve };
})();
