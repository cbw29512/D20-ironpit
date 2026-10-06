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

  function applyIncomingTypeResistance(target, amount, type) {
    try {
      const rule = target.template?.incomingDamageTypeResistanceReaction;
      const economy = window.IRON_PIT_ACTION_ECONOMY;
      const timed = window.IRON_PIT_BROWSER_TIMED;
      if (!rule || amount <= 0 || target.current_hp <= 0 || target.is_dead
          || !economy?.available(target, "reaction") || !timed) return false;
      economy.spend(target, "reaction");
      timed.apply(target, "incoming-damage-type-resistance", rule.source_id, {
        sourceEffectId: rule.source_id,
        appliedRound: target.current_round,
        ownedDamageResistances: [type],
      });
      return true;
    } catch (error) {
      console.error("Incoming damage-type resistance failed.", error);
      throw error;
    }
  }

  function expireCurrentTurnTypeResistances(setup) {
    const timed = window.IRON_PIT_BROWSER_TIMED;
    if (!timed || !setup) return;
    for (const member of [...(setup.heroes || []), ...(setup.monsters || [])]) {
      for (const effect of [...(member.state.timed_effects || [])]) {
        if (effect.effect_id === "incoming-damage-type-resistance") timed.removeEffect(member.state, effect);
      }
    }
  }

  function absorptionRule(target, type) {
    try {
      const matches = (target.template.damage_absorptions || []).filter((rule) => rule.damageType === type);
      if (matches.length > 1) throw new Error(`${target.template.name} has multiple absorption rules for ${type}.`);
      return matches[0] || null;
    } catch (error) {
      throw new Error(`Damage absorption lookup failed: ${error.message}`);
    }
  }

  function adjustedDamage(target, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) {
    try {
      const conditional = conditionalKinds(target, type, sourceQualifiers);
      if (absorptionRule(target, type) || target.template.damage_immunities?.includes(type)
          || (target.zone_damage_immunities || []).includes(type) || conditional.has("immunity")) return 0;
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
    } catch (error) {
      console.error("Damage estimation failed.", { target: target?.template?.name, type, error });
      throw error;
    }
  }

  function resolveDamage(target, amount, type, allowVulnerability = true, sourceQualifiers = [], ignoreResistance = false) {
    try {
      const absorption = absorptionRule(target, type);
      if (absorption) {
        if (amount <= 0) return { applied: 0, healed: 0, sourceName: absorption.sourceName };
        const healing = window.IRON_PIT_BROWSER_HEALING;
        if (!healing?.restore) throw new Error("Browser healing runtime is required for damage absorption.");
        const healed = healing.restore(target, amount);
        return { applied: 0, healed, sourceName: absorption.sourceName };
      }

      const beforeReaction = adjustedDamage(
        target, amount, type, allowVulnerability, sourceQualifiers, ignoreResistance,
      );
      if (beforeReaction <= 0) return { applied: beforeReaction, healed: 0, sourceName: null };

      const conditional = conditionalKinds(target, type, sourceQualifiers);
      const timed = window.IRON_PIT_BROWSER_TIMED;
      const conditions = window.IRON_PIT_BROWSER_CONDITION_RULES;
      const alreadyResisted = target.template.damage_resistances?.includes(type)
        || target.temporary_damage_resistances?.includes(type)
        || timed?.ownsDamageResistance?.(target, type)
        || conditional.has("resistance")
        || conditions?.has?.(target, "petrified");
      if (!ignoreResistance && !alreadyResisted) applyIncomingTypeResistance(target, amount, type);
      const applied = adjustedDamage(
        target, amount, type, allowVulnerability, sourceQualifiers, ignoreResistance,
      );
      return { applied, healed: 0, sourceName: null };
    } catch (error) {
      throw new Error(`Damage amount resolution failed: ${error.message}`);
    }
  }

  window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES = {
    adjustedDamage, resolveDamage, applyIncomingTypeResistance, conditionalKinds, expireCurrentTurnTypeResistances,
  };
})();
