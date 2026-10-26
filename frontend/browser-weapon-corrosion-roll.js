(() => {
  "use strict";
  function adjust(attacker, attack, rolled) {
    const id = attack.weaponId || attack.id;
    if (!id) throw new Error("Corroded weapon roll requires its original item ID.");
    const corrosion = window.IRON_PIT_BROWSER_WEAPON_CORROSION;
    if (!corrosion) throw new Error("Weapon corrosion runtime missing.");
    const penalty = corrosion.modifier(attacker, id);
    if (!penalty) return rolled;
    const total = corrosion.weaponDamage(attacker, id, Math.max(0, rolled.total));
    return {
      ...rolled, total, modifier: rolled.modifier + penalty,
      notation: `${rolled.notation} [corrosion ${penalty}]`,
    };
  }
  window.IRON_PIT_BROWSER_WEAPON_CORROSION_ROLL = { adjust };
})();
