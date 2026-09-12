(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const D = () => window.IRON_PIT_DICE;

  function memberById(setup, id) {
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === id) || null;
  }

  function rechargeAction(state, action) {
    if (!action.resourceId) return false;
    const definition = (state.template.resource_definitions || [])
      .find((item) => item.id === action.resourceId);
    return Boolean(definition?.recharge);
  }

  function choice(member, setup, rechargeOnly = false) {
    try {
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if (!action.area || !V().resourceAvailable(member.state, action)) continue;
        if (rechargeOnly && !rechargeAction(member.state, action)) continue;
        const placements = T().legalPlacements(member, setup, action.area);
        if (placements.length) candidates.push({ action, placement: placements[0] });
      }
      candidates.sort((left, right) =>
        right.placement.targetIds.length - left.placement.targetIds.length
        || left.action.id.localeCompare(right.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser area save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function singleChoice(member, setup, rechargeOnly = false) {
    for (const target of F().targetOrder(member, setup)) {
      for (const action of member.state.template.saving_throw_actions || []) {
        if (action.area) continue;
        if (rechargeOnly && !rechargeAction(member.state, action)) continue;
        if (!V().resourceAvailable(member.state, action)) continue;
        const distance = F().saveDistance(member, target, action.range);
        if (V().legalAction(action, target, distance)) return { target, action, distance };
      }
    }
    return null;
  }

  function resolve(sequence, round, member, setup, rechargeOnly = false) {
    try {
      const selected = choice(member, setup, rechargeOnly);
      if (!selected || !E().available(member.state, "action")) return null;
      const { action, placement } = selected;
      if (!V().resourceAvailable(member.state, action)) throw new Error(`${action.name} resource is unavailable.`);
      let resourceRemaining = null;
      if (action.resourceId) {
        const cost = action.resourceCost || 1;
        member.state.resources[action.resourceId] -= cost;
        resourceRemaining = member.state.resources[action.resourceId];
      }
      E().spend(member.state, "action");
      const shared = action.damageDiceCount
        ? D().rollMany(action.damageDiceCount, action.damageDiceSize)
        : null;
      const events = [];
      for (const targetId of placement.targetIds) {
        const target = memberById(setup, targetId);
        if (!target) throw new Error(`Unknown area target ${targetId}.`);
        events.push(V().resolveAction(sequence++, round, member, target, action, 0, {
          spendAction: false,
          checkResource: false,
          spendResource: false,
          resourceRemaining,
          sharedDamageRolls: shared,
          setup,
        }));
      }
      return { events, sequence, placement };
    } catch (error) {
      console.error("Failed browser area save resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  function fireRecharge(sequence, round, member, setup) {
    const area = resolve(sequence, round, member, setup, true);
    if (area) return area;
    const saved = singleChoice(member, setup, true);
    if (!saved || !E().available(member.state, "action")) return null;
    return {
      events: [V().resolveAction(
        sequence, round, member, saved.target, saved.action, saved.distance, { setup },
      )],
      sequence: sequence + 1,
    };
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = {
    choice,
    fireRecharge,
    rechargeAction,
    resolve,
    singleChoice,
  };
})();
