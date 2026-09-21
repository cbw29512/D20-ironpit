(() => {
  "use strict";

  const CATEGORIES = Object.freeze({
    TIMED_SELF_BUFF: "timed-self-buff",
    SPELL_OFFENSE: "spell-offense",
    INTIMIDATING_PRESENCE_2014: "intimidating-presence-2014",
    DEFERRED_EFFECT: "deferred-effect",
    ATTACK_ACTION: "attack-action",
    AREA_SAVE: "area-save",
    SAVE_ACTION: "save-action",
    STANDARD_ATTACK: "standard-attack",
    DODGE: "dodge",
  });

  const PROFILES = Object.freeze({
    normalPreMove: Object.freeze([CATEGORIES.TIMED_SELF_BUFF, CATEGORIES.SPELL_OFFENSE]),
    normalPostMove: Object.freeze([
      CATEGORIES.SPELL_OFFENSE,
      CATEGORIES.INTIMIDATING_PRESENCE_2014,
      CATEGORIES.DEFERRED_EFFECT,
      CATEGORIES.ATTACK_ACTION,
      CATEGORIES.AREA_SAVE,
      CATEGORIES.SAVE_ACTION,
      CATEGORIES.STANDARD_ATTACK,
      CATEGORIES.DODGE,
    ]),
    actionSurgeAttack: Object.freeze([
      CATEGORIES.ATTACK_ACTION,
      CATEGORIES.STANDARD_ATTACK,
    ]),
  });

  window.IRON_PIT_BROWSER_MAIN_ACTION_PROFILES = { CATEGORIES, PROFILES };
})();
