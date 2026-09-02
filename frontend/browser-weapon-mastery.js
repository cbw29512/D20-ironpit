(() => {
  "use strict";

  function mastered(state, attack) {
    return Boolean(attack?.weaponId)
      && (state?.template?.weapon_masteries || []).includes(attack.weaponId);
  }

  function active(state, attack, masteryProperty) {
    const replaced = window.IRON_PIT_BROWSER_TACTICAL_MASTER?.selected?.(state, attack) || false;
    return attack?.masteryProperty === masteryProperty && mastered(state, attack) && !replaced;
  }

  window.IRON_PIT_BROWSER_WEAPON_MASTERY = { active, mastered };
})();
