(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const D = () => window.IRON_PIT_DICE;

  function memberById(setup, id) {
    return [...setup.heroes, ...setup.monsters].find((member) => member.combatant_id === id) || null;
  }

  function resourceAvailable(state, action) {
    return !action.resourceId
      || (state.resources[action.resourceId] || 0) >= (action.resourceCost || 1);
  }

  function choose(member, setup) {
    try {
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if (!action.area || !resourceAvailable(member.state, action)) continue;
        if (action.requiresNoActiveGrapple) {
          const holding = [...setup.heroes, ...setup.monsters].some((target) =>
            target.combatant_id !== member.combatant_id && !target.state.is_dead
            && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id));
          if (holding) continue;
        }
        const placements = T().legalPlacements(member, setup, action.area, action.range)
          .filter((placement) => placement.targetIds.length)
          .sort((a, b) => b.targetIds.length - a.targetIds.length || a.friendlyIds.length - b.friendlyIds.length);
        if (placements.length) candidates.push({ action, placement: placements[0] });
      }
      candidates.sort((a, b) =>
        b.placement.targetIds.length - a.placement.targetIds.length
        || (b.action.damageDiceCount || 0) - (a.action.damageDiceCount || 0)
        || a.action.id.localeCompare(b.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser area-save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, selected) {
    try {
      if (!selected || !E().available(member.state, "action")) return null;
      const { action, placement } = selected;
      if (!resourceAvailable(member.state, action)) throw new Error(`${action.name} resource is unavailable.`);
      let remaining = null;
      if (action.resourceId) {
        member.state.resources[action.resourceId] -= action.resourceCost || 1;
        remaining = member.state.resources[action.resourceId];
      }
      E().spend(member.state, "action");
      const shared = action.damageDiceCount ? D().rollMany(action.damageDiceCount, action.damageDiceSize) : null;
      const events = [];
      for (const id of placement.targetIds) {
        const target = memberById(setup, id);
        if (!target) throw new Error(`Unknown area-save target ${id}.`);
        events.push(V().resolveAction(sequence++, round, member, target, action, 0, {
          spendAction: false, checkResource: false, spendResource: false,
          resourceRemaining: remaining, sharedDamageRolls: shared, setup,
        }));
      }
      return { events, sequence, placement };
    } catch (error) {
      console.error("Failed browser area-save resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = { choose, resolve };
})();