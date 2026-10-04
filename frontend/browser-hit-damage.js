(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const P = () => window.IRON_PIT_BROWSER_PALADIN_2014;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS || { bonusDamage: () => [] };
  const ADR = () => window.IRON_PIT_BROWSER_ATTACK_DAMAGE_REDUCTION;
  const RD = () => window.IRON_PIT_BROWSER_ROGUE_DEFENSES || {
    applyUncannyDodge: (_attacker, _defender, components) => ({ components, used: false }),
    evasionDamage: (_state, _ability, succeeded, successDamage, total) => succeeded && successDamage === "half" ? Math.floor(total / 2) : total,
  };

  function resolveSaveDamage(defender, attack) {
    const effect = attack.onHitSaveDamage;
    if (!effect) return { component: null, saveRoll: null, saveAbility: null, saveDc: null, saveSucceeded: null };
    const save = S().resolveSavingThrow(defender, effect.saveAbility, effect.dc);
    const result = {
      component: null, saveRoll: save.roll, saveAbility: effect.saveAbility,
      saveDc: effect.dc, saveSucceeded: save.succeeded,
    };
    if (save.succeeded && effect.successDamage === "none") return result;
    const rolls = D().rollMany(effect.diceCount, effect.diceSize);
    const raw = rolls.reduce((sum, roll) => sum + roll, 0) + (effect.damageBonus || 0);
    const total = RD().evasionDamage(defender, effect.saveAbility, save.succeeded, effect.successDamage, raw);
    result.component = {
      source: effect.source || attack.name,
      damage_type: effect.damageType,
      notation: `${effect.diceCount}d${effect.diceSize}+${effect.damageBonus || 0}`,
      rolls, modifier: effect.damageBonus || 0, total,
    };
    return result;
  }

  function saveDamageCausedZero(hpBufferBefore, appliedTotal, components, effect, saveComponentPresent) {
    if (!effect?.zeroHpRider || !saveComponentPresent || !components.length) return false;
    const saveApplied = components[components.length - 1].applied_total;
    const nonSaveApplied = appliedTotal - saveApplied;
    return saveApplied > 0 && hpBufferBefore > nonSaveApplied && hpBufferBefore <= appliedTotal;
  }

  function applyZeroHpSaveDamageRider(defender, effect, turnKey) {
    const rider = effect.zeroHpRider;
    if (!rider) return;
    const separator = turnKey.indexOf(":");
    if (separator < 1 || separator === turnKey.length - 1) {
      throw new Error("Zero-HP save-damage riders require a round:source turn key.");
    }
    const roundNumber = Number.parseInt(turnKey.slice(0, separator), 10);
    const sourceId = turnKey.slice(separator + 1);
    if (!Number.isInteger(roundNumber)) throw new Error("Zero-HP save-damage rider round must be an integer.");
    if (!Z()?.stabilizeAtZero) throw new Error("Browser zero-HP stabilization runtime is not loaded.");
    if (!T()?.apply) throw new Error("Browser timed-condition runtime is not loaded.");
    Z().stabilizeAtZero(defender);
    const sourceEffectId = `${effect.source}:zero-hp-save-damage`;
    for (const conditionId of rider.conditionIds || []) {
      T().apply(defender, conditionId, sourceId, {
        sourceEffectId,
        appliedRound: roundNumber,
        expiresRound: roundNumber + rider.durationRounds,
        expiryTiming: "target_turn_start",
        useDefaultPoisonRecovery: false,
      });
    }
  }

  function modifierDamageComponents(attacker, targetId, critical) {
    return M().bonusDamage(attacker, targetId).map((modifier) => {
      const count = modifier.dice_count * (critical ? 2 : 1);
      const rolls = D().rollMany(count, modifier.dice_size);
      return {
        source: modifier.source_name || modifier.source_effect_id,
        damage_type: modifier.damage_type,
        notation: `${count}d${modifier.dice_size}+0`,
        rolls,
        modifier: 0,
        total: rolls.reduce((sum, roll) => sum + roll, 0),
      };
    });
  }

  function resistanceBypassTypes(attacker) {
    try {
      return new Set(
        (attacker.template.damage_resistance_bypass_grants || [])
          .flatMap((grant) => grant.damage_types || []),
      );
    } catch (error) {
      console.error("Browser outgoing resistance bypass failed", { combatant: attacker?.template?.name, error });
      throw error;
    }
  }

  function naturalTwentyDamageComponents(attacker, attack, naturalRoll, existingComponents) {
    try {
      if (naturalRoll !== 20) return [];
      const grants = attacker.template.natural_twenty_attack_damage_grants || [];
      if (!grants.length) return [];
      const scores = attacker.template.ability_scores;
      if (!scores) throw new Error(`${attacker.template.name} has natural-20 attack damage without certified ability scores.`);
      const qualifiers = [...(existingComponents[0]?.source_qualifiers || [])];
      return grants.map((grant) => {
        const score = scores[grant.ability];
        if (!Number.isInteger(score)) throw new Error(`Missing certified ${grant.ability} score for natural-20 attack damage.`);
        return {
          source: grant.source_name || grant.source_id,
          damage_type: attack.damageType,
          notation: String(score),
          rolls: [],
          modifier: score,
          total: score,
          source_qualifiers: qualifiers,
        };
      });
    } catch (error) {
      console.error("Browser natural-20 attack damage failed", { combatant: attacker?.template?.name, error });
      throw error;
    }
  }

  function aggregate(components) {
    return {
      notation: components.map((part) => part.notation).join(" + "),
      rolls: components.flatMap((part) => part.rolls),
      modifier: components.reduce((sum, part) => sum + (part.modifier || 0), 0),
      total: components.reduce((sum, part) => sum + part.total, 0),
    };
  }

  function resolve(attacker, defender, attack, critical, mode, turnKey, options = {}) {
    const hpBufferBefore = defender.current_hp + defender.temporary_hp;
    const base = R().weaponDamage(
      attacker, attack, critical, mode, turnKey, options.bonusDamage || null,
      defender, Boolean(options.sneakAttackAllyAvailable),
    );
    const rolled = [
      ...base.components,
      ...modifierDamageComponents(attacker, options.targetId || null, critical),
    ];
    rolled.push(...naturalTwentyDamageComponents(attacker, attack, options.naturalRoll, rolled));
    const smite = P()?.divineSmiteComponent(attacker, defender, attack, critical) || null;
    if (smite) rolled.push(smite);
    const saveDamage = resolveSaveDamage(defender, attack);
    const saveComponentPresent = Boolean(saveDamage.component);
    if (saveComponentPresent) rolled.push(saveDamage.component);
    if (defender.template.attackDamageReductionReaction && typeof ADR()?.apply !== "function") throw new Error("Declared attack damage reduction Reaction requires browser-attack-damage-reduction.js.");
    const reduction = ADR()?.apply(defender, attack, rolled) || { components: rolled, used: false, reduction: 0, sourceId: null, sourceName: null };
    const uncanny = RD().applyUncannyDodge(attacker, defender, reduction.components);
    const bypassTypes = resistanceBypassTypes(attacker);
    const damageComponents = uncanny.components.map((part) => ({
      ...part,
      applied_total: A().adjustedDamage(
        defender, part.total, part.damage_type, true, part.source_qualifiers || [], bypassTypes.has(part.damage_type),
      ),
    }));
    const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
    const damageRoll = { ...aggregate(uncanny.components), total: appliedTotal };
    const appliedTypes = [...new Set(
      damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type),
    )];
    let damageOutcome = A().applyDamage(
      defender, appliedTotal, critical, appliedTypes, options.affectedStates || [], options.setup || null,
    );
    const effect = attack.onHitSaveDamage;
    if (defender.current_hp === 0 && saveDamageCausedZero(
      hpBufferBefore, appliedTotal, damageComponents, effect, saveComponentPresent,
    )) {
      applyZeroHpSaveDamageRider(defender, effect, turnKey);
      damageOutcome = "unconscious";
    }
    const cunningStrikeTrip = window.IRON_PIT_BROWSER_SNEAK_ATTACK?.resolveTrip(
      attacker, defender, turnKey,
    ) || { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    const cunningStrikeObscure = window.IRON_PIT_BROWSER_SNEAK_ATTACK?.resolveObscure(
      attacker, defender, turnKey,
    ) || { saveRoll: null, saveDc: null, saveSucceeded: null, applied: false };
    return {
      damageRoll, damageComponents, damageOutcome, appliedTotal, saveDamage, cunningStrikeTrip, cunningStrikeObscure,
      uncannyDodgeUsed: uncanny.used,
      damageReductionReactionUsed: reduction.used, damageReductionReactionSourceId: reduction.sourceId,
      damageReductionReactionSourceName: reduction.sourceName, damageReductionReactionReduction: reduction.reduction,
      damageReductionZeroedAttack: Boolean(reduction.zeroedAttack),
      deflectMissilesUsed: reduction.used && reduction.sourceId === "deflect-missiles",
      deflectMissilesReduction: reduction.used && reduction.sourceId === "deflect-missiles"
        ? reduction.reduction : 0,
    };
  }

  window.IRON_PIT_BROWSER_HIT_DAMAGE = {
    aggregate, applyZeroHpSaveDamageRider, resolve, resolveSaveDamage, saveDamageCausedZero,
  };
})();
