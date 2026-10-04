(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const A = () => window.IRON_PIT_BROWSER_AREA_SHAPES;

  function spanOf(area) {
    const length = area.lengthFt ?? area.length_ft;
    if (!length || length % 5) throw new Error("Contiguous cubes require a 5-foot cube length.");
    return length / 5;
  }

  function cubeCenter(sw, span) {
    return [(sw[0] + span / 2) * 5, (sw[1] + span / 2) * 5];
  }

  function inRange(actorPoints, sw, span, rangeFt) {
    const center = cubeCenter(sw, span);
    return actorPoints.some((source) => Math.max(
      Math.abs(center[0] - source[0]), Math.abs(center[1] - source[1]),
    ) <= rangeFt);
  }

  function covers(sw, span, member) {
    if (!member.state.position) return false;
    return G().occupiedCells(member.state.position, member.state.template.size)
      .some(([x, y]) => x >= sw[0] && x < sw[0] + span && y >= sw[1] && y < sw[1] + span);
  }

  function adjacent(selected, span) {
    const found = new Set();
    for (const [sx, sy] of selected) {
      for (const [dx, dy] of [[span, 0], [-span, 0], [0, span], [0, -span]]) {
        found.add(`${sx + dx},${sy + dy}`);
      }
    }
    for (const key of selected) found.delete(`${key[0]},${key[1]}`);
    return [...found].map((key) => key.split(",").map(Number));
  }

  function legalPlacements(actor, setup, area, rangeFt) {
    try {
      if (!setup.map_definition) throw new Error("Contiguous cube targeting requires a battle map.");
      const span = spanOf(area);
      const maxCubes = area.contiguousSectionCount || area.contiguous_section_count || 1;
      const actorPoints = G().occupiedCells(actor.state.position, actor.state.template.size)
        .map(([x, y]) => A().cellCenterFt(x, y));
      const enemies = (actor.side === "heroes" ? setup.monsters : setup.heroes)
        .filter((row) => row.state.is_alive && !row.state.is_dead && row.state.current_hp > 0);
      const friends = (actor.side === "heroes" ? setup.heroes : setup.monsters)
        .filter((row) => row.combatant_id !== actor.combatant_id && row.state.is_alive && !row.state.is_dead);
      const legal = new Set();
      const covering = new Map();
      const friendly = new Map();
      const width = setup.map_definition.width_squares;
      const height = setup.map_definition.height_squares;
      for (let sx = 0; sx <= width - span; sx += 1) {
        for (let sy = 0; sy <= height - span; sy += 1) {
          const sw = [sx, sy];
          if (!inRange(actorPoints, sw, span, rangeFt)) continue;
          legal.add(`${sx},${sy}`);
          const hits = enemies.filter((enemy) => covers(sw, span, enemy)).map((enemy) => enemy.combatant_id);
          if (hits.length) covering.set(`${sx},${sy}`, hits);
          const allyHits = friends.filter((ally) => covers(sw, span, ally)).map((ally) => ally.combatant_id);
          if (allyHits.length) friendly.set(`${sx},${sy}`, allyHits);
        }
      }
      const placements = [];
      const seeds = [...covering.keys()].sort((left, right) =>
        covering.get(right).length - covering.get(left).length || left.localeCompare(right));
      for (const seed of seeds.slice(0, 16)) {
        const selected = new Set([seed]);
        const covered = new Set(covering.get(seed));
        const exposed = new Set(friendly.get(seed) || []);
        while (selected.size < maxCubes) {
          let best = null;
          let bestGain = -1;
          for (const [cx, cy] of adjacent([...selected].map((key) => key.split(",").map(Number)), span)) {
            const key = `${cx},${cy}`;
            if (!legal.has(key)) continue;
            const gain = (covering.get(key) || []).filter((id) => !covered.has(id)).length;
            if (gain > bestGain) {
              best = key;
              bestGain = gain;
            }
          }
          if (!best || bestGain < 0) break;
          selected.add(best);
          for (const id of covering.get(best) || []) covered.add(id);
          for (const id of friendly.get(best) || []) exposed.add(id);
        }
        const cubes = [...selected].map((key) => key.split(",").map(Number)).sort();
        placements.push({
          targetIds: [...covered].sort(),
          enemyIds: [...covered].sort(),
          friendlyIds: [...exposed].sort(),
          origin: cubeCenter(cubes[0], span),
          direction: null,
          cubeSwCells: cubes,
        });
      }
      return placements.sort((left, right) =>
        right.targetIds.length - left.targetIds.length || left.friendlyIds.length - right.friendlyIds.length);
    } catch (error) {
      console.error("Failed contiguous-cube placement", { actor: actor?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_CONTIGUOUS_CUBES = { legalPlacements, covers, spanOf };
})();
