(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function resolve(sequence, round, caster, target, setup, choice, turnKey) {
    const action = choice.action;
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.name} cannot be cast in this action window.`);
    if (target.side === caster.side || target.state.is_dead || !target.state.is_alive) throw new Error(`${action.name} requires a living enemy target.`);
    if (S().distance(caster, target) > action.range) throw new Error(`${action.name} target is out of range.`);
    if (!C().slotSpellAvailable(caster.state, turnKey)) throw new Error("A spell slot was already expended this turn.");
    const resourceId = `spell-slot-${choice.slotLevel}`;
    if (!(caster.state.resources?.[resourceId] > 0)) throw new Error(`No level ${choice.slotLevel} spell slot remains for ${action.name}.`);

    const components = [], allRolls = [];
    let total = 0;
    for (let index = 0; index < choice.projectileCount; index += 1) {
      const rolls = choice.damageMaximizer
        ? C().maximizedRolls(action.damageDiceCount || 1, action.damageDiceSize || 4)
        : window.IRON_PIT_DICE.rollMany(action.damageDiceCount || 1, action.damageDiceSize || 4);
      const raw = rolls.reduce((sum, value) => sum + value, 0) + (action.damageBonus || 0);
      const applied = A().adjustedDamage(target.state, raw, action.damageType);
      allRolls.push(...rolls);
      total += applied;
      components.push({
        source: `${action.name} projectile ${index + 1}`,
        notation: `${action.damageDiceCount || 1}d${action.damageDiceSize || 4}+${action.damageBonus || 0}`,
        rolls, modifier: action.damageBonus || 0, damage_type: action.damageType,
        total: raw, applied_total: applied,
      });
    }

    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
    A().applyDamage(target.state, total, false, total > 0 ? [action.damageType] : [], states, setup, components);
    C().markSlotSpellCast(caster.state, turnKey);
    caster.state.resources[resourceId] -= 1;
    E().spend(caster.state, action.actionCost);

    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      feature_id: action.id,
      damage_roll: {
        notation: `${choice.projectileCount}x(${action.damageDiceCount || 1}d${action.damageDiceSize || 4}+${action.damageBonus || 0})`,
        rolls: allRolls, modifier: choice.projectileCount * (action.damageBonus || 0), total,
      },
      damage_components: components,
      hp_before: hpBefore, hp_after: target.state.current_hp,
      temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      resource_remaining: caster.state.resources[resourceId],
      animation: action.animation || "spell-projectile",
      description: `${caster.state.template.name} casts ${action.name}: ${choice.projectileCount} projectiles automatically strike ${target.state.template.name}.`,
    };
  }

  window.IRON_PIT_BROWSER_AUTO_HIT_SPELL = { resolve };
})();
