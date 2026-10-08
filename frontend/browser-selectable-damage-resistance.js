(() => {
  "use strict";

  const average = (count, size, bonus = 0) => count > 0 ? count * (size + 1) / 2 + bonus : Math.max(0, bonus);

  function scoresFor(member, setup, allowedTypes, forbiddenQualifiers = []) {
    try {
      const result = Object.fromEntries(allowedTypes.map((type) => [type, 0]));
      const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
      const forbidden = new Set(forbiddenQualifiers);

    for (const enemy of enemies || []) {
      const template = enemy.state.template;
      for (const attack of template.attacks || []) {
        if (!(attack.damageType in result)) continue;
        const qualifiers = window.IRON_PIT_BROWSER_MODIFIERS?.damageSourceQualifiers(enemy.state, attack)
          || new Set(["attack", "weapon", attack.kind, ...(attack.damageSourceQualifiers || [])]);
        if ([...forbidden].some((item) => qualifiers.has(item))) continue;
        result[attack.damageType] += average(attack.diceCount || 0, attack.diceSize || 6, attack.damageBonus || 0);
        for (const rider of attack.onHitDamage || []) {
          if (rider.damageType in result) result[rider.damageType] += average(rider.diceCount || 0, rider.diceSize || 6, rider.damageBonus || 0);
        }
      }

      for (const action of [...(template.saving_throw_actions || []), ...(template.spell_save_actions || [])]) {
        for (const part of action.damageComponents || []) {
          if (part.damageType in result) result[part.damageType] += average(part.diceCount || 0, part.diceSize || 6, part.damageBonus || 0);
        }
        if (action.damageType && action.damageType in result) {
          result[action.damageType] += average(action.damageDiceCount || 0, action.damageDiceSize || 6, action.damageBonus || 0);
        }
      }

      for (const action of template.spell_attack_actions || []) {
        if (!action.damageType || !(action.damageType in result)) continue;
        result[action.damageType] += (action.attackCount || 1)
          * average(action.damageDiceCount || 0, action.damageDiceSize || 6, action.damageBonus || 0);
      }
    }
      return result;
    } catch (error) {
      console.error("Failed to score opponent damage types", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function scores(member, setup) {
    const rule = member.state.template.selectable_damage_resistance;
    if (!rule) return {};
    return scoresFor(member, setup, rule.allowed_damage_types || [], rule.forbidden_source_qualifiers || []);
  }

  function chooseTimed(member, setup, choices) {
    try {
      const sorted = [...choices].sort((a, b) => (b.priority || 0) - (a.priority || 0));
      const preferred = sorted[0] || null;
      if (!preferred || preferred.selectionStrategy !== "incoming-damage" || !setup) return preferred;
      const variants = sorted.filter((action) =>
        action.selectionGroup === preferred.selectionGroup
        && action.selectionStrategy === preferred.selectionStrategy
        && action.resourceId === preferred.resourceId);
      const types = [...new Set(variants.map((action) => {
        if ((action.damageResistances || []).length !== 1) {
          throw new Error("Incoming-damage selection requires exactly one resistance type.");
        }
        return action.damageResistances[0];
      }))];
      const incoming = scoresFor(member, setup, types);
      if (!Object.values(incoming).some((score) => score > 0)) return preferred;
      return variants.sort((a, b) =>
        (incoming[b.damageResistances[0]] || 0) - (incoming[a.damageResistances[0]] || 0)
        || (b.priority || 0) - (a.priority || 0))[0];
    } catch (error) {
      console.error("Threat-aware buff selection failed.", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function choose(member, setup) {
    const rule = member.state.template.selectable_damage_resistance;
    if (!rule) return null;
    const values = scores(member, setup);
    const allowed = rule.allowed_damage_types || [];
    return allowed.reduce((best, type) => {
      if (best == null) return type;
      return (values[type] || 0) > (values[best] || 0) ? type : best;
    }, null);
  }

  function resolve(sequence, member, setup) {
    const rule = member.state.template.selectable_damage_resistance;
    if (!rule || member.state.opening_buff_id) return null;
    const selected = choose(member, setup);
    if (!selected) return null;
    member.state.active_conditional_damage_defenses = (member.state.active_conditional_damage_defenses || [])
      .filter((item) => item.id !== rule.source_id);
    member.state.active_conditional_damage_defenses.push({
      id: rule.source_id,
      kind: "resistance",
      damageTypes: [selected],
      requiredSourceQualifiers: [],
      forbiddenSourceQualifiers: [...(rule.forbidden_source_qualifiers || [])],
    });
    member.state.opening_buff_id = rule.source_id;
    return {
      sequence,
      round_number: 0,
      event_type: "feature",
      actor_id: member.combatant_id,
      actor_name: member.state.template.name,
      target_id: member.combatant_id,
      target_name: member.state.template.name,
      feature_id: rule.source_id,
      animation: "damage-resistance",
      description: `Precombat preparation: ${member.state.template.name} uses ${rule.source_name} and chooses ${selected} resistance.`,
    };
  }

  window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE = { choose, resolve, scores, scoresFor, chooseTimed };
})();
