(() => {
  "use strict";

  const RESOURCE_ID = "legendary-actions";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

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

  function saveAction(option) {
    const raw = option.save_action || option.saveAction;
    if (!raw) return null;
    const rider = raw.failedSaveTimedEffect || raw.failed_save_timed_effect;
    return {
      ...raw,
      saveAbility: raw.saveAbility || raw.save_ability,
      range: raw.range ?? raw.range_ft ?? 0,
      damageDiceCount: raw.damageDiceCount ?? raw.damage_dice_count ?? 0,
      damageDiceSize: raw.damageDiceSize ?? raw.damage_dice_size ?? 6,
      damageBonus: raw.damageBonus ?? raw.damage_bonus ?? 0,
      damageType: raw.damageType || raw.damage_type,
      successDamage: raw.successDamage || raw.success_damage || "none",
      failedSaveTimedEffect: rider && {
        effectId: rider.effectId || rider.effect_id,
        durationRounds: rider.durationRounds ?? rider.duration_rounds ?? null,
        expiryTiming: rider.expiryTiming || rider.expiry_timing || "target_turn_end",
      },
      failedSavePushFt: raw.failedSavePushFt ?? raw.failed_save_push_ft ?? 0,
    };
  }

  function saveDamage(action, targetCount) {
    const average = (action.damageDiceCount || 0) * Math.floor(((action.damageDiceSize || 0) + 1) / 2)
      + (action.damageBonus || 0);
    return average * targetCount;
  }

  function savePlacement(actor, setup, action) {
    const area = action.area;
    if (!area) return null;
    if (T()?.legalPlacements) {
      const placements = T().legalPlacements(actor, setup, area, action.range, false);
      return placements[0] || null;
    }
    const radius = area.radius_ft || area.radiusFt || action.range || 0;
    const ids = opponents(actor, setup)
      .filter((target) => S().distance(actor, target) <= radius)
      .map((target) => target.combatant_id);
    return ids.length ? { targetIds: ids, target_ids: ids } : null;
  }

  function choose(actor, setup) {
    if (Q().incapacitated(actor.state) || actor.state.is_dead || actor.state.current_hp <= 0) return null;
    const remaining = actor.state.resources?.[RESOURCE_ID] || 0;
    let best = null;
    let bestDamage = -1;
    for (const option of actor.state.template.legendary_actions || []) {
      const cost = option.cost || 1;
      if (remaining < cost) continue;
      if (option.kind === "attack") {
        const attack = attacks(actor).find((item) => item.id === option.attack_id);
        if (!attack) throw new Error(`${actor.state.template.name} legendary action ${option.id} references missing attack ${option.attack_id}.`);
        for (const target of opponents(actor, setup)) {
          if (S().distance(actor, target) > reachFt(attack)) continue;
          const damage = attackDamage(attack);
          if (damage > bestDamage) {
            best = { kind: "attack", option, target, attack };
            bestDamage = damage;
          }
        }
        continue;
      }
      if (option.kind !== "save") continue;
      const action = saveAction(option);
      if (!action) throw new Error(`${actor.state.template.name} legendary action ${option.id} is missing a save action.`);
      const placement = savePlacement(actor, setup, action);
      const ids = placement?.targetIds || placement?.target_ids || [];
      if (!ids.length) continue;
      const damage = saveDamage(action, ids.length);
      if (damage > bestDamage) {
        best = { kind: "save", option, action, placement, targetIds: ids };
        bestDamage = damage;
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
        if (choice.kind === "attack") {
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
          continue;
        }
        const prefix = `${actor.state.template.name} uses Legendary Action: ${choice.option.name}.`;
        const shared = choice.action.damageDiceCount
          ? window.IRON_PIT_DICE.rollMany(choice.action.damageDiceCount, choice.action.damageDiceSize)
          : null;
        for (const id of choice.targetIds) {
          const target = [...(setup.heroes || []), ...(setup.monsters || [])]
            .find((item) => item.combatant_id === id);
          if (!target) throw new Error(`Unknown legendary save target ${id}.`);
          const event = V().resolveAction(sequence, round, actor, target, choice.action, 0, {
            spendAction: false, checkResource: false, spendResource: false,
            sharedDamageRolls: shared, setup,
          });
          events.push({
            ...event,
            feature_id: choice.option.id,
            description: `${prefix} ${event.description || ""}`.trim(),
          });
          sequence += 1;
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Legendary actions after turn failed.", { combatant: justActed?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS = { choose, resolveAfterTurn };
})();
