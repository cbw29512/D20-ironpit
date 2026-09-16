(() => {
  "use strict";

  function selectedRuleset(selection) {
    try {
      const ruleset = selection.ruleset || "2024";
      if (!new Set(["2014", "2024"]).has(ruleset)) {
        throw new Error(`Unsupported browser ruleset: ${ruleset}.`);
      }
      return ruleset;
    } catch (error) {
      console.error("Failed to select browser ruleset", { error });
      throw error;
    }
  }

  function rosters(ruleset) {
    try {
      if (ruleset === "2014") {
        const heroes = window.IRON_PIT_BROWSER_HEROES_2014;
        const monsters = window.IRON_PIT_BROWSER_MONSTERS_2014;
        if (window.IRON_PIT_2014_HEROES_READY !== true || !heroes) {
          throw new Error("Certified 2014 browser hero roster is not loaded.");
        }
        if (window.IRON_PIT_2014_MVP_READY !== true || !monsters) {
          throw new Error("Certified 2014 browser monster roster is not loaded.");
        }
        return { heroes, monsters };
      }
      return {
        heroes: window.IRON_PIT_BROWSER_HEROES,
        monsters: window.IRON_PIT_BROWSER_MONSTERS,
      };
    } catch (error) {
      console.error("Failed to resolve browser ruleset rosters", { ruleset, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RULESET_ROSTERS = { selectedRuleset, rosters };
})();
