(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_DICE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;

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
    let total = rolls.reduce((sum, roll) => sum + roll, 0) + (effect.damageBonus || 0);
    if (save.succeeded && effect.successDamage === "half") total = Math.floor(total / 2);
    result.component = {
      source: effect.source || attack.name,
      damage_type: effect.damageType,
      notation: `${effect.diceCount}d${effect.diceSize}+${effect.damageBonus || 0}`,
      rolls, modifier: effect.damageBonus || 0, total,
    };
    return result;
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
    const base = R().weaponDamage(
      attacker, attack, critical, mode, turnKey, options.bonusDamage || null,
      defender, Boolean(options.sneakAttackAllyAvailable),
    );
    const saveDamage = resolveSaveDamage(defender, attack);
    const rolled = [...base.components];
    if (saveDamage.component) rolled.push(saveDamage.component);
    const damageComponents = rolled.map((part) => ({
      ...part,
      applied_total: A().adjustedDamage(defender, part.total, part.damage_type),
    }));
    const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
    const damageRoll = { ...aggregate(rolled), total: appliedTotal };
    const appliedTypes = [...new Set(
      damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type),
    )];
    const damageOutcome = A().applyDamage(
      defender, appliedTotal, critical, appliedTypes, options.affectedStates || [],
    );
    return { damageRoll, damageComponents, damageOutcome, appliedTotal, saveDamage };
  }

  window.IRON_PIT_BROWSER_HIT_DAMAGE = { aggregate, resolve, resolveSaveDamage };
})();
