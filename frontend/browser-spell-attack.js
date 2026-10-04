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
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const HI = () => window.IRON_PIT_BROWSER_HEROIC_INSPIRATION || { rerollFailedAttack: (_state, roll) => ({ roll, used: false }) };
  const CE = () => window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS;

  function spendRangeModifier(state, option) {
    if (!option) return null;
    const cost = option.resourceCost || 1;
    const current = state.resources?.[option.resourceId] || 0;
    if (current < cost) throw new Error(`Insufficient ${option.resourceId} for ${option.name}.`);
    state.resources[option.resourceId] = current - cost;
    return state.resources[option.resourceId];
  }

  function slotResource(caster, spell, turnKey, castSlotLevel = null) {
    if (spell.level === 0 || !C().slotSpellAvailable(caster.state, turnKey)) return null;
    const level = castSlotLevel ?? spell.level;
    if (!Number.isInteger(level) || level < spell.level || level > 9) {
      throw new Error(`Illegal slot level ${level} for ${spell.name}.`);
    }
    const id = `spell-slot-${level}`;
    return (caster.state.resources?.[id] || 0) > 0 ? id : null;
  }

  function resolve(sequence, round, caster, target, spell, setup, turnKey, options = {}) {
    const spendCastCosts = options.spendCastCosts !== false;
    if (spell.actionCost === "reaction" || (spendCastCosts && !E().available(caster.state, spell.actionCost))) throw new Error(`${spell.name} cannot be cast in this action window.`);
    if (target.side === caster.side || target.state.is_dead || !target.state.is_alive) throw new Error(`${spell.name} requires a living enemy target.`);
    const distance = options.distanceOverrideFt ?? S().distance(caster, target);
    const rangeModifier = options.rangeModifier || null;
    const allowedRange = spell.range * (rangeModifier?.rangeMultiplier || 1);
    if (distance > allowedRange) throw new Error(`${spell.name} target is out of range.`);
    const castSlotLevel = options.castSlotLevel ?? null;
    const resourceId = spendCastCosts ? slotResource(caster, spell, turnKey, castSlotLevel) : null;
    if (spendCastCosts && spell.level > 0 && !resourceId) {
      throw new Error(`No level ${castSlotLevel ?? spell.level} spell slot remains for ${spell.name}.`);
    }
    const ward = window.IRON_PIT_BROWSER_TARGETING_WARDS?.check(caster, target) || null;
    if (ward && !ward.succeeded) {
      if (resourceId) { C().markSlotSpellCast(caster.state, turnKey); caster.state.resources[resourceId] -= 1; }
      if (spendCastCosts) E().spend(caster.state, spell.actionCost);
      const rangeRemaining = spendCastCosts ? spendRangeModifier(caster.state, rangeModifier) : null;
      if (spendCastCosts) CE()?.applyTimedResistance(caster, spell, round);
      const event = window.IRON_PIT_BROWSER_TARGETING_WARDS.blocked(sequence, round, caster, target, spell.name, ward);
      event.resource_remaining = resourceId ? caster.state.resources[resourceId] : rangeRemaining;
      if (rangeModifier) event.description += ` ${caster.state.template.name} uses ${rangeModifier.name}.`;
      return event;
    }
    const conditions = A().conditionSources(caster.state, target.state, distance, target.combatant_id);
    const armorAdvantage = spell.advantageIfTargetWearingMetalArmor && target.state.template.wearing_metal_armor ? 1 : 0;
    const buffAdvantage = window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS?.spellAttackAdvantage?.(caster.state) ? 1 : 0;
    const advantage = conditions.advantage + armorAdvantage + buffAdvantage + M().nextAttackAgainstAdvantage(caster.state, target.combatant_id);
    const closeThreat = (spell.attackKind || "ranged") === "ranged" && A().rangedCloseThreat(caster, target, distance, setup);
    const mode = R().modeFromSources(
      advantage,
      conditions.disadvantage + SAP().disadvantage(caster.state)
        + (T()?.nextAttackDisadvantage(caster.state) || 0) + (closeThreat ? 1 : 0),
    );
    const targetAc = M().effectiveArmorClass(target.state);
    const heroic = HI().rerollFailedAttack(caster.state, R().d20(spell.attackBonus, mode), targetAc);
    let attackRoll = M().applyD20Bonus(caster.state, "attack-roll-bonus-die", heroic.roll); const rollPenalty = window.IRON_PIT_BROWSER_REACTION_ROLL_PENALTIES?.applyIfUseful(caster, setup, "attack", attackRoll, targetAc); if (rollPenalty) attackRoll = rollPenalty.roll;
    M().consumeNextAttackAgainstAdvantage(caster.state, target.combatant_id);
    T()?.consumeNextAttackDisadvantage(caster.state);
    SAP().consume(caster.state); M().consumeAttacksAgainstAdvantage(target.state);
    if (resourceId) { C().markSlotSpellCast(caster.state, turnKey); caster.state.resources[resourceId] -= 1; }
    if (spendCastCosts) E().spend(caster.state, spell.actionCost);
    const rangeRemaining = spendCastCosts ? spendRangeModifier(caster.state, rangeModifier) : null;
    if (spendCastCosts) CE()?.applyTimedResistance(caster, spell, round);
    const natural = attackRoll.selected_roll;
    const hit = natural !== 1 && (natural === 20 || attackRoll.total >= targetAc);
    const critical = Boolean(hit && (natural === 20 || (Q().autoCritical(target.state) && distance <= 5)));
    const hpBefore = target.state.current_hp, temporaryHpBefore = target.state.temporary_hp;
    const deathSuccessBefore = target.state.death_save_successes, deathFailureBefore = target.state.death_save_failures;
    const concentrationBefore = target.state.concentration?.effect_id || null;
    let damageRoll = null, damageComponents = [], appliedConditions = [];
    const missHalf = !hit && spell.missDamage === "half";
    if (hit || missHalf) {
      const count = spell.damageDiceCount * (critical ? 2 : 1);
      const rolls = window.IRON_PIT_DICE.rollMany(count, spell.damageDiceSize);
      const raw = rolls.reduce((sum, value) => sum + value, 0) + (spell.damageBonus || 0);
      const rolledComponents = spell.damageType ? [{
        source: spell.name,
        notation: `${count}d${spell.damageDiceSize}+${spell.damageBonus || 0}`,
        rolls: [...rolls],
        modifier: spell.damageBonus || 0,
        damage_type: spell.damageType,
        total: missHalf ? Math.floor(raw / 2) : raw,
      }] : [];
      for (const modifier of (hit ? M().bonusDamage(caster.state, target.combatant_id) : [])) {
        const riderCount = modifier.dice_count * (critical ? 2 : 1);
        const riderRolls = window.IRON_PIT_DICE.rollMany(riderCount, modifier.dice_size);
        rolledComponents.push({
          source: modifier.source_name || modifier.source_effect_id,
          notation: `${riderCount}d${modifier.dice_size}+0`,
          rolls: riderRolls,
          modifier: 0,
          damage_type: modifier.damage_type,
          total: riderRolls.reduce((sum, value) => sum + value, 0),
        });
      }
      damageComponents = rolledComponents.map((part) => ({
        ...part,
        applied_total: A().adjustedDamage(target.state, part.total, part.damage_type),
      }));
      const applied = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
      damageRoll = damageComponents.length ? {
        notation: damageComponents.map((part) => part.notation).join(" + "),
        rolls: damageComponents.flatMap((part) => part.rolls),
        modifier: damageComponents.reduce((sum, part) => sum + (part.modifier || 0), 0),
        total: applied,
      } : null;
      const states = [...setup.heroes, ...setup.monsters].map((entry) => entry.state);
      const appliedTypes = [...new Set(
        damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type),
      )];
      A().applyDamage(target.state, applied, critical, appliedTypes, states);
      if (hit && target.state.is_alive && !target.state.is_dead) {
        (spell.onHitModifierEffects || []).forEach((effect, index) => {
          M().add(target.state, SM().build(caster.combatant_id, target.combatant_id, spell, effect, index, round));
        });
        (spell.onHitTimedEffects || []).forEach((effect) => {
          const appliedId = T().apply(target.state, effect.effectId, caster.combatant_id, {
            sourceEffectId: spell.id,
            sourceTemplate: caster.state.template,
            sourceIsMagical: Boolean(effect.sourceIsMagical),
            appliedRound: round,
            expiresRound: round + effect.durationRounds,
            expiryTiming: effect.expiryTiming,
            suppressAction: Boolean(effect.suppressAction),
            suppressBonusAction: Boolean(effect.suppressBonusAction),
            suppressReactions: Boolean(effect.suppressReactions),
            suppressMovement: Boolean(effect.suppressMovement),
            nextAttackDisadvantage: Boolean(effect.nextAttackDisadvantage),
            useDefaultPoisonRecovery: false,
          });
          if (appliedId) appliedConditions.push(appliedId);
        });
      }
      if (hit && target.state.is_alive && !target.state.is_dead) {
        window.IRON_PIT_BROWSER_EXILE?.applyOnHit?.({
          sequence, round, member: caster, target, setup, turnKey, attackOutcome: {},
        });
        window.IRON_PIT_BROWSER_MELEE_RETALIATION?.apply(caster, target, {
          melee: (spell.attackKind || "ranged") === "melee", setup,
        });
      }
    }
    const outcome = critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS";
    const survivalLog = window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(target.state) || "";
    let description = `${caster.state.template.name}: ${outcome} with ${spell.name}.`;
    if (rangeModifier) description += ` ${caster.state.template.name} uses ${rangeModifier.name}.`;
    if (heroic.used) description += " Heroic Inspiration rerolls one d20."; if (rollPenalty?.restorationName) description += ` ${rollPenalty.sourceName} uses ${rollPenalty.restorationName}.`; if (rollPenalty) description += ` ${rollPenalty.sourceName} uses ${rollPenalty.actionId} to subtract ${rollPenalty.penaltyTotal} from the attack roll.`;
    const event = {
      sequence, round_number: round, event_type: "attack", actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, attack_name: spell.name, target_ac: targetAc,
      attack_roll: attackRoll, damage_roll: damageRoll, damage_components: damageComponents,
      applied_condition_ids: appliedConditions, hit, critical,
      hp_before: hpBefore, hp_after: target.state.current_hp, temporary_hp_before: temporaryHpBefore, temporary_hp_after: target.state.temporary_hp,
      death_save_successes_before: deathSuccessBefore, death_save_failures_before: deathFailureBefore,
      death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
      is_stable: target.state.is_stable, is_dead: target.state.is_dead, weapon_id: null, projectile: null, feature_id: spell.id,
      concentration_ended_effect_id: concentrationBefore && !target.state.concentration ? concentrationBefore : null,
      resource_remaining: resourceId ? caster.state.resources[resourceId] : rangeRemaining, animation: spell.animation || "spell-attack",
      description: description + survivalLog + (window.IRON_PIT_BROWSER_ZERO_HP_REPLACEMENT?.consumeLog(target.state) || ""),
    };
    if (ward) window.IRON_PIT_BROWSER_TARGETING_WARDS.annotate(event, ward, caster.state.template.name);
    return event;
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK = { resolve };
})();
