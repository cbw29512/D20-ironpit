(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { has: () => false };

  function qualifiedDefenseKinds(target, type, attack = null) {
    const kinds = new Set();
    for (const rule of target.template.qualified_damage_defenses || []) {
      if (!(rule.damage_types || []).includes(type)) continue;
      if (rule.attack_only && !attack) continue;
      if (rule.magical !== null && rule.magical !== undefined) {
        if (!attack || Boolean(attack.magical) !== rule.magical) continue;
      }
      const material = (attack?.material || "").toLowerCase();
      if ((rule.bypass_materials || []).map((item) => item.toLowerCase()).includes(material)) continue;
      kinds.add(rule.kind);
    }
    return kinds;
  }

  function adjustedDamage(target, amount, type, allowVulnerability = true, attack = null) {
    const qualified = qualifiedDefenseKinds(target, type, attack);
    if (target.template.damage_immunities?.includes(type) || qualified.has("immunity")) return 0;
    let value = amount;
    if (target.template.damage_resistances?.includes(type) || target.temporary_damage_resistances?.includes(type)
      || T()?.ownsDamageResistance?.(target, type) || qualified.has("resistance") || Q().has(target, "petrified")) {
      value = Math.floor(value / 2);
    }
    if (allowVulnerability
      && (target.template.damage_vulnerabilities?.includes(type) || qualified.has("vulnerability"))) value *= 2;
    return value;
  }

  window.IRON_PIT_BROWSER_DAMAGE_DEFENSES = { adjustedDamage, qualifiedDefenseKinds };
})();
