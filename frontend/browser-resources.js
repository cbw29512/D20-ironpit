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

  function buildRechargeEvents(state, member, round, sequence, results) {
    const definitions = new Map((state.template.resourceDefinitions || []).map((item) => [item.id, item]));
    const events = [];
    for (const result of results) {
      const definition = definitions.get(result.resourceId);
      if (!definition) throw new Error(`Recharge definition ${result.resourceId} is missing.`);
      const remaining = state.resources?.[result.resourceId] || 0;
      const outcome = result.recharged ? `recharged to ${remaining}` : "did not recharge";
      const rollLabel = `Recharge d${definition.rechargeDieSize || 6}: ${result.roll} vs ${definition.rechargeMinimum}+`;
      events.push({
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: state.template.name,
        feature_id: result.resourceId, resource_remaining: remaining, animation: "resource",
        description: `${state.template.name} rolls ${definition.name} ${rollLabel}; ${outcome}.`,
        audit: { schema_version: 1, steps: [
          { phase: "roll", kind: "roll", label: rollLabel },
          { phase: "resource_change", kind: "resource", label: `${definition.name}: ${outcome}` },
        ] },
      });
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_RESOURCES = { buildRechargeEvents, canUse, refresh, spend };
})();