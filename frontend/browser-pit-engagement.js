(() => {
  "use strict";

  const MELEE_ENGAGEMENT_FT = 5;

  function livingEnemies(mover, members) {
    return (members || []).filter((member) => member.combatant_id !== mover.combatant_id
      && member.side !== mover.side
      && member.state?.is_alive !== false
      && !member.state?.is_dead
      && member.state?.position);
  }

  function nearestLivingEnemyDistanceFt(mover, members, origin = null) {
    try {
      const start = origin || mover.state?.position;
      if (!start) return null;
      const geometry = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
      if (!geometry) return null;
      const distances = livingEnemies(mover, members).map((enemy) => geometry.footprintDistanceFt(
        start,
        mover.state.template.size,
        enemy.state.position,
        enemy.state.template.size,
      ));
      return distances.length ? Math.min(...distances) : null;
    } catch (error) {
      console.error("Failed browser nearest-enemy distance", { mover: mover?.combatant_id, error });
      throw error;
    }
  }

  function leavesMelee(mover, members, destination) {
    try {
      const current = nearestLivingEnemyDistanceFt(mover, members);
      if (current == null || current > MELEE_ENGAGEMENT_FT) return false;
      const after = nearestLivingEnemyDistanceFt(mover, members, destination);
      return after != null && after > current;
    } catch (error) {
      console.error("Failed browser melee-engagement lock", { mover: mover?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_PIT_ENGAGEMENT = {
    MELEE_ENGAGEMENT_FT, leavesMelee, nearestLivingEnemyDistanceFt,
  };
})();
