(() => {
  "use strict";
  const SIZES = ["tiny", "small", "medium", "large", "huge", "gargantuan"];
  function resolve(sequence, round, attacker, setup, successfulHits) {
    try {
      const rule = attacker.state.template.attack_action?.hitGrapple;
      if (!rule || !attacker.state.is_alive || attacker.state.is_dead) {
        return { events: [], sequence };
      }
      const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
      if (!grapple?.apply) throw new Error("Multiattack hit trigger requires shared grapple runtime.");
      const members = [...setup.heroes, ...setup.monsters];
      const counts = new Map();
      for (const { attackId, targetId } of successfulHits) {
        if (attackId !== rule.attackId) continue;
        counts.set(targetId, (counts.get(targetId) || 0) + 1);
      }
      const alreadyHeld = members.filter(target =>
        target.combatant_id !== attacker.combatant_id &&
        (target.state.grapple_sources || []).some(held =>
          held.source_id === attacker.combatant_id &&
          (held.linked_condition_ids || []).includes(rule.ownershipMarkerId)),
      ).length;
      if (alreadyHeld >= rule.maxActiveTargets) return { events: [], sequence };
      const maxSize = SIZES.indexOf(rule.maxTargetSize);
      if (maxSize < 0) throw new Error("Multiattack grapple has an unknown size limit.");
      for (const target of members) {
        if ((counts.get(target.combatant_id) || 0) < rule.requiredHits) continue;
        if (target.side === attacker.side || target.state.swallowed
          || !target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) continue;
        const size = SIZES.indexOf(target.state.template.size);
        if (size < 0) throw new Error("Multiattack grapple target size is unsupported.");
        if (size > maxSize) continue;
        if (window.IRON_PIT_BROWSER_STATE.distance(attacker, target) > rule.grappleRangeFt) continue;
        const applied = grapple.apply(
          target.state, attacker.combatant_id, rule.grappleEscapeDc,
          rule.grappleRangeFt, true, false, null, rule.linkedConditionIds,
          Boolean(rule.movesWithSource),
        );
        if (!applied.includes("grappled")) continue;
        return { events: [{
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: rule.sourceName, applied_condition_ids: applied, animation: "feature",
          description: attacker.state.template.name + ": " + rule.sourceName
            + " triggers after " + rule.requiredHits + " successful "
            + rule.attackId + " hits; grappled (escape DC " + rule.grappleEscapeDc
            + "), blinded and restrained.",
        }], sequence };
      }
      return { events: [], sequence };
    } catch (error) {
      console.error("Generic Multiattack hit-grapple failed.", { attacker: attacker?.combatant_id, error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_MULTIATTACK_HIT_GRAPPLE = { resolve };
})();
