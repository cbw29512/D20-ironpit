(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const members = (setup) => setup ? [...setup.heroes, ...setup.monsters] : [];
  function actualTarget(target, event, setup) {
    if (event.target_id === target.combatant_id) return target;
    return members(setup).find((member) => member.combatant_id === event.target_id) || target;
  }
  function apply(source, target, effect, event, setup) {
    if (!effect || event.hit !== true) return 0;
    if (effect.maxTargetSize && !S().sizeAtMost(target, effect.maxTargetSize)) return 0;
    const before = Math.abs(target.position_ft - source.position_ft);
    let moved = effect.distance, proposed;
    if (effect.direction === "pull") {
      moved = Math.min(effect.distance, before); if (!moved) return 0;
      target.position_ft += (target.position_ft > source.position_ft ? -1 : 1) * moved;
    } else {
      const direction = target.position_ft >= source.position_ft ? 1 : -1;
      proposed = target.position_ft + direction * moved;
      if (proposed < 0 && setup) { const shift = -proposed; for (const member of members(setup)) member.position_ft += shift; proposed = 0; }
      else if (proposed < 0) proposed = source.position_ft + before + moved;
      target.position_ft = proposed;
    }
    event.distance_before_ft = before; event.distance_after_ft = Math.abs(target.position_ft - source.position_ft); event.movement_ft = moved;
    event.description += ` ${target.state.template.name} is ${effect.direction === "push" ? "pushed" : "pulled"} ${moved} feet.`;
    return moved;
  }
  const base = window.IRON_PIT_BROWSER_ATTACK?.resolveAttack;
  if (!base) throw new Error("Browser attack runtime must load before forced movement.");
  function resolveAttack(sequence, round, attacker, target, attack, distance, extra = {}) {
    const event = base(sequence, round, attacker, target, attack, distance, extra);
    const resolved = actualTarget(target, event, extra.setup); apply(attacker, resolved, attack.forcedMovement, event, extra.setup); return event;
  }
  window.IRON_PIT_BROWSER_ATTACK = { ...window.IRON_PIT_BROWSER_ATTACK, resolveAttack };
  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { apply };
})();
