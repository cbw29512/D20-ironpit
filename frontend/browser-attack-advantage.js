(() => {
  "use strict";
  function sources(attack, target) {
    try {
      let total = 0;
      const effectiveMaxHp = target.template.max_hp + (target.max_hp_bonus || 0);
      for (const spec of attack.conditionalAttackAdvantage || []) {
        if (spec.trigger === "target_not_full_hp") { total += target.current_hp < effectiveMaxHp ? 1 : 0; continue; }
        throw new Error(`Unsupported conditional attack Advantage trigger: ${spec.trigger}`);
      }
      return total;
    } catch (error) { console.error("Conditional attack Advantage resolution failed.", error); throw error; }
  }
  window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE = { sources };
})();
