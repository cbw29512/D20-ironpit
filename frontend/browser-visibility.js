(() => {
  "use strict";
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    has: (state, id) => state.active_effect_ids?.includes(id) === true,
  };

  function hasLineOfSight(observer, target, options = {}) {
    if (options.externallyBlocked === true) return false;
    if (Q().has(observer, "blinded")) return false;
    if (Q().has(target, "invisible")) return false;
    if (target.active_buff_effect_ids?.includes("invisibility") === true) return false;
    return true;
  }

  window.IRON_PIT_BROWSER_VISIBILITY = { hasLineOfSight };
})();
