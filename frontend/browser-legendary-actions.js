(() => {
  "use strict";

  const RESOURCE_ID = "legendary-actions";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function attacks(member) {
    return member.state.template.attacks || [
      member.state.template.weapon_attack,
      ...(member.state.template.alternate_weapon_attacks || []),
    ].filter(Boolean);
  }

  function attackDamage(attack) {
    if (Number.isInteger(attack.fixedDamage) || Number.isInteger(attack.fixed_damage)) {
      return (attack.fixedDamage ?? attack.fixed_damage) + (attack.damageBonus || attack.damage_bonus || 0);
    }
    const count = attack.diceCount || attack.weapon?.dice_count || 0;
    const size = attack.diceSize || attack.weapon?.dice_size || 0;
    const bonus = attack.damageBonus || attack.damage_bonus || 0;
    return count * Math.floor((size + 1) / 2) + bonus;
  }

  function reachFt(attack) {
    return attack.reach || attack.weapon?.reach_ft || 5;
  }

  function opponents(member, setup) {
    const side = member.side === "heroes" ? setup.monsters : setup.heroes;
    return (side || []).filter((item) => item.state.is_alive && !item.state.is_dead && item.state.current_hp > 0);
  }

  function choose(actor, setup) {
    if (Q().incapacitated(actor.state) || actor.state.is_dead || actor.state.current_hp <= 0) return null;
    const remaining = actor.state.resources?.[RESOURCE_ID] || 0;
    let best = null;
    let bestDamage = -1;
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "attack" || remaining < (option.cost || 1)) continue;
      const attack = attacks(actor).find((item) => item.id === option.attack_id);
      if (!attack) throw new Error(`${actor.state.template.name} legendary action ${option.id} references missing attack ${option.attack_id}.`);
      for (const target of opponents(actor, setup)) {
        if (S().distance(actor, target) > reachFt(attack)) continue;
        const damage = attackDamage(attack);
        if (damage > bestDamage) {
          best = { option, target, attack };
          bestDamage = damage;
        }
      }
    }
    return best;
  }

  function resolveAfterTurn(sequence, round, justActed, setup) {
    try {
      const events = [];
      const others = [...(setup.heroes || []), ...(setup.monsters || [])]
        .filter((item) => item.combatant_id !== justActed.combatant_id);
      for (const actor of others) {
        const choice = choose(actor, setup);
        if (!choice) continue;
        const cost = choice.option.cost || 1;
        actor.state.resources[RESOURCE_ID] = (actor.state.resources[RESOURCE_ID] || 0) - cost;
        const event = A().resolveAttack(
          sequence, round, actor, choice.target, choice.attack,
          S().distance(actor, choice.target),
          { spendAction: false, setup, featureId: choice.option.id },
        );
        events.push({
          ...event,
          description: `${actor.state.template.name} uses Legendary Action: ${choice.option.name}. ${event.description || ""}`.trim(),
        });
        sequence += 1;
      }
      return { events, sequence };
    } catch (error) {
      console.error("Legendary actions after turn failed.", { combatant: justActed?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS = { choose, resolveAfterTurn };
})();
