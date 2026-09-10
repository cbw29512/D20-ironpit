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

  function installAttackHook() {
    try {
      const engine = window.IRON_PIT_BROWSER_ATTACK;
      if (!engine?.resolveAttack || engine.__forcedMovementHookInstalled) return false;
      const baseResolveAttack = engine.resolveAttack.bind(engine);
      engine.resolveAttack = function resolveAttackWithForcedMovement(
        sequence, round, attacker, target, attack, distance, extra = {},
      ) {
        const event = baseResolveAttack(sequence, round, attacker, target, attack, distance, extra);
        const members = extra.setup ? [...extra.setup.heroes, ...extra.setup.monsters] : [target];
        const actualTarget = members.find((member) => member.combatant_id === event.target_id) || target;
        const moved = applyAttackPush(attacker, actualTarget, attack, event.hit === true);
        if (moved > 0) {
          event.description += ` ${actualTarget.state.template.name} is pushed ${moved} feet straight away.`;
        }
        return event;
      };
      engine.__forcedMovementHookInstalled = true;
      return true;
    } catch (error) {
      console.error("Forced movement attack hook installation failed.", error);
      throw new Error("Forced movement attack hook installation failed.");
    }
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { applyAttackPush, installAttackHook };
  installAttackHook();
})();
