(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const L = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || {
    resolveCleave: (sequence) => ({ events: [], sequence }),
  };

  function eligible(target, maximum) {
    if (!target?.state?.is_alive || target.state.is_dead) return false;
    return !maximum || S().sizeAtMost(target, maximum);
  }

  function applyAttackPush(attacker, target, attack, hit) {
    try {
      const distance = Number(attack?.pushTargetAwayFt || 0);
      if (!hit || distance <= 0 || !eligible(target, attack.pushTargetMaxSize || null)) return 0;
      const direction = target.position_ft >= attacker.position_ft ? 1 : -1;
      const destination = Math.max(0, target.position_ft + direction * distance);
      const moved = Math.abs(destination - target.position_ft);
      target.position_ft = destination;
      return moved;
    } catch (error) {
      console.error("Forced attack push failed.", error);
      throw new Error("Forced push resolution failed.");
    }
  }

  function applyAttackPull(attacker, target, attack, hit) {
    try {
      const distance = Number(attack?.pullTargetTowardFt || 0);
      if (!hit || distance <= 0 || !eligible(target, attack.pullTargetMaxSize || null)) return 0;
      const separation = Math.abs(target.position_ft - attacker.position_ft);
      const moved = Math.min(distance, separation);
      if (moved <= 0) return 0;
      const direction = target.position_ft >= attacker.position_ft ? -1 : 1;
      target.position_ft = Math.max(0, target.position_ft + direction * moved);
      return moved;
    } catch (error) {
      console.error("Forced attack pull failed.", error);
      throw new Error("Forced pull resolution failed.");
    }
  }

  function installForcedMovementHook() {
    try {
      const engine = A();
      if (!engine?.resolveAttack || engine.__forcedMovementHookInstalled) return;
      const baseResolveAttack = engine.resolveAttack.bind(engine);
      engine.resolveAttack = function resolveAttackWithForcedMovement(
        sequence, round, attacker, target, attack, distance, extra = {},
      ) {
        const event = baseResolveAttack(sequence, round, attacker, target, attack, distance, extra);
        const hasPush = Number(attack?.pushTargetAwayFt || 0) > 0;
        const hasPull = Number(attack?.pullTargetTowardFt || 0) > 0;
        if (!event.hit || (!hasPush && !hasPull)) return event;
        const members = extra.setup ? [...extra.setup.heroes, ...extra.setup.monsters] : [target];
        const actualTarget = members.find((member) => member.combatant_id === event.target_id) || target;
        const before = S().distance(attacker, actualTarget);
        const moved = hasPush
          ? applyAttackPush(attacker, actualTarget, attack, true)
          : applyAttackPull(attacker, actualTarget, attack, true);
        if (moved > 0) {
          const after = S().distance(attacker, actualTarget);
          const verb = hasPush ? "pushed" : "pulled";
          const direction = hasPush ? "straight away" : "straight toward the attacker";
          event.distance_before_ft = before;
          event.distance_after_ft = after;
          event.description += ` ${actualTarget.state.template.name} is ${verb} ${moved} feet ${direction}. Target is ${verb} ${moved} ft. (${before} ft. to ${after} ft.).`;
        }
        return event;
      };
      engine.__forcedMovementHookInstalled = true;
    } catch (error) {
      console.error("Forced movement hook installation failed.", error);
      throw new Error("Forced movement hook installation failed.");
    }
  }

  function resolve(sequence, round, member, target, attack, distance, setup, turnKey, options = {}) {
    const event = A().resolveAttack(sequence++, round, member, target, attack, distance, {
      advantage: options.advantage || 0,
      featureId: options.featureId || null,
      setup,
      allowReckless: options.allowReckless !== false,
      turnKey,
    });
    const events = [event];
    if (member.state.turn_terminated) return { events, sequence };
    const cleave = W().resolveCleave(sequence, round, member, event, attack, setup, turnKey);
    events.push(...cleave.events); sequence = cleave.sequence;
    if (member.state.template.kind !== "character" || !attack.light || member.state.turn_terminated) return { events, sequence };
    const extra = L().resolve(sequence, round, member, setup, attack, turnKey);
    events.push(...extra.events);
    return { events, sequence: extra.sequence };
  }

  installForcedMovementHook();
  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { applyAttackPush, applyAttackPull, resolve };
})();