(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;

  function slotLevels(member, spell, turnKey) {
    return C().legalSlotLevels(member.state, turnKey, spell.level, {
      higherSlotScaling: (spell.attacksPerSlotAbove || 0) > 0 || (spell.upcastDicePerLevel || 0) > 0,
    });
  }

  function castOptions(member, spell, turnKey) {
    try {
      const slots = slotLevels(member, spell, turnKey)
        .map((slotLevel) => ({ slotLevel, alternateCast: null }));
      const alternates = (member.state.template.alternate_spell_cast_grants || [])
        .filter((grant) => grant.spell_id === spell.id
          && (grant.resource_id == null
            || (member.state.resources?.[grant.resource_id] || 0) >= (grant.resource_cost || 1)))
        .map((grant) => ({ slotLevel: grant.cast_level, alternateCast: grant }));
      return [...slots, ...alternates];
    } catch (error) {
      console.error("Failed to build browser spell-attack cast options.", {
        combatantId: member?.combatant_id, spellId: spell?.id, turnKey, error,
      });
      throw error;
    }
  }

  function attackCountAtSlot(spell, slotLevel) {
    if (spell.level === 0) return spell.attackCount || 1;
    return (spell.attackCount || 1) + Math.max(0, slotLevel - spell.level) * (spell.attacksPerSlotAbove || 0);
  }

  function choose(member, setup, turnKey) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    const candidates = [];
    for (const [index, spell] of (member.state.template.spell_attack_actions || []).entries()) {
      if (spell.actionCost === "reaction" || !E().available(member.state, spell.actionCost)) continue;
      const options = castOptions(member, spell, turnKey);
      if (!options.length) continue;
      const policy = P();
      const castRange = policy?.effectiveRange
        ? policy.effectiveRange(member.state, spell.range)
        : spell.range;
      for (const { slotLevel, alternateCast } of options) {
        const attackCount = attackCountAtSlot(spell, slotLevel);
        const extraDice = spell.level > 0
          ? Math.max(0, slotLevel - spell.level) * (spell.upcastDicePerLevel || 0)
          : 0;
        const scaled = extraDice ? { ...spell, damageDiceCount: spell.damageDiceCount + extraDice } : spell;
        for (const target of enemies) {
          const distance = S().distance(member, target);
          if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0 || distance > castRange || window.IRON_PIT_BROWSER_GRID_BARRIERS && !window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(member, target, setup)) continue;
          candidates.push({
            spell, target, index, slotLevel, alternateCast,
            score: O().spellAttack(member, target, scaled, setup) * attackCount,
            rangeModifier: policy?.availableRangeModifier
              ? policy.availableRangeModifier(member.state, spell.range, distance)
              : null,
          });
        }
      }
    }
    candidates.sort((a, b) => b.score - a.score || Number(a.alternateCast != null) - Number(b.alternateCast != null)
      || a.slotLevel - b.slotLevel || a.spell.level - b.spell.level
      || a.target.state.current_hp - b.target.state.current_hp || a.index - b.index
      || a.target.combatant_id.localeCompare(b.target.combatant_id));
    return candidates.length ? {
      action: candidates[0].spell,
      target: candidates[0].target,
      expectedDamage: candidates[0].score,
      slotLevel: candidates[0].slotLevel,
      alternateCast: candidates[0].alternateCast || null,
      rangeModifier: candidates[0].rangeModifier || null,
    } : null;
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = { attackCountAtSlot, castOptions, choose, slotLevels };
})();
