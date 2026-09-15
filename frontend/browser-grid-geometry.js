(() => {
  "use strict";

  const FOOTPRINT_SIDE = {
    tiny: 1, small: 1, medium: 1, large: 2, huge: 3, gargantuan: 4,
  };

  function footprintSide(size) {
    try {
      const side = FOOTPRINT_SIDE[size];
      if (!side) throw new Error(`Unsupported creature size: ${size}`);
      return side;
    } catch (error) {
      console.error("Failed to derive grid footprint", { size, error }); throw error;
    }
  }

  function occupiedCells(position, size) {
    try {
      const side = footprintSide(size), cells = [];
      for (let dx = 0; dx < side; dx += 1) for (let dy = 0; dy < side; dy += 1) cells.push([position.x + dx, position.y + dy]);
      return cells;
    } catch (error) {
      console.error("Failed to derive occupied grid cells", { position, size, error }); throw error;
    }
  }

  function inBounds(map, position, size) {
    try {
      const side = footprintSide(size);
      return position.x >= 0 && position.y >= 0 && position.x + side <= map.width_squares && position.y + side <= map.height_squares;
    } catch (error) {
      console.error("Failed to validate grid bounds", { map, position, size, error }); throw error;
    }
  }

  function overlaps(firstPosition, firstSize, secondPosition, secondSize) {
    try {
      const first = new Set(occupiedCells(firstPosition, firstSize).map(([x, y]) => `${x},${y}`));
      return occupiedCells(secondPosition, secondSize).some(([x, y]) => first.has(`${x},${y}`));
    } catch (error) {
      console.error("Failed to test footprint overlap", { error }); throw error;
    }
  }

  function footprintDistanceFt(firstPosition, firstSize, secondPosition, secondSize) {
    try {
      const first = occupiedCells(firstPosition, firstSize), second = occupiedCells(secondPosition, secondSize);
      let minimum = Number.POSITIVE_INFINITY;
      for (const [ax, ay] of first) for (const [bx, by] of second) minimum = Math.min(minimum, Math.max(Math.abs(ax - bx), Math.abs(ay - by)));
      return minimum * 5;
    } catch (error) {
      console.error("Failed to calculate footprint-aware grid distance", { error }); throw error;
    }
  }

  const sign = (value) => Number(value > 0) - Number(value < 0);
  function center(member) {
    if (!member.state.position) throw new Error("Forced movement requires authoritative grid positions.");
    const offset = (footprintSide(member.state.template.size) - 1) / 2;
    return [member.state.position.x + offset, member.state.position.y + offset];
  }
  function occupiedByOther(target, candidate, setup) {
    return [...setup.heroes, ...setup.monsters].some((member) => member.combatant_id !== target.combatant_id
      && member.state.position && !member.state.is_dead
      && overlaps(candidate, target.state.template.size, member.state.position, member.state.template.size));
  }
  function moveRelative(source, target, distanceFt, setup, toward) {
    if (!Number.isInteger(distanceFt) || distanceFt < 0 || distanceFt % 5) throw new Error("Forced movement distance must be a nonnegative 5-foot increment.");
    if (!distanceFt) return 0;
    if (!setup?.map_definition || !target.state.position) throw new Error("Forced movement requires an authoritative battle map and target position.");
    const [sx, sy] = center(source), [tx, ty] = center(target);
    const dx = toward ? sign(sx - tx) : sign(tx - sx), dy = toward ? sign(sy - ty) : sign(ty - sy);
    if (!dx && !dy) throw new Error("Forced movement direction is undefined for overlapping centers.");
    let current = { ...target.state.position }, moved = 0;
    for (let step = 0; step < distanceFt / 5; step += 1) {
      const candidate = { x: current.x + dx, y: current.y + dy };
      if (!inBounds(setup.map_definition, candidate, target.state.template.size) || occupiedByOther(target, candidate, setup)) break;
      current = candidate; moved += 5;
    }
    target.state.position = current; return moved;
  }
  const pushAway = (source, target, distanceFt, setup) => moveRelative(source, target, distanceFt, setup, false);
  const pullToward = (source, target, distanceFt, setup) => moveRelative(source, target, distanceFt, setup, true);

  window.IRON_PIT_BROWSER_GRID_GEOMETRY = { footprintSide, occupiedCells, inBounds, overlaps, footprintDistanceFt };
  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { pushAway, pullToward };
})();
