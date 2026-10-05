(() => {
  "use strict";

  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
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
      console.error("Failed browser area-healing target choice", { member: member.combatant_id, action: action.id, error });
      throw error;
    }
  }

  function resolveHealing(sequence, round, member, target, action, remaining) {
    try {
      const rider = action.areaHealingRider;
      if (!rider || !H()) throw new Error(`${action.name} area-healing runtime is unavailable.`);
      const rolls = D().rollMany(rider.diceCount, rider.diceSize);
      const total = rolls.reduce((sum, value) => sum + value, 0) + (rider.healingBonus || 0);
      const before = target.state.current_hp;
      const healed = H().restore(target.state, total);
      return {
        sequence, round_number: round, event_type: "healing",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        healing_roll: {
          notation: `${rider.diceCount}d${rider.diceSize}+${rider.healingBonus || 0}`,
          rolls, modifier: rider.healingBonus || 0, total,
        },
        hp_before: before, hp_after: target.state.current_hp,
        death_save_successes: target.state.death_save_successes,
        death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable, is_dead: target.state.is_dead,
        feature_id: action.id, resource_remaining: remaining,
        animation: action.animation,
        description: `${member.state.template.name}'s ${action.name} restores ${healed} HP to ${target.state.template.name}.`,
      };
    } catch (error) {
      console.error("Failed browser area-healing resolution", { member: member.combatant_id, action: action.id, error });
      throw error;
    }
  }

  function choose(member, setup, actionCost = null) {
    try {
      const candidates = [];
      for (const action of member.state.template.saving_throw_actions || []) {
        if (actionCost && (action.actionCost || "action") !== actionCost) continue;
        if (!action.area || !resourceAvailable(member.state, action)) continue;
        if (action.requiresNoActiveGrapple) {
          const holding = [...setup.heroes, ...setup.monsters].some((target) =>
            target.combatant_id !== member.combatant_id && !target.state.is_dead
            && target.state.grapple_sources.some((source) => source.source_id === member.combatant_id));
          if (holding) continue;
        }
        const placements = T().legalPlacements(
          member, setup, action.area, action.range, Boolean(action.areaHealingRider),
        );
        for (const placement of placements) {
          const targetIds = placement.targetIds.filter((id) => {
            const target = memberById(setup, id);
            return target && V().legalAction(action, target, 0, member.combatant_id);
          });
          if (!targetIds.length && !action.areaHealingRider) continue;
          const legal = { ...placement, targetIds, target_ids: targetIds };
          const healTarget = healingTarget(member, setup, action, legal, !legal.targetIds.length);
          if (action.areaHealingRider && !healTarget) continue;
          candidates.push({ action, placement: legal, healTarget });
        }
      }
      candidates.sort((a, b) =>
        b.placement.targetIds.length - a.placement.targetIds.length
        || (b.action.damageDiceCount || 0) - (a.action.damageDiceCount || 0)
        || Number(Boolean(b.healTarget)) - Number(Boolean(a.healTarget))
        || a.action.id.localeCompare(b.action.id));
      return candidates[0] || null;
    } catch (error) {
      console.error("Failed browser area-save choice", { member: member.combatant_id, error });
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
      const legalPlacements = T().legalPlacements(
        member, setup, action.area, action.range, Boolean(action.areaHealingRider),
      );
      if (!legalPlacements.some((row) =>
        JSON.stringify(row.origin) === JSON.stringify(placement.origin)
        && JSON.stringify(row.direction) === JSON.stringify(placement.direction)
        && JSON.stringify(row.targetIds) === JSON.stringify(placement.targetIds))) {
        throw new Error(`${action.name} has a stale or illegal area placement.`);
      }
      const healTarget = healingTarget(member, setup, action, placement, !placement.targetIds.length);
      if (action.areaHealingRider && !healTarget) throw new Error(`${action.name} has no legal healing target in its area.`);

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
      if (healTarget) {
        events.push(resolveHealing(sequence, round, member, healTarget, action, remaining));
        sequence += 1;
      }
      return { events, sequence, placement };
    } catch (error) {
      console.error("Failed browser area-save resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = { choose, resolve };
})();
