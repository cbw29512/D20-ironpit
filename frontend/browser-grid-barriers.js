(() => {
  "use strict";

  function edgeKey(first, second) {
    try {
      const a = [first.x, first.y];
      const b = [second.x, second.y];
      const ordered = (a[0] < b[0] || (a[0] === b[0] && a[1] <= b[1])) ? [a, b] : [b, a];
      return `${ordered[0][0]},${ordered[0][1]}|${ordered[1][0]},${ordered[1][1]}`;
    } catch (error) {
      console.error("Failed to resolve browser barrier edge key", { error });
      throw error;
    }
  }

  function blocksTransition(origin, destination, barriers) {
    try {
      if (!origin || !Array.isArray(barriers) || !barriers.length) return false;
      if (Math.abs(origin.x - destination.x) + Math.abs(origin.y - destination.y) !== 1) return false;
      const wanted = edgeKey(origin, destination);
      return barriers.some((barrier) => barrier.blocks_movement !== false
        && Array.isArray(barrier.sections)
        && barrier.sections.some((section) => !section.destroyed
          && (section.current_hp ?? 0) > 0
          && Array.isArray(section.edges)
          && section.edges.some((edge) => edgeKey(edge.first, edge.second) === wanted)));
    } catch (error) {
      console.error("Failed to evaluate browser persistent barrier passage", {
        origin,
        destination,
        error,
      });
      throw error;
    }
  }

  function cleanup(setup, roundNumber) {
    try {
      if (!Array.isArray(setup?.persistent_barriers)) {
        if (setup) setup.persistent_barriers = [];
        return [];
      }
      const members = new Map(
        [...(setup.heroes || []), ...(setup.monsters || [])]
          .map((member) => [member.combatant_id, member]),
      );
      const kept = [], removed = [];
      for (const barrier of setup.persistent_barriers) {
        if ((barrier.sections || []).every((section) => section.destroyed || (section.current_hp ?? 0) <= 0)) {
          removed.push(barrier.barrier_id);
          continue;
        }
        if (roundNumber >= barrier.expires_round) {
          if (barrier.permanent_after_full_duration) {
            barrier.concentration = false;
            barrier.permanent_after_full_duration = false;
            kept.push(barrier);
          } else {
            removed.push(barrier.barrier_id);
          }
          continue;
        }
        if (barrier.concentration) {
          const source = members.get(barrier.source_id);
          const current = source?.state?.concentration || null;
          if (!current || current.source_id !== barrier.source_id || current.effect_id !== barrier.action_id) {
            removed.push(barrier.barrier_id);
            continue;
          }
        }
        kept.push(barrier);
      }
      setup.persistent_barriers = kept;
      return removed;
    } catch (error) {
      console.error("Failed to clean browser persistent barriers", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_BARRIERS = { edgeKey, blocksTransition, cleanup };
})();
