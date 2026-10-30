(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const AS = () => window.IRON_PIT_BROWSER_AREA_SAVES;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function resourceIds(member) {
    try {
      return new Set((member.state.template.recharge_rules || [])
        .map((rule) => rule.resourceId));
    } catch (error) {
      console.error("Failed browser Recharge resource discovery", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function isRecharge(member, action) {
    try {
      return Boolean(action?.resourceId && resourceIds(member).has(action.resourceId));
    } catch (error) {
      console.error("Failed browser Recharge action classification", {
        member: member.combatant_id, action: action?.id, error,
      });
      throw error;
    }
  }

  function attackIds(member) {
    try {
      return (member.state.template.attacks || [])
        .filter((attack) => isRecharge(member, attack))
        .map((attack) => attack.id);
    } catch (error) {
      console.error("Failed browser Recharge attack discovery", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function legalSave(member, setup) {
    try {
      if (!E().available(member.state, "action")) return null;
      for (const target of F().targetOrder(member, setup)) {
        for (const action of member.state.template.saving_throw_actions || []) {
          if (!isRecharge(member, action)
            || (action.actionCost || "action") !== "action" || action.area) continue;
          if (action.resourceId
            && !R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
          const distance = F().saveDistance(member, target, action.range);
          if (V().legalAction(action, target, distance, member.combatant_id, member)) {
            return { action, target, distance };
          }
        }
      }
      return null;
    } catch (error) {
      console.error("Failed browser Recharge save legality", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function legalArea(member, setup) {
    try {
      if (!E().available(member.state, "action")) return null;
      return AS()?.choose(
        member, setup, "action", false, (action) => isRecharge(member, action),
      ) || null;
    } catch (error) {
      console.error("Failed browser Recharge area-save legality", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function legalAttack(member, setup) {
    try {
      const ids = attackIds(member);
      return ids.length ? F().chooseAttack(member, setup, ids) : null;
    } catch (error) {
      console.error("Failed browser Recharge attack legality", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function families(member, setup) {
    try {
      return [
        legalArea(member, setup) ? "area-save" : null,
        legalSave(member, setup) ? "save-action" : null,
        legalAttack(member, setup) ? "standard-attack" : null,
      ].filter(Boolean);
    } catch (error) {
      console.error("Failed browser Recharge family discovery", {
        member: member.combatant_id, error,
      });
      throw error;
    }
  }

  function score(member, setup, action) {
    try {
      if (!isRecharge(member, action)) return null;
      const active = [...new Set(families(member, setup))];
      if (active.length > 1) {
        throw new Error(
          "Multiple legal Recharge Action families require explicit source-priority policy.",
        );
      }
      return Number.POSITIVE_INFINITY;
    } catch (error) {
      console.error("Failed browser Recharge priority scoring", {
        member: member.combatant_id, action: action?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RECHARGE_ACTION_PRIORITY = {
    attackIds, isRecharge, legalArea, legalAttack, legalSave, score,
  };
})();
