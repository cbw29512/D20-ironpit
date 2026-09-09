(() => {
  "use strict";
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s) => s.action_available, spend: (s) => { s.action_available = false; } };

  function resolve(sequence, round, actor, setup, action) {
    if (!action?.area) throw new Error(`${action?.name || "Save action"} has no area geometry.`);
    if (!E().available(actor.state, "action")) throw new Error("Action is unavailable for area save action.");
    if (!V().resourceAvailable(actor, action)) throw new Error(`${action.name} resource is unavailable.`);
    const targetIds = T().targetIds(actor, setup, action);
    if (!targetIds.length) throw new Error(`${action.name} has no legal area targets.`);
    const byId = Object.fromEntries([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    E().spend(actor.state, "action");
    const events = [];
    let shared = null;
    for (const id of targetIds) {
      const target = byId[id];
      const event = V().resolveAction(sequence++, round, actor, target, action,
        Math.abs(actor.position_ft - target.position_ft), {
          spendAction: false, spendResource: false, sharedDamageRolls: shared, setup,
        });
      events.push(event);
      if (shared == null && event.damage_components?.length) shared = [...event.damage_components[0].rolls];
    }
    S().spendAttackResource(actor.state, action);
    if (action.resourceId) {
      const remaining = actor.state.resources[action.resourceId];
      events.forEach((event) => { event.resource_remaining = remaining; });
    }
    return { events, sequence };
  }

  function resolveSignature(sequence, round, actor, setup) {
    if (!E().available(actor.state, "action")) return null;
    for (const action of actor.state.template.saving_throw_actions || []) {
      if (!action.area || !action.resourceId || !V().resourceAvailable(actor, action)) continue;
      if (!T().targetIds(actor, setup, action).length) continue;
      return resolve(sequence, round, actor, setup, action);
    }
    return null;
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = { resolve, resolveSignature };
})();
