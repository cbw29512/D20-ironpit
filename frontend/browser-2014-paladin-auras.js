(() => {
  "use strict";

  function sync(setup) {
    try {
      window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS?.sync(setup);
    } catch (error) {
      console.error("Failed to synchronize browser 2014 Paladin auras.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PALADIN_AURAS_2014 = { sync };
})();
