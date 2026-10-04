(() => {
  "use strict";

  const RESOURCE_ID = "legendary-actions";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;

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
    return count * Math.floor((size + 1) / 2) + (attack.damageBonus || attack.damage_bonus || 0);
  }

  function reachFt(attack) {
    return attack.reach || attack.weapon?.reach_ft || 5;
  }

  function living(side) {
    return (side || []).filter((item) => item.state.is_alive && !item.state.is_dead && item.state.current_hp > 0);
  }

  function opponents(member, setup) {
    return living(member.side === "heroes" ? setup.monsters : setup.heroes);
  }

  function allies(member, setup) {
    return living(member.side === "heroes" ? setup.heroes : setup.monsters);
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
        escapeCheckAbility: rider.escapeCheckAbility || rider.escape_check_ability || null,
        escapeCheckDc: rider.escapeCheckDc ?? rider.escape_check_dc ?? null,
      },
      failedSavePushFt: raw.failedSavePushFt ?? raw.failed_save_push_ft ?? 0,
    };
  }

  function saveDamage(action, targetCount) {
    return ((action.damageDiceCount || 0) * Math.floor(((action.damageDiceSize || 0) + 1) / 2)
      + (action.damageBonus || 0)) * targetCount;
  }

  function savePlacement(actor, setup, action) {
    const area = action.area;
    if (!area) return null;
    if (T()?.legalPlacements) return T().legalPlacements(actor, setup, area, action.range, false)[0] || null;
    const radius = area.radius_ft || area.radiusFt || action.range || 0;
    const ids = opponents(actor, setup).filter((target) => S().distance(actor, target) <= radius)
      .map((target) => target.combatant_id);
    return ids.length ? { targetIds: ids, target_ids: ids } : null;
  }

  function remainingUses(actor) {
    return actor.state.resources?.[RESOURCE_ID] || 0;
  }

  function chooseAttack(actor, setup) {
    let best = null, bestDamage = -1;
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "attack" || remainingUses(actor) < (option.cost || 1)) continue;
      const attack = attacks(actor).find((item) => item.id === option.attack_id);
      if (!attack) throw new Error(`${actor.state.template.name} legendary action ${option.id} references missing attack ${option.attack_id}.`);
      for (const target of opponents(actor, setup)) {
        if (S().distance(actor, target) > reachFt(attack)) continue;
        const damage = attackDamage(attack);
        if (damage > bestDamage) { best = { kind: "attack", option, target, attack }; bestDamage = damage; }
      }
    }
    return { choice: best, damage: bestDamage };
  }

  function chooseSave(actor, setup) {
    let best = null, bestDamage = -1;
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "save" || remainingUses(actor) < (option.cost || 1)) continue;
      const action = saveAction(option);
      if (!action) throw new Error(`${actor.state.template.name} legendary action ${option.id} is missing a save action.`);
      const placement = savePlacement(actor, setup, action);
      const ids = placement?.targetIds || placement?.target_ids || [];
      if (!ids.length) continue;
      const damage = saveDamage(action, ids.length);
      if (damage > bestDamage) { best = { kind: "save", option, action, placement, targetIds: ids }; bestDamage = damage; }
    }
    return { choice: best, damage: bestDamage };
  }

  function chooseAcBuff(actor, setup) {
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "ac_buff" || remainingUses(actor) < (option.cost || 1)) continue;
      const spec = option.ac_buff || option.acBuff;
      if (!spec) throw new Error(`${actor.state.template.name} legendary action ${option.id} is missing ac_buff.`);
      const legal = allies(actor, setup).filter((item) => S().distance(actor, item) <= (spec.range_ft ?? spec.rangeFt ?? 60));
      if (!legal.length) continue;
      return { kind: "ac_buff", option, target: legal.find((item) => item.combatant_id === actor.combatant_id) || legal[0], spec };
    }
    return null;
  }

  function chooseHeal(actor) {
    if (actor.state.current_hp >= (actor.state.template.max_hp || actor.state.current_hp)) return null;
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "heal" || remainingUses(actor) < (option.cost || 1)) continue;
      if (!option.heal) throw new Error(`${actor.state.template.name} legendary action ${option.id} is missing heal.`);
      return { kind: "heal", option, spec: option.heal };
    }
    return null;
  }

  function chooseCheck(actor) {
    for (const option of actor.state.template.legendary_actions || []) {
      if (option.kind !== "check" || remainingUses(actor) < (option.cost || 1)) continue;
      const ability = option.check_ability || option.checkAbility;
      if (!ability) throw new Error(`${actor.state.template.name} legendary action ${option.id} is missing check_ability.`);
      return { kind: "check", option, ability };
    }
    return null;
  }

  function choose(actor, setup) {
    if (Q().incapacitated(actor.state) || actor.state.is_dead || actor.state.current_hp <= 0) return null;
    const attack = chooseAttack(actor, setup);
    const save = chooseSave(actor, setup);
    if (save.damage > attack.damage) return save.choice;
    if (attack.choice) return attack.choice;
    return chooseAcBuff(actor, setup) || chooseHeal(actor) || chooseCheck(actor);
  }

  window.IRON_PIT_BROWSER_LEGENDARY_ACTION_CHOICE = { choose };
})();
