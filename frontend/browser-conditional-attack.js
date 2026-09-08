(() => {
  "use strict";

  function sources(attacker, defender, attack, mode) {
    try {
      void attacker;
      return (attack.conditionalAttackModifiers || []).filter((item) =>
        item.mode === mode
        && item.trigger === "target_missing_hp"
        && defender.current_hp < defender.template.max_hp
      ).length;
    } catch (error) {
      console.error("Conditional attack modifier resolution failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONDITIONAL_ATTACK = {
    advantage: (attacker, defender, attack) => sources(attacker, defender, attack, "advantage"),
    disadvantage: (attacker, defender, attack) => sources(attacker, defender, attack, "disadvantage"),
  };
})();
