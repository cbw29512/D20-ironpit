(() => {
  "use strict";

  function sources(attacker, defender, attack, mode) {
    try {
      if (defender.current_hp >= defender.template.max_hp) return 0;
      const explicit = (attack.conditionalAttackModifiers || []).filter((item) =>
        item.mode === mode && item.trigger === "target_missing_hp"
      ).length;
      const bloodFrenzy = mode === "advantage" && attacker.template.traits?.includes("blood-frenzy") ? 1 : 0;
      return explicit + bloodFrenzy;
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
