(() => {
  "use strict";

  const D = () => window.IRON_PIT_DICE;

  function canUse(state, action) {
    const id = action?.resourceId;
    if (!id) return true;
    const cost = action.resourceCost || 1;
    return (state.resources?.[id] || 0) >= cost;
  }

  function spend(state, action) {
    const id = action?.resourceId;
    if (!id) return null;
    const cost = action.resourceCost || 1;
    if (!canUse(state, action)) throw new Error(`Resource ${id} is unavailable for ${action.id || "action"}.`);
    state.resources[id] -= cost;
    return state.resources[id];
  }

  function refresh(state) {
    if (state.template.kind !== "monster") return [];
    const recharge = (state.template.resourceDefinitions || []).filter((item) => item.rechargeMinimum != null);
    if (!recharge.length) return [];
    const results = [];
    for (const definition of recharge) {
      const current = state.resources?.[definition.id] || 0;
      const maxUses = definition.maxUses || 1;
      if (current >= maxUses) continue;
      const roll = D().roll(definition.rechargeDieSize || 6);
      const recharged = roll >= definition.rechargeMinimum;
      if (recharged) state.resources[definition.id] = maxUses;
      results.push({ resourceId: definition.id, roll, recharged });
    }
    return results;
  }

  window.IRON_PIT_BROWSER_RESOURCES = { canUse, refresh, spend };
})();
