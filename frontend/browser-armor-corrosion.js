(() => {
  "use strict";
  function afterHit(state, armorId, {hit, nonmagicalMetalArmor, itemBaseAC, destroyAtItemAC = 10}) {
    if (typeof armorId !== "string" || !armorId.trim())
      throw new Error("Armor corrosion requires a stable item ID.");
    if (typeof hit !== "boolean" || typeof nonmagicalMetalArmor !== "boolean")
      throw new Error("Armor corrosion requires verified hit and gear flags.");
    if (!Number.isInteger(itemBaseAC) || !Number.isInteger(destroyAtItemAC)
      || itemBaseAC <= destroyAtItemAC || destroyAtItemAC < 0)
      throw new Error("Armor corrosion requires verified item AC and floor.");
    const current = (state.armor_corrosion_penalties || {})[armorId] ?? 0;
    if (!Number.isInteger(current) || current < 0 || current > itemBaseAC - destroyAtItemAC)
      throw new Error("Invalid armor corrosion item state.");
    let destroyed = (state.destroyed_armor_ids || []).includes(armorId);
    if (!hit || !nonmagicalMetalArmor || destroyed)
      return {penalty: current ? -current : 0, destroyed, applied: false};
    const next = current + 1;
    destroyed = itemBaseAC - next <= destroyAtItemAC;
    if (!state.armor_corrosion_penalties) state.armor_corrosion_penalties = {};
    if (!state.destroyed_armor_ids) state.destroyed_armor_ids = [];
    state.armor_corrosion_penalties[armorId] = next;
    if (destroyed) state.destroyed_armor_ids.push(armorId);
    return {penalty: -next, destroyed, applied: true};
  }
  window.IRON_PIT_BROWSER_ARMOR_CORROSION = {afterHit};
})();
