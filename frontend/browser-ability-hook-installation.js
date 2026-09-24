(() => {
  "use strict";

  function install() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Ability hook installation requires browser-ability-hooks.js.");

    const installers = [
      ["Rage", window.IRON_PIT_BROWSER_RAGE?.installAbilityHooks],
      ["Support", window.IRON_PIT_BROWSER_SUPPORT?.installAbilityHooks],
      ["Steady Aim", window.IRON_PIT_BROWSER_STATIONARY_ATTACK_ADVANTAGE?.installAbilityHooks],
      ["2014 Monk", window.IRON_PIT_BROWSER_MONK_2014?.installAbilityHooks],
      ["2014 Frenzy", window.IRON_PIT_BROWSER_FRENZY_2014?.installAbilityHooks],
      ["Persistent Spell Attacks", window.IRON_PIT_BROWSER_PERSISTENT_SPELL_ATTACKS?.installAbilityHooks],
    ];
    for (const [name, installer] of installers) {
      if (typeof installer !== "function") throw new Error(`${name} ability hook installer is not loaded.`);
      installer();
    }
  }

  install();
  window.IRON_PIT_BROWSER_ABILITY_HOOK_INSTALLATION = { install };
})();
