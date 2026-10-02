(() => {
  "use strict";

  function install() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Ability hook installation requires browser-ability-hooks.js.");

    const installers = [
      ["Rage", window.IRON_PIT_BROWSER_RAGE?.installAbilityHooks],
      ["Support", window.IRON_PIT_BROWSER_SUPPORT?.installAbilityHooks],
      ["Start-turn Timed Self Buffs", window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS?.installAbilityHooks],
      ["Resource Conversion", window.IRON_PIT_BROWSER_RESOURCE_CONVERSION?.installAbilityHooks],
      ["Steady Aim", window.IRON_PIT_BROWSER_STATIONARY_ATTACK_ADVANTAGE?.installAbilityHooks],
      ["Bonus Attacks", window.IRON_PIT_BROWSER_BONUS_ATTACKS?.installAbilityHooks],
      ["Tactical Actions", window.IRON_PIT_BROWSER_TACTICAL_ACTIONS?.installAbilityHooks],
      ["2014 Monk", window.IRON_PIT_BROWSER_MONK_2014?.installAbilityHooks],
      ["2014 Frenzy", window.IRON_PIT_BROWSER_FRENZY_2014?.installAbilityHooks],
      ["Targeted Concentration Damage", window.IRON_PIT_BROWSER_TARGETED_CONCENTRATION_DAMAGE?.installAbilityHooks],
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
