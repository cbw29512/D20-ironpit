(() => {
  "use strict";
  const MAX_STACKS = 5;
  function key(id) {
    if (typeof id !== "string" || !id.trim())
      throw new Error("Corrosion requires a stable weapon-instance ID.");
    return id;
  }
  function modifier(state, id) {
    const stacks = (state.weapon_corrosion_penalties || {})[key(id)] ?? 0;
    if (!Number.isInteger(stacks) || stacks < 0 || stacks > MAX_STACKS)
      throw new Error("Invalid encounter-local corrosion stacks.");
    return -stacks;
  }
  function available(state, id) { return modifier(state, id) > -MAX_STACKS; }
  function afterHit(state, id, { hit, nonmagicalMetal }) {
    const weaponId = key(id), previous = -modifier(state, weaponId);
    if (typeof hit !== "boolean" || typeof nonmagicalMetal !== "boolean")
      throw new Error("Corrosion requires verified hit and material flags.");
    if (!hit || !nonmagicalMetal) return -previous;
    if (previous === MAX_STACKS)
      throw new Error("A destroyed weapon cannot hit again this fight.");
    if (!state.weapon_corrosion_penalties)
      state.weapon_corrosion_penalties = {};
    state.weapon_corrosion_penalties[weaponId] = previous + 1;
    return -(previous + 1);
  }
  function weaponDamage(state, id, damage) {
    if (!Number.isInteger(damage) || damage < 0)
      throw new Error("Weapon damage before corrosion must be nonnegative.");
    if (!available(state, id))
      throw new Error("Destroyed weapon cannot be used for another attack.");
    return Math.max(0, damage + modifier(state, id));
  }
  window.IRON_PIT_BROWSER_WEAPON_CORROSION = {
    modifier, available, afterHit, weaponDamage,
  };
})();
