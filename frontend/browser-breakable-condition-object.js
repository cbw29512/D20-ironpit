(() => {
  "use strict";
  // No source-name dispatch: both Restrained objects and Grapple objects
  // share the exact same fight-local HP and typed damage calculation.
  function damageState(obj, attackTotal, rolledDamage, damageType) {
    try {
      if (!Number.isInteger(attackTotal) || attackTotal < 0
          || !Number.isInteger(rolledDamage) || rolledDamage < 0)
        throw new Error("Resolved attack/damage values must be nonnegative.");
      if (attackTotal < obj.armor_class) return { appliedDamage: 0, destroyed: false };
      const types = new Set([
        "acid", "bludgeoning", "cold", "fire", "force", "lightning", "necrotic",
        "piercing", "poison", "psychic", "radiant", "slashing", "thunder",
      ]);
      if (!types.has(damageType)) throw new Error("Unknown breakable-object damage type.");
      let amount = (obj.damage_immunities || []).includes(damageType) ? 0 : rolledDamage;
      if (amount && (obj.damage_vulnerabilities || []).includes(damageType)) amount *= 2;
      const appliedDamage = Math.min(amount, obj.current_hp);
      obj.current_hp -= appliedDamage;
      return { appliedDamage, destroyed: obj.current_hp === 0 };
    } catch (error) {
      console.error("Universal breakable object damage failed.", { damageType, error });
      throw error;
    }
  }
  // Hit roll and damage are already resolved. This primitive changes only
  // the temporary object's HP and removes its owning canonical condition.
  function damage(state, effect, attackTotal, rolledDamage, damageType) {
    try {
      if (!(state.timed_effects || []).includes(effect) || !effect.breakable_object)
        throw new Error("The target has no active breakable condition object.");
      const result = damageState(effect.breakable_object, attackTotal, rolledDamage, damageType);
      if (result.destroyed) {
        const timed = window.IRON_PIT_BROWSER_TIMED;
        if (!timed?.removeGroup) throw new Error("Canonical timed condition removal is unavailable.");
        timed.removeGroup(state, effect);
      }
      return result;
    } catch (error) {
      console.error("Breakable condition object damage failed.", { damageType, error });
      throw error;
    }
  }
  function damageGrapple(state, grapple, attackTotal, rolledDamage, damageType) {
    try {
      if (!(state.grapple_sources || []).includes(grapple) || !grapple.breakable_object)
        throw new Error("The target has no active breakable Grapple object.");
      const result = damageState(grapple.breakable_object, attackTotal, rolledDamage, damageType);
      if (result.destroyed) {
        const engine = window.IRON_PIT_BROWSER_GRAPPLE;
        if (!engine?.release) throw new Error("Canonical Grapple release is unavailable.");
        engine.release(state, grapple.source_id);
      }
      return result;
    } catch (error) {
      console.error("Breakable Grapple object damage failed.", { damageType, error });
      throw error;
    }
  }
  function preferFreshLimitedControl(attacker, target, attack) {
    try {
      const control = attack?.controlEffect;
      if (attack?.kind !== "ranged" || !attack.resourceId || attack.fixedDamage !== 0
          || (attack.onHitDamage || []).length || attack.onHitSaveDamage
          || attack.onHitConditionSave || (attack.conditionalDamage || []).length
          || !control?.conditionId || !control.breakableObject) return false;
      const immunity = window.IRON_PIT_BROWSER_CONDITION_IMMUNITY;
      if (!immunity?.immune) throw new Error("Shared condition immunity runtime is unavailable.");
      return !(target.state.active_effect_ids || []).includes(control.conditionId)
        && !immunity.immune(target.state, control.conditionId, attacker.state.template);
    } catch (error) {
      console.error("Breakable-control attack policy failed.", { attack: attack?.id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT = { damage, damageGrapple, preferFreshLimitedControl };
})();