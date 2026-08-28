(() => {
  "use strict";

  const dice = window.IRON_PIT_DICE;
  const barbarian = window.IRON_PIT_BARBARIAN;

  function resolve(actor, target, weapon, critical, mode, sneakAttack) {
    const components = [];
    const weaponRolls = dice.rollMany(weapon.count * (critical ? 2 : 1), weapon.size);
    components.push({
      source: weapon.name,
      rolls: weaponRolls,
      total: weaponRolls.reduce((a, b) => a + b, 0) + weapon.damageBonus,
      damageType: weapon.damageType,
    });
    if (sneakAttack) {
      const rolls = dice.rollMany(actor.template.sneakAttackDice * (critical ? 2 : 1), 6);
      components.push({ source: "Sneak Attack", rolls, total: rolls.reduce((a, b) => a + b, 0), damageType: weapon.damageType });
    }
    if (mode === "advantage" && weapon.conditionalAdvantageDie) {
      const rolls = dice.rollMany(critical ? 2 : 1, weapon.conditionalAdvantageDie);
      components.push({ source: "Advantage damage", rolls, total: rolls.reduce((a, b) => a + b, 0), damageType: weapon.damageType });
    }
    const rageBonus = barbarian.damageBonus(actor, weapon);
    if (rageBonus) components.push({ source: "Rage", rolls: [], total: rageBonus, damageType: weapon.damageType });
    const rolls = components.flatMap((component) => component.rolls);
    const rawTotal = components.reduce((sum, component) => sum + component.total, 0);
    const mitigation = barbarian.damageTaken(target, components);
    return {
      notation: components.map((component) => component.source).join(" + "),
      rolls,
      modifier: weapon.damageBonus + rageBonus,
      total: rawTotal,
      applied: mitigation.applied,
      resisted: mitigation.resisted,
      components,
    };
  }

  window.IRON_PIT_DAMAGE = { resolve };
})();
