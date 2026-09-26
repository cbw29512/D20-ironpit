(() => {
  "use strict";

  const CATEGORIES = Object.freeze({
    REPLACEMENT_FORM_SETUP: "replacement-form-setup",
    SPELL_OFFENSE: "spell-offense",
    INTIMIDATING_PRESENCE_2014: "intimidating-presence-2014",
    DEFERRED_EFFECT: "deferred-effect",
    AREA_WEAPON_ATTACK: "area-weapon-attack",
    ATTACK_ACTION: "attack-action",
    AREA_SAVE: "area-save",
    SAVE_ACTION: "save-action",
    STANDARD_ATTACK: "standard-attack",
    DODGE: "dodge",
  });

  const PROFILES = Object.freeze({
    normalPreMove: Object.freeze([CATEGORIES.REPLACEMENT_FORM_SETUP, CATEGORIES.SPELL_OFFENSE]),
    normalPostMove: Object.freeze([
      CATEGORIES.REPLACEMENT_FORM_SETUP,
      CATEGORIES.SPELL_OFFENSE,
      CATEGORIES.INTIMIDATING_PRESENCE_2014,
      CATEGORIES.DEFERRED_EFFECT,
      CATEGORIES.AREA_WEAPON_ATTACK,
      CATEGORIES.ATTACK_ACTION,
      CATEGORIES.AREA_SAVE,
      CATEGORIES.SAVE_ACTION,
      CATEGORIES.STANDARD_ATTACK,
      CATEGORIES.DODGE,
    ]),
    actionSurgeAttack: Object.freeze([
      CATEGORIES.AREA_WEAPON_ATTACK,
      CATEGORIES.ATTACK_ACTION,
      CATEGORIES.STANDARD_ATTACK,
    ]),
  });

  window.IRON_PIT_BROWSER_MAIN_ACTION_PROFILES = { CATEGORIES, PROFILES };
})();
