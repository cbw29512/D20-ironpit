(() => {
  "use strict";

  function mastered(state, attack) {
    return Boolean(attack?.weaponId)
      && (state?.template?.weapon_masteries || []).includes(attack.weaponId);
  }

  function active(state, attack, masteryProperty) {
    return attack?.masteryProperty === masteryProperty && mastered(state, attack);
  }

  window.IRON_PIT_BROWSER_WEAPON_MASTERY = { active, mastered };
})();
