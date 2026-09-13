(() => {
  "use strict";
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const B = () => window.IRON_PIT_BROWSER_BARBARIAN2 || { attacksAgainstAdvantage: () => 0 };
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;

  function sources(attack, target) {
    try {
      let total = 0;
      const effectiveMaxHp = Math.max(0, target.template.max_hp + (target.max_hp_bonus || 0) - (target.max_hp_reduction || 0));
      for (const spec of attack.conditionalAttackAdvantage || []) {
        if (spec.trigger === "target_not_full_hp") { total += target.current_hp < effectiveMaxHp ? 1 : 0; continue; }
        throw new Error(`Unsupported conditional attack Advantage trigger: ${spec.trigger}`);
      }
      return total;
    } catch (error) { console.error("Conditional attack Advantage resolution failed.", error); throw error; }
  }

  function conditionSources(attacker, defender, distance, targetId) {
    let advantage = M().attacksAgainstAdvantage(defender) + B().attacksAgainstAdvantage(defender), disadvantage = 0;
    if (Q().has(attacker, "blinded")) disadvantage += 1; if (Q().has(attacker, "invisible")) advantage += 1;
    if (attacker.active_effect_ids.includes("prone")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("restrained")) disadvantage += 1;
    if (attacker.active_effect_ids.includes("poisoned")) disadvantage += 1;
    disadvantage += T()?.attackRollDisadvantage?.(attacker) || 0;
    disadvantage += G()?.attackDisadvantage(attacker, targetId) || 0;
    if (defender.active_effect_ids.includes("dodge") && !Q().incapacitated(defender) && M().effectiveSpeed(defender) > 0 && !G()?.speedIsZero(defender)) disadvantage += 1;
    if (Q().attackAdvantage(defender)) advantage += 1; if (Q().has(defender, "invisible")) disadvantage += 1;
    if (defender.active_effect_ids.includes("restrained")) advantage += 1;
    if (defender.active_effect_ids.includes("prone")) distance <= 5 ? advantage += 1 : disadvantage += 1;
    return { advantage, disadvantage };
  }

  window.IRON_PIT_BROWSER_ATTACK_ADVANTAGE = { conditionSources, sources };
})();