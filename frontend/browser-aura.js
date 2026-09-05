(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };
  const targets = (member, setup, aura) => [...setup.heroes, ...setup.monsters].filter((target) =>
    target.combatant_id !== member.combatant_id && !target.state.is_dead &&
    (aura.targetMode === "all_others" || target.side !== member.side) && S().distance(member, target) <= aura.radius);
  function rollAdvantageSources(member, setup, kind) {
    if (!member || !setup) return 0;
    const sources = member.side === "heroes" ? setup.heroes : setup.monsters;
    return sources.filter((source) => {
      const aura = source.state?.template?.rollAdvantageAura;
      if (!aura || source.state.is_dead || !source.state.is_alive || source.state.current_hp <= 0) return false;
      if (aura.disabledWhileIncapacitated && Q().incapacitated(source.state)) return false;
      if (kind === "attack_roll" && !aura.grantsAttackRollAdvantage) return false;
      if (kind === "saving_throw" && !aura.grantsSavingThrowAdvantage) return false;
      return S().distance(source, member) <= aura.radius;
    }).length;
  }

  function resolve(sequence, round, member, setup) {
    const aura = member.state.template.endTurnDamageAura;
    if (!aura || member.state.is_dead || (aura.disabledWhileIncapacitated && Q().incapacitated(member.state))) return { events: [], sequence };
    const selected = targets(member, setup, aura); if (!selected.length) return { events: [], sequence };
    const rolls = Array.from({ length: aura.diceCount }, () => window.IRON_PIT_DICE.roll(aura.diceSize));
    const raw = rolls.reduce((sum, value) => sum + value, aura.damageBonus || 0);
    const notation = `${aura.diceCount}d${aura.diceSize}${aura.damageBonus ? (aura.damageBonus > 0 ? `+${aura.damageBonus}` : aura.damageBonus) : ""}`;
    const affected = [...setup.heroes, ...setup.monsters].map((item) => item.state), events = [];
    for (const target of selected) {
      const hp = target.state.current_hp, temp = target.state.temporary_hp, ds = target.state.death_save_successes, df = target.state.death_save_failures;
      const applied = A().adjustedDamage(target.state, raw, aura.damageType);
      A().applyDamage(target.state, applied, false, applied ? [aura.damageType] : [], affected, rollAdvantageSources(target, setup, "saving_throw"));
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name, damage_roll: { notation, rolls, modifier: aura.damageBonus || 0, selected_roll: null, mode: "normal", total: applied },
        damage_components: [{ source: aura.name, notation, rolls, modifier: aura.damageBonus || 0, damage_type: aura.damageType, total: raw, applied_total: applied }],
        hp_before: hp, hp_after: target.state.current_hp, temporary_hp_before: temp, temporary_hp_after: target.state.temporary_hp,
        death_save_successes_before: ds, death_save_failures_before: df, death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: "end-turn-damage-aura", animation: "fire",
        description: `${member.state.template.name}'s ${aura.name} deals ${applied} ${aura.damageType} damage to ${target.state.template.name}.` });
    }
    return { events, sequence };
  }
  window.IRON_PIT_BROWSER_AURA = { resolve, rollAdvantageSources };
})();
