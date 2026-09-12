(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const P = () => window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL_POLICY;

  function resolve(sequence, round, caster, target, action, setup, turnKey) {
    if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) throw new Error(`${action.name} cannot be cast in this action window.`);
    if (target.side === caster.side || target.state.is_dead || !target.state.is_alive) throw new Error(`${action.name} requires a living enemy target.`);
    if (S().distance(caster, target) > action.range) throw new Error(`${action.name} target is out of range.`);
    const slot = P().slots(caster.state, action.level, turnKey)[0];
    if (!slot) throw new Error(`No legal spell slot remains for ${action.name}.`);
    const [slotLevel, resourceId] = slot;
    const projectileCount = P().projectileCount(action, slotLevel);
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    const components = [], allRolls = [];
    let appliedTotal = 0;
    for (let i = 0; i < projectileCount; i += 1) {
      const rolls = window.IRON_PIT_DICE.rollMany(action.damageDiceCountPerProjectile || 1, action.damageDiceSize);
      allRolls.push(...rolls);
      const raw = rolls.reduce((sum, value) => sum + value, 0) + (action.damageBonusPerProjectile || 0);
      const applied = A().adjustedDamage(target.state, raw, action.damageType);
      appliedTotal += applied;
      components.push({ source: `${action.name} projectile ${i + 1}`, notation: `${action.damageDiceCountPerProjectile || 1}d${action.damageDiceSize}+${action.damageBonusPerProjectile || 0}`, rolls: [...rolls], modifier: action.damageBonusPerProjectile || 0, damage_type: action.damageType, total: raw, applied_total: applied });
    }
    const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
    A().applyDamage(target.state, appliedTotal, false, appliedTotal > 0 ? [action.damageType] : [], states);
    C().markSlotSpellCast(caster.state, turnKey); caster.state.resources[resourceId] -= 1;
    E().spend(caster.state, action.actionCost);
    const damageRoll = { notation: components.map((item) => item.notation).join(" + "), rolls: allRolls, modifier: projectileCount * (action.damageBonusPerProjectile || 0), total: appliedTotal };
    return {
      sequence, round_number: round, event_type: "feature", actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, attack_name: action.name,
      damage_roll: damageRoll, damage_components: components, applied_condition_ids: [],
      hp_before: hpBefore, hp_after: target.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, feature_id: action.id,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      resource_remaining: caster.state.resources[resourceId], animation: action.animation || "automatic-damage-spell",
      description: `${caster.state.template.name} casts ${action.name} at slot level ${slotLevel}; ${projectileCount} projectiles automatically hit ${target.state.template.name}.`,
    };
  }

  window.IRON_PIT_BROWSER_AUTOMATIC_DAMAGE_SPELL = { resolve };
})();
