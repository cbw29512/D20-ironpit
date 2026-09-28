(() => {
  "use strict";

  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCE_CONVERSION;
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

  function resourceReadyOrRestorable(state, action) {
    if (resourceAvailable(state, action)) return true;
    return Boolean(action.resourceId && R()?.restorationAction(state, action.resourceId));
  }

  function chooseBonus(member, setup) {
    try {
      if (!E().available(member.state, "bonus_action")) return null;
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if ((action.actionCost || "action") !== "bonus_action" || !resourceReadyOrRestorable(member.state, action)) continue;
        if (action.area) {
          const placements = T().legalPlacements(member, setup, action.area, action.range)
            .filter((placement) => placement.targetIds.length)
            .sort((a, b) => b.targetIds.length - a.targetIds.length || a.friendlyIds.length - b.friendlyIds.length);
          if (placements.length) candidates.push({ action, placement: placements[0], target: null, distance: 0 });
          continue;
        }
        for (const target of F().targetOrder(member, setup)) {
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance)) {
            candidates.push({ action, placement: null, target, distance });
            break;
          }
        }
      }
      candidates.sort((a, b) =>
        Number(Boolean(b.placement)) - Number(Boolean(a.placement))
        || (b.placement?.targetIds.length || 1) - (a.placement?.targetIds.length || 1)
        || a.action.id.localeCompare(b.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser Bonus Action save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, selected) {
    try {
      if (!selected) return null;
      const { action, placement } = selected;
      const actionCost = action.actionCost || "action";
      if (!E().available(member.state, actionCost)) return null;
      if (!resourceAvailable(member.state, action)) throw new Error(`${action.name} resource is unavailable.`);
      let remaining = null;
      if (action.resourceId) {
        member.state.resources[action.resourceId] -= action.resourceCost || 1;
        remaining = member.state.resources[action.resourceId];
      }
      E().spend(member.state, actionCost);
      const shared = action.damageDiceCount ? D().rollMany(action.damageDiceCount, action.damageDiceSize) : null;
      const events = [];
      for (const id of placement.targetIds) {
        const target = memberById(setup, id);
        if (!target) throw new Error(`Unknown area-save target ${id}.`);
        const event = V().resolveAction(sequence, round, member, target, action, 0, {
          spendAction: false, checkResource: false, spendResource: false,
          resourceRemaining: remaining, sharedDamageRolls: shared, setup,
        });
        sequence += 1;
        const chain = DMR()?.chain(sequence, round, member, event, setup)
          || { events: [event], sequence };
        events.push(...chain.events); sequence = chain.sequence;
      }
      return { events, sequence, placement };
    } catch (error) {
      console.error("Failed browser area-save resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolveBonus(sequence, round, member, setup) {
    try {
      const selected = chooseBonus(member, setup);
      if (!selected) return null;
      const events = [];
      if (!resourceAvailable(member.state, selected.action)) {
        const conversion = R()?.restorationAction(member.state, selected.action.resourceId);
        if (!conversion) throw new Error(`${selected.action.name} resource cannot be restored.`);
        const restored = R().resolve(sequence, round, member, conversion);
        if (!restored) throw new Error(`${selected.action.name} restoration became unavailable.`);
        events.push(restored); sequence += 1;
      }
      if (selected.placement) {
        const area = resolve(sequence, round, member, setup, selected);
        if (!area) throw new Error("Bonus Action area save became unavailable.");
        return { events: [...events, ...area.events], sequence: area.sequence };
      }
      const event = V().resolveAction(
        sequence, round, member, selected.target, selected.action, selected.distance, { setup },
      );
      const next = sequence + 1;
      const chain = DMR()?.chain(next, round, member, event, setup) || { events: [event], sequence: next };
      return { events: [...events, ...chain.events], sequence: chain.sequence };
    } catch (error) {
      console.error("Failed browser Bonus Action save resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Bonus Action save hook installation requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "bonus-save-action")) return;
    hooks.registerAbility(phase, {
      id: "bonus-save-action", priority: 40, rulesets: ["2014", "2024"],
      appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
      resolve: ({ sequence, round, member, setup }) => {
        const result = resolveBonus(sequence, round, member, setup);
        return result ? { ...result, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = { choose, chooseBonus, installAbilityHooks, resolve, resolveBonus };
})();