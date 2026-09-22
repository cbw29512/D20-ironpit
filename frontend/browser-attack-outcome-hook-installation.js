(() => {
  "use strict";

  function install() {
    const installers = [
      ["Graze", window.IRON_PIT_BROWSER_GRAZE?.installAbilityHooks],
      ["Studied Attacks", window.IRON_PIT_BROWSER_STUDIED_ATTACKS?.installAbilityHooks],
      ["Sap", window.IRON_PIT_BROWSER_SAP?.installAbilityHooks],
      ["Topple", window.IRON_PIT_BROWSER_TOPPLE?.installAbilityHooks],
      ["Vex", window.IRON_PIT_BROWSER_VEX?.installAbilityHooks],
      ["Deferred save effect", window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT?.installAbilityHooks],
    ];
    for (const [name, installer] of installers) {
      if (typeof installer !== "function") throw new Error(`${name} attack-outcome hook installer is not loaded.`);
      installer();
    }
  }

  install();
  window.IRON_PIT_BROWSER_ATTACK_OUTCOME_HOOK_INSTALLATION = { install };
})();
