(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;

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

  function resolveAndApply(target, action, succeeded, options = {}) {
    try {
      const component = window.IRON_PIT_BROWSER_SAVE_DAMAGE;
      const legacy = window.IRON_PIT_BROWSER_SAVE_DAMAGE_LEGACY;
      if (!component?.resolve || !legacy?.resolve) {
        throw new Error("Save-damage resolver modules are unavailable.");
      }
      const resolved = component.resolve(
        target.state, action, succeeded, options.sharedDamageRolls,
      ) || legacy.resolve(
        target.state, action, succeeded, options.sharedDamageRolls,
      ) || {
        components: [], roll: null, appliedTotal: 0, damageTypes: [],
      };
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
            target.state,
            appliedTotal,
            false,
            resolved.damageTypes,
            states,
            options.setup,
            resolved.components,
            options.sourceId || null,
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

  window.IRON_PIT_BROWSER_SAVE_DAMAGE_APPLY = {
    affectedStates, resolveAndApply,
  };
})();
