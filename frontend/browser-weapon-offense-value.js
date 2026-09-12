(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;

  function expectedDamage(attacker, target, attack, setup, distance) {
    try {
      const conditions = A().conditionSources(attacker.state, target.state, distance, target.combatant_id, setup);
      const closeThreat = A().rangedCloseThreat(attacker, target, distance, setup);
      const advantage = conditions.advantage + M().attacksAgainstAdvantage(target.state);
      const mode = R().attackMode(attack, distance, advantage, conditions.disadvantage, closeThreat);
      const probabilities = O().attackProbabilities(
        attacker.state,
        attack.bonus,
        M().effectiveArmorClass(target.state),
        mode,
      );
      if (Q().autoCritical(target.state) && distance <= 5) probabilities.critical = probabilities.hit;
      const factor = O().damageFactor(target.state, attack.damageType);
      const base = attack.fixedDamage != null
        ? attack.fixedDamage
        : O().meanDamage(attack.diceCount || 0, attack.diceSize || 6, attack.damageBonus || 0);
      const critBase = attack.fixedDamage != null
        ? base
        : O().meanDamage((attack.diceCount || 0) * 2, attack.diceSize || 6, attack.damageBonus || 0);
      let normal = base * factor, critical = critBase * factor;
      for (const rider of attack.onHitDamage || []) {
        const riderFactor = O().damageFactor(target.state, rider.damageType);
        normal += O().meanDamage(rider.diceCount || 0, rider.diceSize || 6, rider.damageBonus || 0) * riderFactor;
        critical += O().meanDamage((rider.diceCount || 0) * 2, rider.diceSize || 6, rider.damageBonus || 0) * riderFactor;
      }
      return Math.max(0,
        (probabilities.hit - probabilities.critical) * normal + probabilities.critical * critical);
    } catch (error) {
      console.error("Failed browser weapon offense value", {
        attacker: attacker.combatant_id,
        target: target.combatant_id,
        attack: attack.id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_WEAPON_OFFENSE_VALUE = { expectedDamage };
})();
