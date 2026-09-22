(() => {
  "use strict";

  function install() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Before-attack-roll installation requires browser-ability-hooks.js.");
    if (!window.IRON_PIT_BROWSER_ATTACK_ROLL_CONTEXT) {
      throw new Error("Before-attack-roll installation requires browser-attack-roll-context.js.");
    }
    const installers = [
      ["Reckless Attack", window.IRON_PIT_BROWSER_BARBARIAN2?.installAbilityHooks],
      ["Sap", window.IRON_PIT_BROWSER_SAP?.installAbilityHooks],
      ["Brutal Strike", window.IRON_PIT_BROWSER_BRUTAL_STRIKE?.installAbilityHooks],
      ["Bloodied Fury", window.IRON_PIT_BROWSER_BLOODIED_FURY?.installAbilityHooks],
    ];
    for (const [name, abilityInstaller] of installers) {
      if (typeof abilityInstaller !== "function") {
        throw new Error(`${name} before-attack-roll hook installer is not loaded.`);
      }
      abilityInstaller();
    }
    const installed = new Set(
      hooks.abilitiesFor(hooks.PHASES.BEFORE_ATTACK_ROLL).map((item) => item.id),
    );
    for (const id of ["reckless-attack", "sap-disadvantage", "brutal-strike", "bloodied-fury"]) {
      if (!installed.has(id)) throw new Error(`Before-attack-roll hook "${id}" is not installed.`);
    }
  }

  install();
  window.IRON_PIT_BROWSER_ATTACK_ROLL_HOOK_INSTALLATION = { install };
})();