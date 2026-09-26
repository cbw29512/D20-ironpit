(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function damageTypes(spell) {
    const result = new Set();
    if (spell?.damageType) result.add(spell.damageType);
    for (const component of (spell?.damageComponents || [])) {
      if (component.damageType) result.add(component.damageType);
    }
    return result;
  }

  function active(state, option) {
    return (state.timed_effects || []).some((effect) =>
      effect.source_id === state.template.id
      && effect.source_effect_id === option.id
    );
  }

  function applyTimedResistance(caster, spell, round) {
    try {
      const options = [...(caster.state.template.spellCastTimedResistances || [])]
        .sort((a, b) => (b.priority || 0) - (a.priority || 0));
      const types = damageTypes(spell);
      for (const option of options) {
        if (!types.has(option.qualifyingDamageType)) continue;
        if (T().ownsDamageResistance(caster.state, option.resistanceDamageType)) continue;
        const current = caster.state.resources?.[option.resourceId] || 0;
        if (current < option.resourceCost) continue;
        caster.state.resources[option.resourceId] = current - option.resourceCost;
        T().apply(caster.state, option.id, caster.combatant_id, {
          sourceEffectId: option.id,
          sourceTemplate: caster.state.template,
          appliedRound: round,
          expiresRound: round + option.durationRounds,
          expiryTiming: "source_turn_start",
          expiresAtStartOfSourceTurn: true,
          ownedDamageResistances: [option.resistanceDamageType],
          useDefaultPoisonRecovery: false,
        });
        return option;
      }
      return null;
    } catch (error) {
      console.error("Spell-cast timed resistance failed.", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_CAST_EFFECTS = { applyTimedResistance, damageTypes };
})();
