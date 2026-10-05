(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function passengers(caster, setup, action) {
    if (!action.passengerCount) return [];
    const allies = caster.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.filter((ally) => ally.combatant_id !== caster.combatant_id
      && ally.state.is_alive && !ally.state.is_dead
      && S().distance(caster, ally) <= (action.passengerRangeFt || 5))
      .sort((a, b) => a.state.current_hp - b.state.current_hp || a.combatant_id.localeCompare(b.combatant_id))
      .slice(0, action.passengerCount);
  }

  function chooseDestination(caster, setup, action) {
    try {
      if (!setup || !action) throw new Error("Teleport destination choice requires a setup and action.");
      if (!caster?.state?.position) return null;
      return { ...caster.state.position };
    } catch (error) {
      console.error("Failed browser teleport destination", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function choose(caster, setup, turnKey) {
    try {
      if (!caster || !setup || !String(turnKey || "").trim()) {
        throw new Error("Teleport choice requires a caster, setup, and turn key.");
      }
      if (!caster.state.position) return null;
      const cancel = window.IRON_PIT_BROWSER_TELEPORT_CANCEL;
      if (!cancel?.cancelableIds(caster.state).length) return null;
      const actions = (caster.state.template.teleport_actions || []).filter((action) =>
        E().available(caster.state, action.actionCost || action.action_cost));
      if (!actions.length) return null;
      const action = actions.slice().sort((a, b) => (a.level - b.level) || String(a.id).localeCompare(b.id))[0];
      return { action, destination: { ...caster.state.position } };
    } catch (error) {
      console.error("Failed browser teleport choice", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, caster, setup, action, destination, turnKey) {
    try {
      if (window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(caster, setup)) {
        throw new Error(`${action.name} cannot be cast inside a Silence effect.`);
      }
      if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
      if (!destination) throw new Error(`${action.name} requires a destination argument.`);
      if (action.expendsSpellSlot) P()?.markSlotSpellCast?.(caster.state, turnKey);
      E().spend(caster.state, action.actionCost);
      if (action.resourceId) caster.state.resources[action.resourceId] -= action.resourceCost || 1;
      const travelers = [caster, ...passengers(caster, setup, action)];
      const origin = { ...caster.state.position };
      const removed = [];
      for (const traveler of travelers) {
        for (const conditionId of (window.IRON_PIT_BROWSER_TELEPORT_CANCEL?.clear(traveler) || [])) {
          if (!removed.includes(conditionId)) removed.push(conditionId);
        }
      }
      const names = removed.map((id) => id.replace(/_/g, " ").replace(/\b\w/g, (ch) => ch.toUpperCase())).join(", ");
      let description = `${caster.state.template.name} uses ${action.name} without leaving its spot.`;
      if (names) description += ` ${names} ends.`;
      return {
        events: [{
          sequence, round_number: round, event_type: "feature",
          actor_id: caster.combatant_id, actor_name: caster.state.template.name,
          feature_id: action.id, removed_condition_ids: removed,
          resource_remaining: action.resourceId ? caster.state.resources[action.resourceId] : null,
          grid_position_before: origin, grid_position_after: origin,
          animation: action.animation || "teleport",
          description,
        }],
        sequence: sequence + 1,
      };
    } catch (error) {
      console.error("Failed browser teleport resolve", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TELEPORT = { choose, chooseDestination, resolve };
})();
