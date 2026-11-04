(() => {
  "use strict";

  // Use the same action economy and movement ledger as all other combat features.
  const A = () => window.IRON_PIT_BROWSER_ATTACHMENTS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const participants = (setup) => [...setup.heroes, ...setup.monsters];
  const findLink = (setup, sourceId, effectId) =>
    (setup.attachments || []).find((row) =>
      row.source_id === sourceId && row.effect_id === effectId);

  function removeByAction(setup, actor, sourceId, effectId) {
    try {
      const link = findLink(setup, sourceId, effectId);
      if (!link) return false;
      if (!link.action_removable || !E()?.available(actor.state, "action")) return false;
      const source = participants(setup).find((row) => row.combatant_id === sourceId);
      if (!source) throw Error("Attachment source is missing.");
      if (actor.combatant_id !== link.target_id && S().distance(actor, source) > link.action_removal_range_ft) return false;
      E().spend(actor.state, "action");
      setup.attachments = A().detach(setup.attachments, sourceId, effectId);
      return true;
    } catch (error) {
      console.error("Action attachment removal failed", { sourceId, effectId, error });
      throw error;
    }
  }

  function detachWithMovement(setup, source, effectId) {
    try {
      const link = findLink(setup, source.combatant_id, effectId);
      if (!link) return false;
      const cost = link.source_detach_movement_ft;
      if (!Number.isInteger(cost) || cost <= 0 || source.state.is_dead || !source.state.is_alive) {
        return false;
      }
      if ((source.state.movement_remaining_ft || 0) < cost) return false;
      if (!E()?.voluntaryActivityAvailable(source.state, "movement")) return false;
      E().claimActivity(source.state, "movement");
      source.state.movement_remaining_ft -= cost;
      setup.attachments = A().detach(setup.attachments, source.combatant_id, effectId);
      return true;
    } catch (error) {
      console.error("Source attachment movement removal failed", { source: source.combatant_id, error });
      throw error;
    }
  }

  function resolveBlockedSource(sequence, round, setup, source) {
    try {
      const candidates = (setup.attachments || [])
        .filter((link) => link.source_id === source.combatant_id
          && link.blocks_source_attacks && link.source_detach_movement_ft > 0)
        .sort((left, right) => left.source_detach_movement_ft - right.source_detach_movement_ft
          || left.effect_id.localeCompare(right.effect_id)
          || left.target_id.localeCompare(right.target_id));
      for (const link of candidates) {
        const movementBefore = source.state.movement_remaining_ft || 0;
        if (!detachWithMovement(setup, source, link.effect_id)) continue;
        const spent = movementBefore - source.state.movement_remaining_ft;
        return {
          sequence, round_number: round, event_type: "feature",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: link.target_id, feature_id: link.source_name,
          movement_ft: spent, animation: "movement",
          attachment_changes: [{
            operation: "detach", source_id: link.source_id, target_id: link.target_id,
            effect_id: link.effect_id, source_name: link.source_name,
          }],
          description: `${source.state.template.name} spends ${spent} feet of movement to detach ${link.source_name}.`,
        };
      }
      return null;
    } catch (error) {
      console.error("Blocked-source movement detachment failed", {
        source: source.combatant_id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACHMENT_REMOVAL = {
    removeByAction, detachWithMovement, resolveBlockedSource,
  };
})();
