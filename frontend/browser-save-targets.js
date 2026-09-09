(() => {
  "use strict";

  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

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
      if (!V().legalAction(action, target, distance)) throw new Error(`${action.name} cannot legally affect ${target.state.template.name}.`);
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

  window.IRON_PIT_BROWSER_SAVE_TARGETS = { resolve, targets };
})();
