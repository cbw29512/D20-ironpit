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

  window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = { conditionalKinds };
})();
