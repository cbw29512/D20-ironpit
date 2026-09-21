(() => {
  "use strict";

  const meanDice = (count, size) => (count || 0) * ((size || 0) + 1) / 2;

  function weaponValue(attack) {
    let damage = Number.isFinite(attack.fixedDamage)
      ? attack.fixedDamage
      : meanDice(attack.diceCount, attack.diceSize) + (attack.damageBonus || 0);
    for (const rider of attack.onHitDamage || []) {
      damage += meanDice(rider.diceCount, rider.diceSize) + (rider.damageBonus || 0);
    }
    if (attack.onHitSaveDamage) {
      const rider = attack.onHitSaveDamage;
      const full = meanDice(rider.diceCount, rider.diceSize) + (rider.damageBonus || 0);
      damage += full * (rider.successDamage === "half" ? 0.75 : 0.5);
    }
    return [damage, attack.bonus || 0, attack.id || ""];
  }

  function compareWeapons(a, b) {
    const av = weaponValue(a), bv = weaponValue(b);
    return bv[0] - av[0] || bv[1] - av[1] || String(av[2]).localeCompare(String(bv[2]));
  }

  const signatureSave = (action) => Boolean(action?.resourceId);

  window.IRON_PIT_BROWSER_OFFENSE_PRIORITY = { meanDice, weaponValue, compareWeapons, signatureSave };
})();
