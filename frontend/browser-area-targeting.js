(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_AREA_SHAPES;

  function points(member, position = null) {
    const authoritative = position || member?.state?.position;
    if (!authoritative) throw new Error(`${member?.combatant_id || "combatant"} has no authoritative grid position.`);
    return G().occupiedCells(authoritative, member.state.template.size).map(([x, y]) => S().cellCenterFt(x, y));
  }
  function livingOpponents(actor, setup) {
    const rows = actor.side === "heroes" ? setup.monsters : setup.heroes;
    return rows.filter((row) => row.state.is_alive && !row.state.is_dead && row.state.current_hp > 0);
  }
  function directionKey(direction) { return `${direction[0].toFixed(12)},${direction[1].toFixed(12)}`; }
  function directions(origins, enemies) {
    const values = new Map();
    for (const origin of origins) {
      const vectors = [];
      for (const enemy of enemies) {
        for (const point of points(enemy)) {
          const direction = S().normalized(point[0] - origin[0], point[1] - origin[1]);
          if (direction) { vectors.push(direction); values.set(directionKey(direction), direction); }
        }
      }
      for (let i = 0; i < vectors.length; i += 1) {
        for (let j = i + 1; j < vectors.length; j += 1) {
          const direction = S().normalized(vectors[i][0] + vectors[j][0], vectors[i][1] + vectors[j][1]);
          if (direction) values.set(directionKey(direction), direction);
        }
      }
    }
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]) {
      const direction = S().normalized(dx, dy); values.set(directionKey(direction), direction);
    }
    return [...values.values()].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  }
  function hits(area, actorPoints, origin, direction, target) {
    const targetPoints = points(target);
    if (area.shape === "radius") return targetPoints.some((point) => S().radiusContains(origin, point, area.radiusFt));
    if (area.shape === "emanation") return targetPoints.some((point) => S().emanationContains(actorPoints, point, area.radiusFt));
    if (!direction) return false;
    if (area.shape === "cone") return targetPoints.some((point) => S().coneContains(origin, direction, point, area.lengthFt));
    if (area.shape === "line") return targetPoints.some((point) => S().lineContains(origin, direction, point, area.lengthFt, area.widthFt));
    throw new Error(`Unsupported area shape: ${area.shape}`);
  }
  function pointOrigins(actor, setup, range, actorPosition = null) {
    const map = setup.map_definition;
    if (!map) throw new Error("Area targeting requires an authoritative battle map.");
    const actorPoints = points(actor, actorPosition), result = [];
    for (let x = 0; x < map.width_squares; x += 1) {
      for (let y = 0; y < map.height_squares; y += 1) {
        const point = S().cellCenterFt(x, y);
        const distance = Math.min(...actorPoints.map((source) => Math.max(Math.abs(point[0] - source[0]), Math.abs(point[1] - source[1]))));
        if (distance <= range) result.push(point);
      }
    }
    return result;
  }
  function legalPlacements(actor, setup, area, range, actorPosition = null) {
    try {
      const enemies = livingOpponents(actor, setup);
      if (!enemies.length) return [];
      const actorPoints = points(actor, actorPosition);
      const origins = area.origin === "point" ? pointOrigins(actor, setup, range, actorPosition) : actorPoints;
      const facing = ["radius", "emanation"].includes(area.shape) ? [null] : directions(actorPoints, enemies);
      const unique = new Map();
      for (const origin of origins) {
        for (const direction of facing) {
          const targetIds = enemies.filter((enemy) => hits(area, actorPoints, origin, direction, enemy)).map((enemy) => enemy.combatant_id);
          if (!targetIds.length) continue;
          const key = targetIds.join("|");
          if (!unique.has(key)) unique.set(key, { targetIds, origin: [...origin], direction: direction ? [...direction] : null });
        }
      }
      return [...unique.values()].sort((a, b) => b.targetIds.length - a.targetIds.length
        || a.targetIds.join("|").localeCompare(b.targetIds.join("|"))
        || a.origin[0] - b.origin[0] || a.origin[1] - b.origin[1]);
    } catch (error) {
      console.error("Failed universal browser area targeting", { actor: actor?.combatant_id, error }); throw error;
    }
  }
  window.IRON_PIT_BROWSER_AREA_TARGETING = { legalPlacements, points };
})();
