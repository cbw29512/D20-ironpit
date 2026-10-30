(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;

  function memberById(setup, id) {
    try {
      return [...setup.heroes, ...setup.monsters]
        .find((member) => member.combatant_id === id) || null;
    } catch (error) {
      console.error("Failed browser area-save member lookup", { id, error });
      throw error;
    }
  }

  function resourceAvailable(state, action) {
    try {
      return !action.resourceId
        || (state.resources[action.resourceId] || 0) >= (action.resourceCost || 1);
    } catch (error) {
      console.error("Failed browser area-save resource check", { action: action?.id, error });
      throw error;
    }
  }

  function healingTarget(member, setup, action, placement, requireWounded = false) {
    try {
      if (!action.areaHealingRider) return null;
      const allies = member.side === "heroes" ? setup.heroes : setup.monsters;
      const legal = allies.filter((target) => target.state.is_alive && !target.state.is_dead
        && T().memberInPlacement(member, target, action.area, placement)
        && (!requireWounded || target.state.current_hp < S().effectiveMaxHp(target.state)));
      legal.sort((left, right) =>
        Number(left.state.current_hp > 0) - Number(right.state.current_hp > 0)
        || left.state.current_hp / Math.max(1, S().effectiveMaxHp(left.state))
          - right.state.current_hp / Math.max(1, S().effectiveMaxHp(right.state))
        || left.combatant_id.localeCompare(right.combatant_id));
      return legal[0] || null;
    } catch (error) {
      console.error("Failed browser area-healing target choice", {
        member: member.combatant_id, action: action.id, error,
      });
      throw error;
    }
  }

  function prohibitedContext(member, setup, action) {
    try {
      if (!action.prohibitedEnvironmentContextId) return false;
      const runtime = window.IRON_PIT_BROWSER_ENVIRONMENT_CONTEXTS;
      if (!runtime?.inside) {
        throw new Error("Context-gated Action requires shared environment context resolver.");
      }
      return runtime.inside(member, setup, action.prohibitedEnvironmentContextId);
    } catch (error) {
      console.error("Failed Action environment eligibility.", {
        source: member?.combatant_id, effect: action?.id, error,
      });
      throw error;
    }
  }

  function eligiblePlacement(member, setup, action, placement) {
    try {
      const candidates = action.targetScope === "all-other-creatures"
        ? [...placement.targetIds, ...placement.friendlyIds] : placement.targetIds;
      const targetIds = candidates.filter((id) => {
        const target = memberById(setup, id);
        return target && target.combatant_id !== member.combatant_id
          && (action.targetScope === "all-other-creatures" || target.side !== member.side)
          && V().legalAction(action, target, 0, member.combatant_id, member);
      });
      return { ...placement, targetIds, target_ids: targetIds };
    } catch (error) {
      console.error("Failed browser area-save eligibility", {
        member: member.combatant_id, action: action.id, error,
      });
      throw error;
    }
  }

  function expectedSaveDamage(action) {
    try {
      const components = action.damageComponents?.length
        ? action.damageComponents : (action.damageDiceCount ? [action] : []);
      return components.reduce((sum, part) => {
        const count = part.diceCount ?? part.damageDiceCount ?? 0;
        const size = part.diceSize ?? part.damageDiceSize ?? 0;
        return sum + (count > 0
          ? count * (size + 1) / 2 + (part.damageBonus ?? 0) : 0);
      }, 0);
    } catch (error) {
      console.error("Failed area-save expected damage calculation", { action: action?.id, error });
      throw error;
    }
  }

  function choose(member, setup, actionCost = null, openingOnly = false, predicate = null) {
    try {
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if (predicate && !predicate(action)) continue;
        if (Boolean(action.openingInitiativeOnly) !== openingOnly) continue;
        if (openingOnly
          && !window.IRON_PIT_BROWSER_CHARGE?.openingEligible(member.state.current_round, member, setup)) {
          continue;
        }
        if (actionCost && (action.actionCost || "action") !== actionCost) continue;
        if (!action.area || !resourceAvailable(member.state, action)
          || prohibitedContext(member, setup, action)) continue;
        if (action.requiresNoActiveGrapple) {
          const holding = [...setup.heroes, ...setup.monsters].some((target) =>
            target.combatant_id !== member.combatant_id && !target.state.is_dead
            && target.state.grapple_sources.some((source) =>
              source.source_id === member.combatant_id));
          if (holding) continue;
        }
        const placements = T().legalPlacements(
          member, setup, action.area, action.range,
          Boolean(action.areaHealingRider) || action.targetScope === "all-other-creatures",
        );
        for (const placement of placements) {
          const legal = eligiblePlacement(member, setup, action, placement);
          if (!legal.targetIds.length && !action.areaHealingRider) continue;
          const healTarget = healingTarget(member, setup, action, legal, !legal.targetIds.length);
          if (action.areaHealingRider && !healTarget) continue;
          candidates.push({ action, placement: legal, healTarget });
        }
      }
      candidates.sort((a, b) =>
        b.placement.targetIds.length - a.placement.targetIds.length
        || expectedSaveDamage(b.action) - expectedSaveDamage(a.action)
        || Number(Boolean(b.healTarget)) - Number(Boolean(a.healTarget))
        || a.action.id.localeCompare(b.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser area-save choice", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_SAVE_CHOICE = {
    choose, eligiblePlacement, expectedSaveDamage, healingTarget,
    prohibitedContext, resourceAvailable,
  };
})();
