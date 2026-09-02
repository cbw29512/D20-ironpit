(() => {
  "use strict";

  function active(attacker, attack) {
    return attack.masteryProperty === "Graze"
      && (attacker.template.weapon_masteries || []).includes(attack.weaponId);
  }

  function rawDamage(attacker, attack) {
    try {
      if (!active(attacker, attack)) return null;
      const modifier = attack.attackAbilityModifier;
      if (!Number.isInteger(modifier)) {
        throw new Error(`Graze attack ${attack.id || attack.name} requires an explicit attack ability modifier.`);
      }
      return Math.max(0, modifier);
    } catch (error) {
      console.error("Graze mastery resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRAZE = { active, rawDamage };
})();
