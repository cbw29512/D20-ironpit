(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
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

  function affectedStates(setup) {
    try {
      return setup
        ? [...setup.heroes, ...setup.monsters].map((member) => member.state)
        : [];
    } catch (error) {
      console.error("Failed to collect save-damage combatant states", { error });
      throw error;
    }
  }

  function validatedRolls(action, count, shared) {
    try {
      const rolls = shared == null
        ? D().rollMany(count, action.damageDiceSize)
        : [...shared];
      if (rolls.length !== count || rolls.some(
        (roll) => !Number.isInteger(roll)
          || roll < 1 || roll > action.damageDiceSize,
      )) throw new Error(`${action.name} shared damage rolls are invalid.`);
      return rolls;
    } catch (error) {
      console.error("Failed to validate legacy save-damage rolls", {
        actionId: action?.id, error,
      });
      throw error;
    }
  }

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

  function resolveComponents(state, action, succeeded, shared) {
    try {
      if (!action.damageComponents?.length) return null;
      if ((action.damageDiceCount || 0) || action.damageType
        || (action.damageBonus || 0)) {
        throw new Error(`${action.name} mixes component and legacy save damage.`);
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
        )) throw new Error(`${action.name} component rolls are invalid.`);
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

  function resolveLegacy(state, action, succeeded, shared) {
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

  function resolveAndApply(target, action, succeeded, options = {}) {
    try {
      const resolved = resolveComponents(
        target.state, action, succeeded, options.sharedDamageRolls,
      ) || resolveLegacy(
        target.state, action, succeeded, options.sharedDamageRolls,
      ) || { components: [], roll: null, appliedTotal: 0, damageTypes: [] };
      let damageOutcome = null;
      if (resolved.appliedTotal) {
        const states = affectedStates(options.setup);
        const incoming = resolved.appliedTotal;
        let appliedTotal = incoming;
        if (action.minimumRemainingHp) {
          appliedTotal = Math.min(
            appliedTotal,
            Math.max(0, target.state.current_hp - action.minimumRemainingHp),
          );
        }
        if (appliedTotal) {
          damageOutcome = A().applyDamage(
            target.state, appliedTotal, false, resolved.damageTypes,
            states, options.setup, resolved.components,
          );
        }
        if (!succeeded && action.reduceHitPointMaximumOnFailedSave && incoming) {
          window.IRON_PIT_BROWSER_FRIENDLY_RECOVERY_AURAS
            .applyHitPointMaximumReduction(target.state, incoming);
        }
        window.IRON_PIT_BROWSER_RAGE?.endIfIncapacitated(target.state);
        C()?.endIfIncapacitated(target.state, states);
      }
      if (!succeeded && action.failureSetsZeroHp) {
        const zeroHp = window.IRON_PIT_BROWSER_ZERO_HP;
        if (!zeroHp?.reduceToZero) {
          throw new Error(
            "Direct zero-HP save outcome requires universal zero-HP runtime.",
          );
        }
        zeroHp.reduceToZero(target.state, affectedStates(options.setup));
      }
      return { ...resolved, damageOutcome };
    } catch (error) {
      console.error("Failed to resolve and apply save damage", {
        actionId: action?.id, target: target?.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_DAMAGE = {
    resolve: resolveComponents,
    resolveAndApply,
  };
})();
