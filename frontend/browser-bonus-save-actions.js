(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCE_CONVERSION;
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function resourceAvailable(state, action) {
    return !action.resourceId
      || (state.resources[action.resourceId] || 0) >= (action.resourceCost || 1);
  }

  function resourceReadyOrRestorable(state, action, turnKey = null) {
    if (resourceAvailable(state, action)) return true;
    return Boolean(action.resourceId && R()?.restorationAction(state, action.resourceId, turnKey));
  }

  function choose(member, setup, turnKey = null) {
    try {
      if (!E().available(member.state, "bonus_action")) return null;
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if ((action.actionCost || "action") !== "bonus_action"
          || !resourceReadyOrRestorable(member.state, action, turnKey)) continue;
        if (action.area) {
          const placements = T().legalPlacements(member, setup, action.area, action.range)
            .filter((placement) => placement.targetIds.length)
            .sort((left, right) =>
              right.targetIds.length - left.targetIds.length
              || left.friendlyIds.length - right.friendlyIds.length);
          if (placements.length) {
            candidates.push({ action, placement: placements[0], target: null, distance: 0 });
          }
          continue;
        }
        for (const target of F().targetOrder(member, setup)) {
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance, member.combatant_id)) {
            candidates.push({ action, placement: null, target, distance });
            break;
          }
        }
      }
      candidates.sort((left, right) =>
        Number(Boolean(right.placement)) - Number(Boolean(left.placement))
        || (right.placement?.targetIds.length || 1) - (left.placement?.targetIds.length || 1)
        || left.action.id.localeCompare(right.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser Bonus Action save choice", {
        member: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup) {
    try {
      const turnKey = `${round}:${member.combatant_id}`;
      const selected = choose(member, setup, turnKey);
      if (!selected) return null;
      const events = [];
      if (!resourceAvailable(member.state, selected.action)) {
        const conversion = R()?.restorationAction(member.state, selected.action.resourceId, turnKey);
        if (!conversion) throw new Error(`${selected.action.name} resource cannot be restored.`);
        const restored = R().resolve(sequence, round, member, conversion, turnKey);
        if (!restored) throw new Error(`${selected.action.name} restoration became unavailable.`);
        events.push(restored);
        sequence += 1;
      }
      if (selected.placement) {
        const area = A().resolve(sequence, round, member, setup, selected);
        if (!area) throw new Error("Bonus Action area save became unavailable.");
        return { events: [...events, ...area.events], sequence: area.sequence };
      }
      const event = V().resolveAction(
        sequence, round, member, selected.target, selected.action, selected.distance, { setup },
      );
      const next = sequence + 1;
      const chain = DMR()?.chain(next, round, member, event, setup)
        || { events: [event], sequence: next };
      return { events: [...events, ...chain.events], sequence: chain.sequence };
    } catch (error) {
      console.error("Failed browser Bonus Action save resolution", {
        member: member?.combatant_id, error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Bonus Action save hook requires browser-ability-hooks.js.");
      const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "bonus-save-action")) return;
      hooks.registerAbility(phase, {
        id: "bonus-save-action",
        priority: 40,
        rulesets: ["2014", "2024"],
        appliesTo: (_member, ctx) => ctx.bonusActionCheckpoint === "beforeEscape",
        resolve: ({ sequence, round, member, setup }) => {
          const result = resolve(sequence, round, member, setup);
          return result ? { ...result, claimed: true } : null;
        },
      });
    } catch (error) {
      console.error("Failed to install browser Bonus Action save hook", { error });
      throw error;
    }
  }

  installAbilityHooks();
  window.IRON_PIT_BROWSER_BONUS_SAVE_ACTIONS = { choose, installAbilityHooks, resolve };
})();
