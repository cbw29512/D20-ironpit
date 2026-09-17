(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const Z = () => window.IRON_PIT_BROWSER_ZERO_HP;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const MK = () => window.IRON_PIT_BROWSER_MONK_2014 || {
    applyDeflectMissiles: (_defender, _attack, components) => ({ components, used: false, reduction: 0 }),
  };
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
    const saveDamage = resolveSaveDamage(defender, attack);
    const saveComponentPresent = Boolean(saveDamage.component);
    const rolled = [...base.components];
    if (saveComponentPresent) rolled.push(saveDamage.component);
    const deflect = MK().applyDeflectMissiles(defender, attack, rolled);
    const uncanny = RD().applyUncannyDodge(attacker, defender, deflect.components);
    const damageComponents = uncanny.components.map((part) => ({
      ...part,
      applied_total: A().adjustedDamage(defender, part.total, part.damage_type),
    }));
    const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
    const damageRoll = { ...aggregate(uncanny.components), total: appliedTotal };
    const appliedTypes = [...new Set(
      damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type),
    )];
    let damageOutcome = A().applyDamage(
      defender, appliedTotal, critical, appliedTypes, options.affectedStates || [],
    );
    const effect = attack.onHitSaveDamage;
    if (defender.current_hp === 0 && saveDamageCausedZero(
      hpBufferBefore, appliedTotal, damageComponents, effect, saveComponentPresent,
    )) {
      applyZeroHpSaveDamageRider(defender, effect, turnKey);
      damageOutcome = "unconscious";
    }
    return {
      damageRoll, damageComponents, damageOutcome, appliedTotal, saveDamage,
      uncannyDodgeUsed: uncanny.used, deflectMissilesUsed: deflect.used,
      deflectMissilesReduction: deflect.reduction,
    };
  }

  window.IRON_PIT_BROWSER_HIT_DAMAGE = {
    aggregate, applyZeroHpSaveDamageRider, resolve, resolveSaveDamage, saveDamageCausedZero,
  };
})();