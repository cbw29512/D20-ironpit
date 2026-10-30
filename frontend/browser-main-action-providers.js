(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const DG = () => window.IRON_PIT_BROWSER_DODGE;
  const CORE = () => window.IRON_PIT_BROWSER_MAIN_ACTION_CORE_PROVIDERS;
  const OFF = () => window.IRON_PIT_BROWSER_MAIN_ACTION_OFFENSE_PROVIDERS;
  const BOTH = Object.freeze(["2014", "2024"]);

  function register(descriptor) {
    try {
      S().registerProvider(descriptor);
    } catch (error) {
      console.error("Failed browser Main Action provider registration", {
        provider: descriptor?.id, error,
      });
      throw error;
    }
  }

  function install() {
    try {
      if (!S()) {
        throw new Error(
          "Main Action provider installation requires browser-main-action-selection.js.",
        );
      }
      if (!CORE()?.install || !OFF()?.install) {
        throw new Error("Split Main Action provider modules are not loaded.");
      }
      CORE().install();
      OFF().install();
      window.IRON_PIT_BROWSER_HP_THRESHOLD_INSTANT_DEATH?.installProvider();
      window.IRON_PIT_BROWSER_HP_THRESHOLD_CONDITION?.installProvider();
      register({
        id: "dodge", category: S().CATEGORIES.DODGE, rulesets: BOTH,
        discover: ({ member }) => E().available(member.state, "action")
          ? { payload: { delivery: "dodge", expectedDamage: 0 } } : null,
        resolve: ({ sequence, round, member }) => ({
          events: [DG().take(sequence, round, member)], sequence: sequence + 1,
        }),
      });
    } catch (error) {
      console.error("Failed browser Main Action provider installation", { error });
      throw error;
    }
  }

  install();
  window.IRON_PIT_BROWSER_MAIN_ACTION_PROVIDERS = {
    install,
    saveChoice: (...args) => OFF().saveChoice(...args),
    printedSave: (...args) => OFF().printedSave(...args),
  };
})();
