(() => {
  "use strict";

  const EPSILON = 1e-9;

  function cellCenterFt(x, y) {
    return [(x + 0.5) * 5, (y + 0.5) * 5];
  }

  function normalized(dx, dy) {
    const magnitude = Math.hypot(dx, dy);
    if (magnitude <= EPSILON) return null;
    return [dx / magnitude, dy / magnitude];
  }

  function projection(origin, direction, point) {
    const vx = point[0] - origin[0], vy = point[1] - origin[1];
    return {
      forward: vx * direction[0] + vy * direction[1],
      sideways: Math.abs(vx * direction[1] - vy * direction[0]),
    };
  }

  function lineContains(origin, direction, point, lengthFt, widthFt) {
    const { forward, sideways } = projection(origin, direction, point);
    return forward >= -EPSILON && forward <= lengthFt + EPSILON
      && sideways <= widthFt / 2 + EPSILON;
  }

  function coneContains(origin, direction, point, lengthFt) {
    const { forward, sideways } = projection(origin, direction, point);
    if (forward < -EPSILON || forward > lengthFt + EPSILON) return false;
    return sideways <= forward / 2 + EPSILON;
  }

  window.IRON_PIT_BROWSER_AREA_SHAPES = {
    cellCenterFt,
    normalized,
    lineContains,
    coneContains,
  };
})();
