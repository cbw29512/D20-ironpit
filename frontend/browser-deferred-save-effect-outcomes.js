(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;

  function typedDamage(targetState, rule, diceCount, diceSize, damageType, multiplier, affectedStates) {
    try {
      const rolls = Array.from({ length: diceCount }, () => D().roll(diceSize));
      const rolledTotal = rolls.reduce((sum, value) => sum + value, 0);
      const scaledTotal = Math.floor(rolledTotal * multiplier);
      const applied = A().resolveDamage
        ? A().resolveDamage(targetState, scaledTotal, damageType).applied
        : A().adjustedDamage(targetState, scaledTotal, damageType);
      const component = {
        source: rule.source_name,
        notation: `${diceCount}d${diceSize}`,
        rolls,
        modifier: 0,
        damage_type: damageType,
        total: scaledTotal,
        applied_total: applied,
      };
      A().applyDamage(targetState, applied, false, [damageType], affectedStates);
      return {
        damageRoll: { notation: component.notation, rolls, modifier: 0, total: applied },
        damageComponents: [component],
      };
    } catch (error) {
      console.error("Browser deferred typed damage failed", { source: rule?.source_name, error });
      throw error;
    }
  }

  function resolve(targetState, rule, saveSucceeded, affectedStates) {
    try {
      if ((rule.failure_damage_dice_count || 0) > 0) {
        if (!rule.failure_damage_type) {
          throw new Error(`Deferred effect ${rule.source_id} has failure damage dice without a type.`);
        }
        if (saveSucceeded && rule.success_damage_from_failure === "none") {
          return { damageRoll: null, damageComponents: [] };
        }
        return typedDamage(
          targetState,
          rule,
          rule.failure_damage_dice_count,
          rule.failure_damage_dice_size,
          rule.failure_damage_type,
          saveSucceeded && rule.success_damage_from_failure === "half" ? 0.5 : 1,
          affectedStates,
        );
      }
      if (saveSucceeded && (rule.success_damage_dice_count || 0) > 0) {
        if (!rule.success_damage_type) {
          throw new Error(`Deferred effect ${rule.source_id} has damage dice without a type.`);
        }
        return typedDamage(
          targetState,
          rule,
          rule.success_damage_dice_count,
          rule.success_damage_dice_size,
          rule.success_damage_type,
          1,
          affectedStates,
        );
      }
      if (!saveSucceeded && rule.failure_sets_zero_hp) {
        Z().reduceToZero(targetState, affectedStates);
      }
      return { damageRoll: null, damageComponents: [] };
    } catch (error) {
      console.error("Browser deferred save outcome failed", { source: rule?.source_name, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEFERRED_SAVE_OUTCOMES = { resolve };
})();
