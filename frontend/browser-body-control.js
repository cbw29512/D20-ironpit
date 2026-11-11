(() => {
  "use strict";
  // Generic link bookkeeping only. No turn-control or targeting bypass.
  function begin(ownerId, owner, hostId, host, options) {
    try {
      if (!options?.failedSave) return false;
      if (ownerId === hostId || host.controlled_by || (owner.controlling_target_ids || []).length) return false;
      if (!owner.is_alive || owner.is_dead || owner.current_hp <= 0
        || !host.is_alive || host.is_dead || host.current_hp <= 0) return false;
      if (!options.sourceActionId || !options.sourceName
        || !Number.isInteger(options.roundNumber) || options.roundNumber < 1)
        throw new Error("Body-control source parameters are incomplete.");
      const link = {
        source_id: ownerId, source_action_id: options.sourceActionId,
        source_name: options.sourceName, host_id: hostId,
        started_round: options.roundNumber,
      };
      host.controlled_by = link;
      (owner.controlling_target_ids ||= []).push(hostId);
      return true;
    } catch (error) {
      console.error("Body-control link start failed", { ownerId, hostId, error });
      throw error;
    }
  }
  function end(ownerId, owner, hostId, host) {
    try {
      if (!host.controlled_by || host.controlled_by.source_id !== ownerId
        || host.controlled_by.host_id !== hostId) return false;
      if (!(owner.controlling_target_ids || []).includes(hostId))
        throw new Error("Body-control link has no matching source ownership.");
      owner.controlling_target_ids = owner.controlling_target_ids.filter(id => id !== hostId);
      host.controlled_by = null;
      return true;
    } catch (error) {
      console.error("Body-control link release failed", { ownerId, hostId, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_BODY_CONTROL = { begin, end };
})();
