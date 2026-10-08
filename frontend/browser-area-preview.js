(() => {
  "use strict";

  const COLORS = Object.freeze({
    fire: "#f45b45", lightning: "#f1f7ff", cold: "#98e4fa",
    necrotic: "#423050", poison: "#76bf63", radiant: "#f3cb66",
    psychic: "#b4a5ce", charm: "#aeb0b8", neutral: "#aeb0b8",
  });

  function cellsForArea(map, area, placement, casterOrigins = []) {
    const shapes = window.IRON_PIT_BROWSER_AREA_SHAPES;
    if (!shapes) throw new Error("Shared area geometry is required.");
    if (!map || !area || !placement?.origin) throw new Error("Missing area placement.");
    const origin = placement.origin;
    const direction = placement.direction;
    const dimension = (camel, snake) => area[camel] ?? area[snake];
    const radius = dimension("radiusFt", "radius_ft");
    const length = dimension("lengthFt", "length_ft");
    const width = dimension("widthFt", "width_ft");
    const cells = [];
    for (let y = 0; y < map.height_squares; y += 1) {
      for (let x = 0; x < map.width_squares; x += 1) {
        const point = shapes.cellCenterFt(x, y);
        let inside = false;
        switch (area.shape) {
          case "radius": inside = shapes.radiusContains(origin, point, radius); break;
          case "emanation": inside = shapes.emanationContains(casterOrigins, point, radius); break;
          case "line": inside = Boolean(direction) && shapes.lineContains(origin, direction, point, length, width); break;
          case "cone": inside = Boolean(direction) && shapes.coneContains(origin, direction, point, length); break;
          case "cube": inside = Boolean(direction) && shapes.cubeContains(origin, direction, point, length); break;
          default: throw new Error(`Preview shape not yet supported: ${area.shape}`);
        }
        if (inside) cells.push({ x, y });
      }
    }
    return cells;
  }

  function preview(map, area, placement, options = {}) {
    return {
      shape: area.shape,
      color: COLORS[options.flavor] || COLORS.neutral,
      cells: cellsForArea(map, area, placement, options.casterOrigins || []),
      targetIds: [...(placement.targetIds || placement.enemyIds || [])],
      friendlyIds: [...(placement.friendlyIds || [])],
      persistent: Boolean(options.persistent),
    };
  }
  window.IRON_PIT_BROWSER_AREA_PREVIEW = { COLORS, cellsForArea, preview };
})();
