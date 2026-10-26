(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) {
      throw new Error("Legacy save damage requires the shared damage resolver.");
    }
    return rules;
  };
  const R = () => window.IRON_PIT_BROWSER_ROGUE_DEFENSES || {
    evasionDamage: (_state, _ability, succeeded, successDamage, total) =>
      succeeded && successDamage === "half" ? Math.floor(total / 2) : total,
  };

  function validatedRolls(action, count, shared) {
    try {
      const rolls = shared == null
        ? D().rollMany(count, action.damageDiceSize) : [...shared];
      if (rolls.length !== count || rolls.some(
        (roll) => !Number.isInteger(roll)
          || roll < 1 || roll > action.damageDiceSize,
      )) {
        throw new Error(`${action.name} shared damage rolls are invalid.`);
      }
      return rolls;
    } catch (error) {
      console.error("Failed to validate legacy save-damage rolls", {
        actionId: action?.id, error,
      });
      throw error;
    }
  }

  function resolve(state, action, succeeded, shared = null) {
    try {
      const count = action.damageDiceCount || 0;
      if (!count || action.damageComponents?.length) return null;
      if (action.damageOnlyOnSuccess ? !succeeded
        : succeeded && action.successDamage === "none") {
        return { components: [], roll: null, appliedTotal: 0, damageTypes: [] };
      }
      if (!action.damageType) {
        throw new Error(`${action.name} has damage dice but no damage type.`);
      }
      const rolls = validatedRolls(action, count, shared);
      const raw = rolls.reduce((sum, roll) => sum + roll, 0)
        + (action.damageBonus || 0);
      const total = R().evasionDamage(
        state, action.saveAbility, succeeded, action.successDamage, raw,
      );
      const resolved = DD().resolveDamage(
        state, Math.max(0, total), action.damageType,
      );
      const component = {
        source: action.name,
        notation: `${count}d${action.damageDiceSize}+${action.damageBonus || 0}`,
        rolls,
        modifier: action.damageBonus || 0,
        damage_type: action.damageType,
        total: Math.max(0, total),
        applied_total: resolved.applied,
        absorbed_healing: resolved.healed || 0,
        absorption_source_name: resolved.sourceName || null,
      };
      return {
        components: [component],
        roll: {
          notation: component.notation,
          rolls,
          modifier: action.damageBonus || 0,
          total: resolved.applied,
        },
        appliedTotal: resolved.applied,
        damageTypes: resolved.applied ? [action.damageType] : [],
      };
    } catch (error) {
      console.error("Failed to resolve legacy save damage", {
        actionId: action?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_DAMAGE_LEGACY = { resolve };
})();
