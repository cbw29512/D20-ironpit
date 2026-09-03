(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const SM = () => window.IRON_PIT_BROWSER_SPELL_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES;
  const SAP = () => window.IRON_PIT_BROWSER_SAP || { consume: () => 0, disadvantage: () => 0 };
  const HI = () => window.IRON_PIT_BROWSER_HEROIC_INSPIRATION || { rerollFailedAttack: (_state, roll) => ({ roll, used: false }) };

  function slotResource(caster, spell, turnKey) {
    if (spell.level === 0 || !C().slotSpellAvailable(caster.state, turnKey)) return null;
    const id = `spell-slot-${spell.level}`;
    return (caster.state.resources?.[id] || 0) > 0 ? id : null;
  }

  function resolve(sequence, round, caster, target, spell, setup, turnKey) {
    if (spell.actionCost === "reaction" || !E().available(caster.state, spell.actionCost)) throw new Error(`${spell.name} cannot be cast in this action window.`);
    if (target.side === caster.side || target.state.is_dead || !target.state.is_alive) throw new Error(`${spell.name} requires a living enemy target.`);
    const distance = S().distance(caster, target);
    if (distance > spell.range) throw new Error(`${spell.name} target is out of range.`);
    const resourceId = slotResource(caster, spell, turnKey);
    if (spell.level > 0 && !resourceId) throw new Error(`No level ${spell.level} spell slot remains for ${spell.name}.`);
    const conditions = A().conditionSources(caster.state, target.state, distance, target.combatant_id);
    const advantage = conditions.advantage + M().nextAttackAgainstAdvantage(caster.state, target.combatant_id);
    const closeThreat = (spell.attackKind || "ranged") === "ranged" && A().rangedCloseThreat(caster, target, distance, setup);
    const mode = R().modeFromSources(advantage, conditions.disadvantage + SAP().disadvantage(caster.state) + (closeThreat ? 1 : 0));
    const targetAc = M().effectiveArmorClass(target.state);
    const heroic = HI().rerollFailedAttack(caster.state, R().d20(spell.attackBonus, mode), targetAc);
    const attackRoll = M().applyD20Bonus(caster.state, "attack-roll-bonus-die", heroic.roll);
    M().consumeNextAttackAgainstAdvantage(caster.state, target.combatant_id);
    SAP().consume(caster.state); M().consumeAttacksAgainstAdvantage(target.state);
    if (resourceId) { C().markSlotSpellCast(caster.state, turnKey); caster.state.resources[resourceId] -= 1; }
    E().spend(caster.state, spell.actionCost);
    const natural = attackRoll.selected_roll;
    const hit = natural !== 1 && (natural === 20 || attackRoll.total >= targetAc);
    const critical = Boolean(hit && (natural === 20 || (Q().autoCritical(target.state) && distance <= 5)));
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [];
    if (hit) {
      const count = spell.damageDiceCount * (critical ? 2 : 1), rolls = window.IRON_PIT_DICE.rollMany(count, spell.damageDiceSize);
      const raw = rolls.reduce((sum, value) => sum + value, 0) + (spell.damageBonus || 0);
      const applied = spell.damageType ? A().adjustedDamage(target.state, raw, spell.damageType) : 0;
      damageRoll = { notation: `${count}d${spell.damageDiceSize}+${spell.damageBonus || 0}`, rolls, modifier: spell.damageBonus || 0, total: applied };
      if (spell.damageType) damageComponents = [{ source: spell.name, notation: damageRoll.notation, rolls: [...rolls], modifier: spell.damageBonus || 0,
        damage_type: spell.damageType, total: raw, applied_total: applied }];
      const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
      A().applyDamage(target.state, applied, critical, spell.damageType && applied > 0 ? [spell.damageType] : [], states);
      if (target.state.is_alive && !target.state.is_dead) (spell.onHitModifierEffects || []).forEach((effect, index) => {
        M().add(target.state, SM().build(caster.combatant_id, target.combatant_id, spell, effect, index, round));
      });
    }
    const outcome = critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS";
    let description = `${caster.state.template.name}: ${outcome} with ${spell.name}.`;
    if (heroic.used) description += " Heroic Inspiration rerolls one d20.";
    return {
      sequence, round_number: round, event_type: "attack", actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, attack_name: spell.name, target_ac: targetAc,
      attack_roll: attackRoll, damage_roll: damageRoll, damage_components: damageComponents, applied_condition_ids: [], hit, critical,
      hp_before: hpBefore, hp_after: target.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, weapon_id: null, projectile: null, feature_id: spell.id,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      resource_remaining: resourceId ? caster.state.resources[resourceId] : null, animation: spell.animation || "spell-attack",
      description,
    };
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK = { resolve };
})();
