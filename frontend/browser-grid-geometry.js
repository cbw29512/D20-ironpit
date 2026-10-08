(() => {
  "use strict";

  // Pit magic: all creature sizes occupy exactly one 5-foot square.
  const FOOTPRINT_SIDE = {
    tiny: 1,
    small: 1,
    medium: 1,
    large: 1,
    huge: 1,
    gargantuan: 1,
  };

  function footprintSide(size) {
    try {
      const side = FOOTPRINT_SIDE[size];
      if (!side) throw new Error(`Unsupported creature size: ${size}`);
      return side;
    } catch (error) {
      console.error("Failed to derive grid footprint", { size, error });
      throw error;
    }
  }

  function occupiedCells(position, size) {
    try {
      const side = footprintSide(size);
      const cells = [];
      for (let dx = 0; dx < side; dx += 1) {
        for (let dy = 0; dy < side; dy += 1) {
          cells.push([position.x + dx, position.y + dy]);
        }
      }
      return cells;
    } catch (error) {
      console.error("Failed to derive occupied grid cells", { position, size, error });
      throw error;
    }
  }

  function inBounds(map, position, size) {
    try {
      const side = footprintSide(size);
      return position.x >= 0 && position.y >= 0
        && position.x + side <= map.width_squares
        && position.y + side <= map.height_squares;
    } catch (error) {
      console.error("Failed to validate grid bounds", { map, position, size, error });
      throw error;
    }
  }

  function overlaps(firstPosition, firstSize, secondPosition, secondSize) {
    try {
      const first = new Set(occupiedCells(firstPosition, firstSize).map(([x, y]) => `${x},${y}`));
      return occupiedCells(secondPosition, secondSize).some(([x, y]) => first.has(`${x},${y}`));
    } catch (error) {
      console.error("Failed to test footprint overlap", { error });
      throw error;
    }
  }

  function footprintDistanceFt(firstPosition, firstSize, secondPosition, secondSize) {
    try {
      const first = occupiedCells(firstPosition, firstSize);
      const second = occupiedCells(secondPosition, secondSize);
      let minimum = Number.POSITIVE_INFINITY;
      for (const [ax, ay] of first) {
        for (const [bx, by] of second) {
          minimum = Math.min(minimum, Math.max(Math.abs(ax - bx), Math.abs(ay - by)));
        }
      }
      return minimum * 5;
    } catch (error) {
      console.error("Failed to calculate footprint-aware grid distance", { error });
      throw error;
    }
  }

  // Effect areas retain their printed dimensions. The one-square Pit override
  // applies to creatures only, never to zones, hazards, or spell geometry.
  const EFFECT_SIDE = { tiny: 1, small: 1, medium: 1, large: 2, huge: 3, gargantuan: 4 };
  function effectSquareSide(size) {
    const side = EFFECT_SIDE[size];
    if (!side) throw new Error(`Unsupported effect footprint size: ${size}`);
    return side;
  }
  function squareAreaCells(position, side) {
    if (!Number.isInteger(side) || side < 1) throw new Error("Area side must be a positive square count.");
    const cells = [];
    for (let dx = 0; dx < side; dx += 1) {
      for (let dy = 0; dy < side; dy += 1) cells.push([position.x + dx, position.y + dy]);
    }
    return cells;
  }
  function squareAreaInBounds(map, position, side) {
    if (!Number.isInteger(side) || side < 1) throw new Error("Area side must be a positive square count.");
    return position.x >= 0 && position.y >= 0
      && position.x + side <= map.width_squares
      && position.y + side <= map.height_squares;
  }
  function squareAreaDistanceFt(firstPosition, firstSide, secondPosition, secondSide) {
    let minimum = Number.POSITIVE_INFINITY;
    for (const [ax, ay] of squareAreaCells(firstPosition, firstSide)) {
      for (const [bx, by] of squareAreaCells(secondPosition, secondSide)) {
        minimum = Math.min(minimum, Math.max(Math.abs(ax - bx), Math.abs(ay - by)));
      }
    }
    return minimum * 5;
  }

  window.IRON_PIT_BROWSER_GRID_GEOMETRY = {
    footprintSide,
    occupiedCells,
    inBounds,
    overlaps,
    footprintDistanceFt,
    effectSquareSide, squareAreaCells, squareAreaInBounds, squareAreaDistanceFt,
  };
})();
