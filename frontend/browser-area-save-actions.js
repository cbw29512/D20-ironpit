(() => {
  "use strict";

  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const D = () => window.IRON_PIT_DICE;
  const C = () => window.IRON_PIT_BROWSER_AREA_SAVE_CHOICE;

  function memberById(setup, id) {
    try {
      return [...setup.heroes, ...setup.monsters]
        .find((member) => member.combatant_id === id) || null;
    } catch (error) {
      console.error("Failed browser area-save member lookup", { id, error });
      throw error;
    }
  }
  function resolveHealing(sequence, round, member, target, action, remaining) {
    try {
      const rider = action.areaHealingRider;
      if (!rider || !H()) throw new Error(`${action.name} area-healing runtime is unavailable.`);
      const rolls = D().rollMany(rider.diceCount, rider.diceSize);
      const total = rolls.reduce((sum, value) => sum + value, 0)
        + (rider.healingBonus || 0);
      const before = target.state.current_hp;
      const healed = H().restore(target.state, total);
      const timed = window.IRON_PIT_BROWSER_TIMED;
      const needsCleanup = action.magicalEffect
        && (target.state.timed_effects || []).some((effect) => effect.ends_on_magical_healing);
      if (needsCleanup && !timed?.removeOnMagicalHealing) {
        throw new Error("Area magical healing requires timed-effect cleanup.");
      }
      const removed = needsCleanup ? timed.removeOnMagicalHealing(target.state) : [];
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
        removed_condition_ids: removed, animation: action.animation,
        description: `${member.state.template.name}'s ${action.name} restores ${healed} HP to ${target.state.template.name}.`,
      };
    } catch (error) {
      console.error("Failed browser area-healing resolution", {
        member: member.combatant_id, action: action.id, error,
      });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, selected) {
    try {
      if (!selected) return null;
      const choice = C();
      if (!choice) throw new Error("Area-save choice runtime is not loaded.");
      const { action, placement } = selected;
      if (action.openingInitiativeOnly
        && !window.IRON_PIT_BROWSER_CHARGE?.openingEligible(round, member, setup)) {
        throw new Error(`${action.name} requires winning initiative on the opening round.`);
      }
      if (choice.prohibitedContext(member, setup, action)) {
        throw new Error(`${action.name} is prohibited by the live environment context.`);
      }
      const actionCost = action.actionCost || "action";
      if (!E().available(member.state, actionCost)) return null;
      if (!choice.resourceAvailable(member.state, action)) {
        throw new Error(`${action.name} resource is unavailable.`);
      }
      const legalPlacements = T().legalPlacements(
        member, setup, action.area, action.range,
        Boolean(action.areaHealingRider) || action.targetScope === "all-other-creatures",
      ).map((row) => choice.eligiblePlacement(member, setup, action, row))
        .filter((row) => row.targetIds.length || action.areaHealingRider);
      if (!legalPlacements.some((row) =>
        JSON.stringify(row.origin) === JSON.stringify(placement.origin)
        && JSON.stringify(row.direction) === JSON.stringify(placement.direction)
        && JSON.stringify(row.targetIds) === JSON.stringify(placement.targetIds))) {
        throw new Error(`${action.name} has a stale or illegal area placement.`);
      }
      const healTarget = choice.healingTarget(
        member, setup, action, placement, !placement.targetIds.length,
      );
      if (action.areaHealingRider && !healTarget) {
        throw new Error(`${action.name} has no legal healing target in its area.`);
      }

      let remaining = null;
      if (action.resourceId) {
        member.state.resources[action.resourceId] -= action.resourceCost || 1;
        remaining = member.state.resources[action.resourceId];
      }
      E().spend(member.state, actionCost);
      const shared = action.damageComponents?.length
        ? action.damageComponents.map((spec) => D().rollMany(spec.diceCount, spec.diceSize))
        : action.damageDiceCount
          ? D().rollMany(action.damageDiceCount, action.damageDiceSize) : null;
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
        events.push(...chain.events);
        sequence = chain.sequence;
      }
      if (healTarget) {
        events.push(resolveHealing(sequence, round, member, healTarget, action, remaining));
        sequence += 1;
      }
      return { events, sequence, placement };
    } catch (error) {
      console.error("Failed browser area-save resolution", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function choose(member, setup, actionCost = null, openingOnly = false, predicate = null) {
    try {
      if (!C()) throw new Error("Area-save choice runtime is not loaded.");
      return C().choose(member, setup, actionCost, openingOnly, predicate);
    } catch (error) {
      console.error("Failed browser area-save choice delegation", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_SAVES = {
    choose, resolve, expectedSaveDamage: (action) => C().expectedSaveDamage(action),
  };
})();
