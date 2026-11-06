(() => {
  "use strict";
  // Hit roll and damage are already resolved. This primitive changes only
  // the temporary object's HP and removes its owning canonical condition.
  function damage(state, effect, attackTotal, rolledDamage, damageType) {
    try {
      if (!(state.timed_effects || []).includes(effect) || !effect.breakable_object)
        throw new Error("The target has no active breakable condition object.");
      if (!Number.isInteger(attackTotal) || attackTotal < 0
        || !Number.isInteger(rolledDamage) || rolledDamage < 0)
        throw new Error("Resolved attack/damage values must be nonnegative.");
      const obj = effect.breakable_object;
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
      const destroyed = obj.current_hp === 0;
      if (destroyed) {
        const timed = window.IRON_PIT_BROWSER_TIMED;
        if (!timed?.removeGroup) throw new Error("Canonical timed condition removal is unavailable.");
        timed.removeGroup(state, effect);
      }
      return { appliedDamage, destroyed };
    } catch (error) {
      console.error("Breakable condition object damage failed.", { damageType, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT = { damage };
})();