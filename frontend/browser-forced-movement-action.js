(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function legalTargets(member, setup, action) {
    try {
      if (action.targetMode !== "creatures_grappled_by_self") throw new Error(`Unsupported forced-movement target mode: ${action.targetMode}`);
      const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
      return enemies.filter((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0
        && (target.state.grapple_sources || []).some((source) => source.source_id === member.combatant_id));
    } catch (error) {
      console.error("Failed browser forced-movement target selection", { member: member.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, action) {
    try {
      const events = [];
      for (const target of legalTargets(member, setup, action)) {
        const before = S().distance(member, target);
        const moved = Math.min(action.distanceFt, before);
        if (moved <= 0) continue;
        let sign = target.position_ft >= member.position_ft ? -1 : 1;
        if (action.direction === "away_from_source") sign *= -1;
        target.position_ft = Math.max(0, target.position_ft + sign * moved);
        const after = S().distance(member, target);
        const direction = action.direction === "toward_source" ? "toward" : "away from";
        events.push({
          sequence: sequence++, round_number: round, event_type: "movement",
          actor_id: member.combatant_id, actor_name: member.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          attack_name: action.name, distance_before_ft: before, distance_after_ft: after,
          movement_ft: moved, animation: action.animation,
          description: `${member.state.template.name} uses ${action.name}, moving ${target.state.template.name} ${moved} ft. ${direction} itself.`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser forced-movement action failed", { member: member.combatant_id, action: action.id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT_ACTION = { legalTargets, resolve };
})();
