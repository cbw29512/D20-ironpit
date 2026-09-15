(() => {
  "use strict";
  const D = () => window.IRON_PIT_DICE;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const members = (setup) => [...setup.heroes, ...setup.monsters];

  function adjusted(state, amount, type) {
    if (state.template.damage_immunities?.includes(type)) return 0;
    let result = amount;
    if (state.template.damage_resistances?.includes(type) || state.temporary_damage_resistances?.includes(type)) result = Math.floor(result / 2);
    if (state.template.damage_vulnerabilities?.includes(type)) result *= 2;
    return result;
  }

  function resolve(sequence, round, source, target, setup, spec) {
    const rolls = Array.from({ length: spec.diceCount }, () => D().roll(spec.diceSize));
    const raw = rolls.reduce((sum, value) => sum + value, 0) + (spec.damageBonus || 0);
    const total = adjusted(target.state, raw, spec.damageType), hpBefore = target.state.current_hp;
    Z().applyDamage(target.state, total, false, total > 0 ? [spec.damageType] : [], members(setup).map((member) => member.state));
    const notation = `${spec.diceCount}d${spec.diceSize}${spec.damageBonus ? `${spec.damageBonus > 0 ? "+" : ""}${spec.damageBonus}` : ""}`;
    const component = { source: spec.featureName, notation, rolls, modifier: spec.damageBonus || 0,
      damage_type: spec.damageType, total: raw, applied_total: total };
    return { sequence, round_number: round, event_type: "feature", actor_id: source.combatant_id,
      actor_name: source.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
      feature_id: spec.featureId, damage_roll: { notation, rolls, modifier: spec.damageBonus || 0, total },
      damage_components: [component], hp_before: hpBefore, hp_after: target.state.current_hp,
      animation: spec.animation || "ongoing-damage",
      description: `${source.state.template.name}'s ${spec.featureName} deals ${total} ${spec.damageType} damage to ${target.state.template.name}.` };
  }

  window.IRON_PIT_BROWSER_ONGOING_DAMAGE = { adjusted, resolve };
})();
