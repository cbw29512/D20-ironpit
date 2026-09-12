(() => {
  "use strict";
  const KEY = "peerless-aim-used";

  function refresh(state) { delete state.feature_last_turn_keys[KEY]; }
  function resolve(state, hit) {
    if (hit || !state.template.peerless_aim || state.feature_last_turn_keys[KEY]) return { hit, used: false };
    state.feature_last_turn_keys[KEY] = "used";
    return { hit: true, used: true };
  }

  window.IRON_PIT_BROWSER_PEERLESS_AIM = { refresh, resolve };
})();
