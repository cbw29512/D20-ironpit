(() => {
  "use strict";
  // Generic per-sight-line visibility obstruction. Darkness is not Blinded.
  function lineCrosses(observer, target, zone) {
    try {
      const a = observer?.position, b = target?.position, c = zone?.position;
      if (!a || !b || !c) return true; // Unknown sight line: fail closed.
      const dx = b.x - a.x, dy = b.y - a.y;
      const lengthSq = dx * dx + dy * dy;
      const t = lengthSq === 0 ? 0 : Math.max(0, Math.min(1,
        ((c.x - a.x) * dx + (c.y - a.y) * dy) / lengthSq));
      const x = a.x + t * dx, y = a.y + t * dy;
      const radiusCells = zone.radius_ft / 5;
      return (x - c.x) ** 2 + (y - c.y) ** 2 <= radiusCells ** 2;
    } catch (error) {
      console.error("Browser sight-line geometry failed.", error);
      throw error;
    }
  }

  function blocked(observer, target, { truesightReaches = false } = {}) {
    try {
      const zones = (observer?.visible_obscuration_zones?.length
        ? observer.visible_obscuration_zones : target?.visible_obscuration_zones) || [];
      return zones.some((zone) =>
        zone.obscuration_kind !== "none"
        && !(zone.obscuration_kind === "magical-darkness" && truesightReaches)
        && lineCrosses(observer, target, zone));
    } catch (error) {
      console.error("Browser universal obscuration check failed.", error);
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OBSCURATION_VISIBILITY = { blocked, lineCrosses };
})();
