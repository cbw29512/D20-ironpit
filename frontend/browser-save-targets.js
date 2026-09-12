(() => {
  "use strict";

  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const A = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function targets(actor, setup, action, targetIds, skipRangeCheck) {
    if (!targetIds.length || new Set(targetIds).size !== targetIds.length) {
      throw new Error("Multi-target save actions require unique target IDs.");
    }
    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    const expectedSide = actor.side === "heroes" ? "monsters" : "heroes";
    return targetIds.map((targetId) => {
      const target = members.get(targetId);
      if (!target) throw new Error(`Unknown save-action target ${targetId}.`);
      if (target.side !== expectedSide) throw new Error("Offensive Iron Pit save actions cannot target allies.");
      if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) {
        throw new Error(`Save-action target ${targetId} is not active.`);
      }
      const distance = skipRangeCheck ? 0 : S().distance(actor, target);
      if (!V().legalAction(action, target, distance, actor)) throw new Error(`${action.name} cannot legally affect ${target.state.template.name}.`);
      return target;
    });
  }

  function resolve(sequence, round, actor, setup, action, targetIds, options = {}) {
    try {
      const skipRangeCheck = options.skipRangeCheck === true;
      const selected = targets(actor, setup, action, targetIds, skipRangeCheck);
      const events = [];
      let sharedDamageRolls = null;
      for (const target of selected) {
        const capture = sharedDamageRolls == null && (action.damageDiceCount || 0) ? [] : null;
        const event = V().resolveAction(
          sequence++, round, actor, target, action, skipRangeCheck ? 0 : S().distance(actor, target),
          { spendAction: false, spendResourceCost: false, sharedDamageRolls,
            captureSharedDamageRolls: capture, setup },
        );
        events.push(event);
        if (capture) {
          if (capture.length !== (action.damageDiceCount || 0)) throw new Error("Shared damage roll was not fully established.");
          sharedDamageRolls = capture;
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser multi-target save resolution failed", { actor: actor?.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  function samePlacement(first, second) {
    const sameDirection = (!first.direction && !second.direction)
      || (first.direction && second.direction && first.direction[0] === second.direction[0] && first.direction[1] === second.direction[1]);
    return first.targetIds.join("|") === second.targetIds.join("|")
      && first.origin[0] === second.origin[0] && first.origin[1] === second.origin[1] && sameDirection;
  }

  function resolveArea(sequence, round, actor, setup, action, options = {}) {
    try {
      if (!action.area) throw new Error(`${action.name} does not define area geometry.`);
      if (!E().available(actor.state, "action")) throw new Error("Action is unavailable for an area saving-throw action.");
      if (!RES().available(actor.state, action.resourceId, action.resourceCost || 1)) {
        throw new Error(`${action.name} lacks its required resource.`);
      }
      const legal = A().legalPlacements(actor, setup, action.area, action.range);
      if (!legal.length) throw new Error(`${action.name} has no legal area placement.`);
      const requested = options.placement || legal[0];
      const placement = legal.find((item) => samePlacement(item, requested));
      if (!placement) throw new Error(`${action.name} received a stale or illegal area placement.`);
      targets(actor, setup, action, placement.targetIds, true);
      E().spend(actor.state, "action");
      const remaining = RES().spend(actor.state, action.resourceId, action.resourceCost || 1);
      const result = resolve(sequence, round, actor, setup, action, placement.targetIds, { skipRangeCheck: true });
      if (result.events.length) result.events[0].resource_remaining = remaining;
      return { ...result, placement };
    } catch (error) {
      console.error("Browser area save action failed", { actor: actor?.combatant_id, action: action?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SAVE_TARGETS = { resolve, resolveArea, targets };
})();
