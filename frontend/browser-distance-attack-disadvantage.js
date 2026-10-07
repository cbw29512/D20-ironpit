(() => {
  "use strict";

  function sources(state, distanceFt) {
    try {
      const threshold = Number(state?.template?.attack_disadvantage_beyond_ft || 0);
      return threshold > 0 && Number(distanceFt) > threshold ? 1 : 0;
    } catch (error) {
      console.error("Distance attack Disadvantage resolution failed.", {
        combatant: state?.template?.name, distanceFt, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DISTANCE_ATTACK_DISADVANTAGE = { sources };
})();
