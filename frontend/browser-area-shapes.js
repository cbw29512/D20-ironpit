(() => {
  "use strict";

  const EPSILON = 1e-9;
  const cellCenterFt = (x, y) => [(x + 0.5) * 5, (y + 0.5) * 5];

  function normalized(dx, dy) {
    const magnitude = Math.hypot(dx, dy);
    return magnitude <= EPSILON ? null : [dx / magnitude, dy / magnitude];
  }

  const radiusContains = (origin, point, radius) => Math.hypot(point[0] - origin[0], point[1] - origin[1]) <= radius + EPSILON;
  const emanationContains = (origins, point, radius) => origins.some((origin) => radiusContains(origin, point, radius));

  function projection(origin, direction, point) {
    const vx = point[0] - origin[0], vy = point[1] - origin[1];
    return [vx * direction[0] + vy * direction[1], Math.abs(vx * direction[1] - vy * direction[0])];
  }

  function lineContains(origin, direction, point, length, width) {
    const [forward, sideways] = projection(origin, direction, point);
    return forward >= -EPSILON && forward <= length + EPSILON && sideways <= width / 2 + EPSILON;
  }

  function coneContains(origin, direction, point, length) {
    const [forward, sideways] = projection(origin, direction, point);
    return forward >= -EPSILON && forward <= length + EPSILON && sideways <= forward / 2 + EPSILON;
  }

  window.IRON_PIT_BROWSER_AREA_SHAPES = {
    cellCenterFt, normalized, radiusContains, emanationContains, lineContains, coneContains,
  };
})();
