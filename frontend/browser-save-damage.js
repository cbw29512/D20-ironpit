(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) {
      throw new Error("Save damage requires the shared damage resolver.");
    }
    return rules;
  };
  const R = () => window.IRON_PIT_BROWSER_ROGUE_DEFENSES || {
    evasionDamage: (_state, _ability, succeeded, successDamage, total) =>
      succeeded && successDamage === "half" ? Math.floor(total / 2) : total,
  };

  function sharedComponentRolls(action, shared, index) {
    try {
      if (shared == null) return null;
      if (!Array.isArray(shared)
        || shared.length !== action.damageComponents.length
        || !shared.every(Array.isArray)) {
        throw new Error(
          `${action.name} shared damage rolls do not match its components.`,
        );
      }
      return shared[index];
    } catch (error) {
      console.error("Failed to validate component save-damage rolls", {
        actionId: action?.id, error,
      });
      throw error;
    }
  }

  function resolve(state, action, succeeded, shared = null) {
    try {
      if (!action.damageComponents?.length) return null;
      if ((action.damageDiceCount || 0) || action.damageType
        || (action.damageBonus || 0)) {
        throw new Error(
          `${action.name} mixes component and legacy save damage.`,
        );
      }
      if ((action.damageOnlyOnSuccess && !succeeded)
        || (succeeded && action.successDamage === "none"
          && !action.damageOnlyOnSuccess)) {
        return { components: [], roll: null, appliedTotal: 0, damageTypes: [] };
      }
      const components = action.damageComponents.map((spec, index) => {
        if (!spec.damageType) {
          throw new Error(`${action.name} component lacks a damage type.`);
        }
        const supplied = sharedComponentRolls(action, shared, index);
        const rolls = supplied == null
          ? D().rollMany(spec.diceCount, spec.diceSize) : [...supplied];
        if (rolls.length !== spec.diceCount || rolls.some(
          (roll) => !Number.isInteger(roll)
            || roll < 1 || roll > spec.diceSize,
        )) {
          throw new Error(`${action.name} component rolls are invalid.`);
        }
        const raw = rolls.reduce((sum, roll) => sum + roll, 0)
          + (spec.damageBonus || 0);
        const total = R().evasionDamage(
          state, action.saveAbility, succeeded, action.successDamage, raw,
        );
        const resolved = DD().resolveDamage(
          state, Math.max(0, total), spec.damageType,
        );
        return {
          source: action.name,
          notation: `${spec.diceCount}d${spec.diceSize}+${spec.damageBonus || 0}`,
          rolls,
          modifier: spec.damageBonus || 0,
          damage_type: spec.damageType,
          total: Math.max(0, total),
          applied_total: resolved.applied,
          absorbed_healing: resolved.healed || 0,
          absorption_source_name: resolved.sourceName || null,
        };
      });
      const appliedTotal = components.reduce(
        (sum, part) => sum + part.applied_total, 0,
      );
      return {
        components,
        roll: {
          notation: components.map((part) => part.notation).join(" + "),
          rolls: components.flatMap((part) => part.rolls),
          modifier: components.reduce((sum, part) => sum + part.modifier, 0),
          total: appliedTotal,
        },
        appliedTotal,
        damageTypes: components
          .filter((part) => part.applied_total > 0)
          .map((part) => part.damage_type),
      };
    } catch (error) {
      console.error("Failed to resolve component save damage", {
        actionId: action?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_DAMAGE = { resolve };
})();
