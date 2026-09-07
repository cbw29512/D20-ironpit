(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(state, damageTaken, damageTypes = [], critical = false) {
    if (!state.template.traits?.includes("undead-fortitude")) return false;
    if (critical || damageTypes.includes("radiant")) return false;
    const bonus = state.template.saving_throw_bonuses?.constitution;
    if (!Number.isInteger(bonus)) throw new Error(`${state.template.name} lacks a Constitution saving throw bonus.`);
    const dc = 5 + damageTaken;
    if (R().d20(bonus).total < dc) return false;
    S().setPositiveHitPoints(state, 1);
    return true;
  }

  window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE = { resolve };
})();
