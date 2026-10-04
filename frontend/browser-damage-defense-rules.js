(() => {
  "use strict";

  function conditionalKinds(target, type, sourceQualifiers = []) {
    const qualifiers = new Set(sourceQualifiers || []);
    const kinds = new Set();
    const rules = [
      ...(target.template.conditional_damage_defenses || []),
      ...(target.active_conditional_damage_defenses || []),
    ];
    for (const rule of rules) {
      if (!(rule.damageTypes || []).includes(type)) continue;
      if (!(rule.requiredSourceQualifiers || []).every((item) => qualifiers.has(item))) continue;
      if ((rule.forbiddenSourceQualifiers || []).some((item) => qualifiers.has(item))) continue;
      kinds.add(rule.kind);
    }
    return kinds;
  }

  function adjustedDamage(target, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) {
    const conditional = conditionalKinds(target, type, sourceQualifiers);
    if (target.template.damage_immunities?.includes(type) || (target.zone_damage_immunities || []).includes(type) || conditional.has("immunity")) return 0;
    let value = amount;
    const timed = window.IRON_PIT_BROWSER_TIMED;
    const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES;
    const resisted = target.template.damage_resistances?.includes(type)
      || target.temporary_damage_resistances?.includes(type)
      || timed?.ownsDamageResistance?.(target, type)
      || conditional.has("resistance")
      || conditions?.has?.(target, "petrified");
    if (resisted && !ignoreResistance) value = Math.floor(value / 2);
    if (allowVulnerability && (
      target.template.damage_vulnerabilities?.includes(type) || conditional.has("vulnerability")
    )) value *= 2;
    return value;
  }

  window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = { adjustedDamage, conditionalKinds };
})();
