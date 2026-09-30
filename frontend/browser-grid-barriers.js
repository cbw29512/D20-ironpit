(() => {
  "use strict";

  function edgeKey(first, second) {
    try {
      const a = [first.x, first.y], b = [second.x, second.y];
      const ordered = (a[0] < b[0] || (a[0] === b[0] && a[1] <= b[1])) ? [a, b] : [b, a];
      return `${ordered[0][0]},${ordered[0][1]}|${ordered[1][0]},${ordered[1][1]}`;
    } catch (error) {
      console.error("Failed to resolve browser barrier edge key", { error }); throw error;
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
      console.error("Failed browser persistent barrier passage", { origin, destination, error }); throw error;
    }
  }

  function edgeVertices(edge) {
    const a = edge.first, b = edge.second;
    if (a.y === b.y) {
      const x = Math.max(a.x, b.x);
      return [[x * 5, a.y * 5], [x * 5, (a.y + 1) * 5]];
    }
    const y = Math.max(a.y, b.y);
    return [[a.x * 5, y * 5], [(a.x + 1) * 5, y * 5]];
  }

  const orient = (a, b, c) => (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
  const onSegment = (a, b, c) => (
    Math.min(a[0], c[0]) <= b[0] && b[0] <= Math.max(a[0], c[0])
    && Math.min(a[1], c[1]) <= b[1] && b[1] <= Math.max(a[1], c[1])
  );

  function intersects(a, b, c, d) {
    const o1 = orient(a, b, c), o2 = orient(a, b, d), o3 = orient(c, d, a), o4 = orient(c, d, b);
    if (((o1 > 0 && o2 < 0) || (o1 < 0 && o2 > 0))
      && ((o3 > 0 && o4 < 0) || (o3 < 0 && o4 > 0))) return true;
    return (o1 === 0 && onSegment(a, c, b)) || (o2 === 0 && onSegment(a, d, b))
      || (o3 === 0 && onSegment(c, a, d)) || (o4 === 0 && onSegment(c, b, d));
  }

  function sightSegments(barriers) {
    const result = [];
    for (const barrier of barriers || []) {
      if (barrier.blocks_line_of_sight === false || barrier.blocksLineOfSight === false) continue;
      for (const section of barrier.sections || []) {
        if (section.destroyed || (section.current_hp ?? 0) <= 0) continue;
        for (const edge of section.edges || []) result.push(edgeVertices(edge));
      }
    }
    return result;
  }

  function clearBetweenPoints(sources, targets, barriers) {
    try {
      const segments = sightSegments(barriers);
      if (!segments.length) return true;
      return sources.some((source) => targets.some((target) =>
        !segments.some(([first, second]) => intersects(source, target, first, second))));
    } catch (error) {
      console.error("Failed browser barrier line of effect", { error }); throw error;
    }
  }

  function memberPoints(member) {
    try {
      const cells = window.IRON_PIT_BROWSER_GRID_GEOMETRY.occupiedCells(
        member.state.position, member.state.template.size,
      );
      return cells.map(([x, y]) => [(x + 0.5) * 5, (y + 0.5) * 5]);
    } catch (error) {
      console.error("Failed browser barrier sight points", { member: member?.combatant_id, error }); throw error;
    }
  }

  function clearBetweenMembers(source, target, setup) {
    return clearBetweenPoints(memberPoints(source), memberPoints(target), setup?.persistent_barriers || []);
  }

  function cleanup(setup, roundNumber) {
    try {
      if (!Array.isArray(setup?.persistent_barriers)) {
        if (setup) setup.persistent_barriers = [];
        return [];
      }
      const members = new Map([...(setup.heroes || []), ...(setup.monsters || [])]
        .map((member) => [member.combatant_id, member]));
      const kept = [], removed = [];
      for (const barrier of setup.persistent_barriers) {
        if ((barrier.sections || []).every((section) => section.destroyed || (section.current_hp ?? 0) <= 0)) {
          removed.push(barrier.barrier_id); continue;
        }
        if (roundNumber >= barrier.expires_round) {
          if (barrier.permanent_after_full_duration) {
            barrier.concentration = false; barrier.permanent_after_full_duration = false; kept.push(barrier);
          } else removed.push(barrier.barrier_id);
          continue;
        }
        if (barrier.concentration) {
          const current = members.get(barrier.source_id)?.state?.concentration || null;
          if (!current || current.source_id !== barrier.source_id || current.effect_id !== barrier.action_id) {
            removed.push(barrier.barrier_id); continue;
          }
        }
        kept.push(barrier);
      }
      setup.persistent_barriers = kept;
      return removed;
    } catch (error) {
      console.error("Failed to clean browser persistent barriers", { error }); throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_BARRIERS = {
    edgeKey, blocksTransition, clearBetweenPoints, clearBetweenMembers, memberPoints, cleanup,
  };
})();
