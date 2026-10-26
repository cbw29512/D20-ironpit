(() => {
  "use strict";
  function afterHit(attacker, defender, attack) {
    const rule = defender.template?.weaponHitCorrosion;
    if (!rule) return null;
    if (!window.IRON_PIT_BROWSER_WEAPON_CORROSION)
      throw new Error("Declared corrosion rule requires the shared corrosion runtime.");
    if (attack.kind === "ranged") return null; // ammunition requires separate proof
    if (attack.weaponMaterial == null || typeof attack.weaponMagical !== "boolean")
      return null; // unknown is NOT nonmagical metal
    if (!(rule.qualifyingMaterials || []).includes(attack.weaponMaterial))
      return null;
    if (rule.requiresNonmagical && attack.weaponMagical) return null;
    const id = attack.weaponId || attack.id;
    if (!id) throw new Error("Weapon corrosion requires item identity.");
    return window.IRON_PIT_BROWSER_WEAPON_CORROSION.afterHit(attacker, id, {
      hit: true, nonmagicalMetal: true,
    });
  }
  window.IRON_PIT_BROWSER_WEAPON_HIT_CORROSION = { afterHit };
})();
