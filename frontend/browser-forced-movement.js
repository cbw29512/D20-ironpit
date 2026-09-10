(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;

  function applyAttackPush(attacker, target, attack, hit) {
    try {
      const distance = Number(attack?.pushTargetAwayFt || 0);
      if (!hit || distance <= 0 || !target?.state?.is_alive || target.state.is_dead) return 0;
      const maximum = attack.pushTargetMaxSize || null;
      if (maximum && !S().sizeAtMost(target, maximum)) return 0;

      const direction = target.position_ft >= attacker.position_ft ? 1 : -1;
      const destination = Math.max(0, target.position_ft + direction * distance);
      const moved = Math.abs(destination - target.position_ft);
      target.position_ft = destination;
      return moved;
    } catch (error) {
      console.error("Forced movement resolution failed.", error);
      throw new Error("Forced movement resolution failed.");
    }
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { applyAttackPush };
})();
