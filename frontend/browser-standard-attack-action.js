(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const L = () => window.IRON_PIT_BROWSER_LIGHT_ATTACK;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const W = () => window.IRON_PIT_BROWSER_WEAPON_MASTERY || {
    resolveCleave: (sequence) => ({ events: [], sequence }),
  };

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
      console.error("Forced attack push failed.", error);
      throw new Error("Forced movement resolution failed.");
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
        const members = extra.setup ? [...extra.setup.heroes, ...extra.setup.monsters] : [target];
        const actualTarget = members.find((member) => member.combatant_id === event.target_id) || target;
        const before = S().distance(attacker, actualTarget);
        const moved = applyAttackPush(attacker, actualTarget, attack, event.hit === true);
        if (moved > 0) {
          const after = S().distance(attacker, actualTarget);
          event.distance_before_ft = before;
          event.distance_after_ft = after;
          event.description += ` ${actualTarget.state.template.name} is pushed ${moved} feet straight away. Target is pushed ${moved} ft. away (${before} ft. to ${after} ft.).`;
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
  window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION = { applyAttackPush, resolve };
})();
