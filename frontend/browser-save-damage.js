(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;

  function resolve(state, action, succeeded) {
    if (succeeded && action.successDamage === "none") return { damageRoll: null, damageComponents: [], appliedTotal: 0, damageTypes: [] };
    const packets = [];
    if (action.damageDiceCount) packets.push({
      source: action.name, diceCount: action.damageDiceCount, diceSize: action.damageDiceSize,
      damageBonus: action.damageBonus || 0, damageType: action.damageType,
    });
    packets.push(...(action.additionalDamage || []));
    const half = succeeded && action.successDamage === "half";
    const damageComponents = packets.map((packet) => {
      if (!packet.damageType) throw new Error(`${action.name} has damage dice but no damage type.`);
      const rolls = D().rollMany(packet.diceCount, packet.diceSize);
      let total = rolls.reduce((sum, roll) => sum + roll, 0) + (packet.damageBonus || 0);
      if (half) total = Math.floor(total / 2);
      total = Math.max(0, total);
      return {
        source: packet.source, notation: `${packet.diceCount}d${packet.diceSize}+${packet.damageBonus || 0}`,
        rolls, modifier: packet.damageBonus || 0, damage_type: packet.damageType, total,
        applied_total: A().adjustedDamage(state, total, packet.damageType),
      };
    });
    const appliedTotal = damageComponents.reduce((sum, part) => sum + part.applied_total, 0);
    const damageTypes = [...new Set(damageComponents.filter((part) => part.applied_total > 0).map((part) => part.damage_type))];
    const damageRoll = damageComponents.length ? {
      notation: damageComponents.map((part) => part.notation).join(" + "),
      rolls: damageComponents.flatMap((part) => part.rolls),
      modifier: damageComponents.reduce((sum, part) => sum + part.modifier, 0), total: appliedTotal,
    } : null;
    return { damageRoll, damageComponents, appliedTotal, damageTypes };
  }

  window.IRON_PIT_BROWSER_SAVE_DAMAGE = { resolve };
})();
