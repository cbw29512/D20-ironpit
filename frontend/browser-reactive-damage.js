(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const members = (setup) => setup ? [...setup.heroes, ...setup.monsters] : [];

  function actualTarget(target, setup, targetId) {
    if (!setup || target.combatant_id === targetId) return target;
    return members(setup).find((member) => member.combatant_id === targetId) || target;
  }

  function install() {
    const runtime = A();
    if (!runtime || runtime.reactiveDamageWrapped) return;
    const original = runtime.resolveAttack;
    runtime.resolveAttack = (...args) => {
      const event = original(...args), attacker = args[2], target = args[3], attack = args[4], extra = args[6] || {};
      if (!event.hit || attack.kind !== "melee" || attacker.state.is_dead) return event;
      const defender = actualTarget(target, extra.setup, event.target_id);
      const distance = extra.setup ? S().distance(attacker, defender) : args[5];
      const allRules = [
        ...(defender.state.template.meleeHitReactiveDamage || []),
        ...(defender.state.temporary_melee_hit_reactive_damage || []),
      ];
      const rules = allRules.filter((rule) => distance <= rule.rangeFt);
      if (!rules.length) return event;
      event.actor_hp_before = attacker.state.current_hp; event.reactive_damage_components = [];
      let total = 0, modifier = 0, rolls = [], notation = [];
      for (const rule of rules) {
        const rolled = D().rollMany(rule.diceCount, rule.diceSize);
        const raw = Math.max(0, rolled.reduce((sum, value) => sum + value, 0) + (rule.damageBonus || 0));
        const applied = runtime.adjustedDamage(attacker.state, raw, rule.damageType, true, true);
        if (applied) runtime.applyDamage(attacker.state, applied, false, [rule.damageType], members(extra.setup).map((member) => member.state));
        event.reactive_damage_components.push({ source: rule.id, notation: `${rule.diceCount}d${rule.diceSize}+${rule.damageBonus || 0}`,
          rolls: rolled, modifier: rule.damageBonus || 0, damage_type: rule.damageType, total: raw, applied_total: applied });
        rolls.push(...rolled); modifier += rule.damageBonus || 0; total += applied; notation.push(`${rule.diceCount}d${rule.diceSize}+${rule.damageBonus || 0}`);
      }
      event.actor_hp_after = attacker.state.current_hp;
      event.reactive_damage_roll = { notation: notation.join(" + "), rolls, modifier, total };
      event.description += ` ${defender.state.template.name}'s reactive damage deals ${total} damage to ${attacker.state.template.name}.`;
      return event;
    };
    runtime.reactiveDamageWrapped = true;
  }

  window.IRON_PIT_BROWSER_REACTIVE_DAMAGE = { install };
  install();
})();
