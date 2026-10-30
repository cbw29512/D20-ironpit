(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function expire(state, event, states = []) {
    if (!["attack", "spell_cast"].includes(event)) throw new Error(`Unknown owner expiry event: ${event}.`);
    const flag = event === "attack" ? "ends_on_owner_attack" : "ends_on_owner_spell_cast";
    const removed = [];
    for (const effect of [...(state.timed_effects || [])]) {
      if (!(state.timed_effects || []).includes(effect) || !effect[flag]) continue;
      const concentration = state.concentration;
      let ids;
      if (concentration
        && concentration.effect_id === effect.source_effect_id
        && concentration.source_id === effect.source_id) {
        ids = (state.timed_effects || [])
          .filter((item) => item.source_id === concentration.source_id
            && item.source_effect_id === concentration.effect_id)
          .map((item) => item.effect_id);
        C().end(state, states);
      } else {
        ids = T().removeGroup(state, effect);
      }
      for (const id of ids) if (!removed.includes(id)) removed.push(id);
    }
    return removed;
  }

  window.IRON_PIT_BROWSER_OWNER_ACTION_EXPIRY = { expire };
})();
