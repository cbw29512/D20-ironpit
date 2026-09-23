(() => {
  "use strict";

  function conditionalKinds(target, type, sourceQualifiers = []) {
    try {
      const qualifiers = new Set(sourceQualifiers || []);
      const kinds = new Set();
      for (const rule of target.template.conditional_damage_defenses || []) {
        if (!(rule.damageTypes || []).includes(type)) continue;
        const required = rule.requiredSourceQualifiers || [];
        const forbidden = rule.forbiddenSourceQualifiers || [];
        if (!required.every((item) => qualifiers.has(item))) continue;
        if (forbidden.some((item) => qualifiers.has(item))) continue;
        kinds.add(rule.kind);
      }
      return kinds;
    } catch (error) {
      console.error("Failed browser conditional damage-defense matching.", {
        target: target?.template?.name, type, sourceQualifiers, error,
      });
      throw error;
    }
  }

  function adjustedDamage(target, amount, type, allowVulnerability = true, sourceQualifiers = []) {
    try {
      const conditional = conditionalKinds(target, type, sourceQualifiers);
      if (target.template.damage_immunities?.includes(type) || conditional.has("immunity")) return 0;
      let value = amount;
      const timed = window.IRON_PIT_BROWSER_TIMED;
      const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES;
      const resisted = target.template.damage_resistances?.includes(type)
        || target.temporary_damage_resistances?.includes(type)
        || timed?.ownsDamageResistance?.(target, type)
        || conditional.has("resistance")
        || conditions?.has?.(target, "petrified");
      if (resisted) value = Math.floor(value / 2);
      if (allowVulnerability && (target.template.damage_vulnerabilities?.includes(type) || conditional.has("vulnerability"))) value *= 2;
      return value;
    } catch (error) {
      console.error("Failed browser damage-defense adjustment.", { target: target?.template?.name, type, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = { adjustedDamage, conditionalKinds };
})();
