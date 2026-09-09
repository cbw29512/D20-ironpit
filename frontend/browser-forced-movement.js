(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const MIN = 0, MAX = 15, FOOTPRINT = 5;
  const clamp = (position) => Math.min(MAX, Math.max(MIN, position));

  function pushDirection(source, target) {
    if (target.position_ft > source.position_ft) return 1;
    if (target.position_ft < source.position_ft) return -1;
    return target.side === "heroes" ? -1 : 1;
  }

  function destination(source, target, movement) {
    if (!movement) return target.position_ft;
    if (movement.direction === "push") {
      return clamp(target.position_ft + pushDirection(source, target) * movement.maxDistanceFt);
    }
    const distance = Math.abs(source.position_ft - target.position_ft);
    const moved = Math.min(movement.maxDistanceFt, Math.max(0, distance - FOOTPRINT));
    if (!moved) return target.position_ft;
    return clamp(target.position_ft + (source.position_ft > target.position_ft ? 1 : -1) * moved);
  }

  function apply(source, target, control) {
    if (!control?.forcedMovement) return null;
    if (control.maxTargetSize && !S().sizeAtMost(target, control.maxTargetSize)) return null;
    const before = target.position_ft;
    const beforeDistance = Math.abs(source.position_ft - before);
    target.position_ft = destination(source, target, control.forcedMovement);
    return {
      movedFt: Math.abs(target.position_ft - before),
      beforeDistanceFt: beforeDistance,
      afterDistanceFt: Math.abs(source.position_ft - target.position_ft),
      direction: control.forcedMovement.direction,
    };
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { apply, destination };
})();
