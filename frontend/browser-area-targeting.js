(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const A = () => window.IRON_PIT_BROWSER_AREA_SHAPES;

  function points(member) {
    const position = member.state.position;
    if (!position) throw new Error(`${member.combatant_id} has no authoritative grid position.`);
    return G().occupiedCells(position, member.state.template.size)
      .map(([x, y]) => A().cellCenterFt(x, y));
  }

  function livingOpponents(actor, setup) {
    const pool = actor.side === "heroes" ? setup.monsters : setup.heroes;
    return pool.filter((member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0);
  }

  function directionKey(direction) {
    return `${direction[0].toFixed(12)},${direction[1].toFixed(12)}`;
  }

  function directions(origins, enemies) {
    const rows = new Map();
    for (const origin of origins) {
      const vectors = [];
      for (const enemy of enemies) {
        for (const point of points(enemy)) {
          const direction = A().normalized(point[0] - origin[0], point[1] - origin[1]);
          if (!direction) continue;
          vectors.push(direction); rows.set(directionKey(direction), direction);
        }
      }
      for (let first = 0; first < vectors.length; first += 1) {
        for (let second = first + 1; second < vectors.length; second += 1) {
          const direction = A().normalized(
            vectors[first][0] + vectors[second][0],
            vectors[first][1] + vectors[second][1],
          );
          if (direction) rows.set(directionKey(direction), direction);
        }
      }
    }
    for (const [dx, dy] of [[1,0],[-1,0],[0,1],[0,-1],[1,1],[1,-1],[-1,1],[-1,-1]]) {
      const direction = A().normalized(dx, dy);
      if (direction) rows.set(directionKey(direction), direction);
    }
    return [...rows.values()];
  }

  const dimension = (area, camel, snake) => area[camel] ?? area[snake];
  function hits(area, origins, origin, direction, target) {
    const targetPoints = points(target);
    const radius = dimension(area, "radiusFt", "radius_ft");
    const length = dimension(area, "lengthFt", "length_ft");
    const width = dimension(area, "widthFt", "width_ft");
    if (area.shape === "radius") return targetPoints.some((point) => A().radiusContains(origin, point, radius));
    if (area.shape === "emanation") return targetPoints.some((point) => A().emanationContains(origins, point, radius));
    if (!direction) return false;
    if (area.shape === "cone") return targetPoints.some((point) => A().coneContains(origin, direction, point, length));
    if (area.shape === "line") return targetPoints.some((point) => A().lineContains(origin, direction, point, length, width));
    throw new Error(`Unsupported browser monster area shape: ${area.shape}`);
  }

  function legalPlacements(actor, setup, area) {
    try {
      if (!area || area.origin !== "self") throw new Error("Browser monster area must originate from self.");
      if (!setup.map_definition) throw new Error("Area targeting requires an authoritative battle map.");
      const enemies = livingOpponents(actor, setup);
      if (!enemies.length) return [];
      const origins = points(actor), result = new Map();
      const areaDirections = ["radius", "emanation"].includes(area.shape) ? [null] : directions(origins, enemies);
      for (const origin of origins) {
        for (const direction of areaDirections) {
          const targetIds = enemies
            .filter((enemy) => hits(area, origins, origin, direction, enemy))
            .map((enemy) => enemy.combatant_id);
          if (!targetIds.length) continue;
          const key = targetIds.join("|");
          if (!result.has(key)) result.set(key, { targetIds, origin, direction });
        }
      }
      return [...result.values()].sort((left, right) =>
        right.targetIds.length - left.targetIds.length
        || left.targetIds.join("|").localeCompare(right.targetIds.join("|")));
    } catch (error) {
      console.error("Failed browser area targeting", { actor: actor.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_AREA_TARGETING = { legalPlacements };
})();
