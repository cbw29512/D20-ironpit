(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_SAVES;

  function resolve(state, damageTaken, damageTypes = [], critical = false, advantageSources = 0) {
    if (!state.template.traits?.includes("undead-fortitude")) return false;
    if (critical || damageTypes.includes("radiant")) return false;
    if (!S()) throw new Error("Browser saving-throw runtime is not loaded.");
    const dc = 5 + damageTaken;
    if (!S().resolveSavingThrow(state, "constitution", dc, false, advantageSources).succeeded) return false;
    state.current_hp = 1;
    state.is_alive = true;
    state.is_dead = false;
    state.is_unconscious = false;
    state.is_stable = false;
    return true;
  }

  window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = { resolve };
})();
