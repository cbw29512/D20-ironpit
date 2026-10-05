(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;

  function choose(member, setup) {
    if (!E().available(member.state, "action")) return null;
    const orderedTargets = F().targetOrder(member, setup);
    for (const action of member.state.template.saving_throw_actions || []) {
      if ((action.actionCost || "action") !== "action" || (action.maxTargets || 1) <= 1) continue;
      if (action.resourceId && !R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
      const targets = orderedTargets.filter((target) => {
        const distance = F().saveDistance(member, target, action.range);
        return V().legalAction(action, target, distance)
          && (!action.requiresTargetSight
            || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state, distance));
      }).slice(0, action.maxTargets);
      if (targets.length) return { targets, action };
    }
    return null;
  }

  function resolve(sequence, round, member, setup, action, targets) {
    if (!targets.length || targets.length > (action.maxTargets || 1)) {
      throw new Error("Multi-target save selection violates its declared target cap.");
    }
    if (!E().available(member.state, action.actionCost || "action")) {
      throw new Error(`${action.name} Action is unavailable.`);
    }
    if (action.resourceId && !R().available(member.state, action.resourceId, action.resourceCost || 1)) {
      throw new Error(`${action.name} resource is unavailable.`);
    }
    for (const target of targets) {
      const distance = F().saveDistance(member, target, action.range);
      if (!V().legalAction(action, target, distance)
        || (action.requiresTargetSight
          && !window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(member.state, target.state, distance))) {
        throw new Error(`${action.name} has an illegal selected target.`);
      }
    }
    const remaining = action.resourceId
      ? R().spend(member.state, action.resourceId, action.resourceCost || 1)
      : null;
    E().spend(member.state, action.actionCost || "action");
    const events = [];
    for (const target of targets) {
      const distance = F().saveDistance(member, target, action.range);
      const event = V().resolveAction(sequence, round, member, target, action, distance, {
        setup, spendAction: false, checkResource: false,
        spendResource: false, resourceRemaining: remaining,
      });
      if (DR()) {
        const chain = DR().chain(sequence + 1, round, member, event, setup);
        events.push(...chain.events);
        sequence = chain.sequence;
      } else {
        events.push(event);
        sequence += 1;
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_MULTI_SAVE_PROVIDER = { choose, resolve };
})();
