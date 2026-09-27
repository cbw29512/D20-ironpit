(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELL_POLICY;

  function slotAvailable(member, spell, turnKey) {
    if (spell.level === 0) return true;
    if (!C().slotSpellAvailable(member.state, turnKey)) return false;
    for (let level = spell.level; level <= 9; level += 1) {
      if ((member.state.resources?.[`spell-slot-${level}`] || 0) > 0) return true;
    }
    return false;
  }

  function choose(member, setup, turnKey) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    const candidates = [];
    for (const [index, spell] of (member.state.template.spell_attack_actions || []).entries()) {
      if (spell.actionCost === "reaction" || !E().available(member.state, spell.actionCost)) continue;
      if (!slotAvailable(member, spell, turnKey)) continue;
      const policy = P();
      const castRange = policy?.effectiveRange
        ? policy.effectiveRange(member.state, spell.range)
        : spell.range;
      for (const target of enemies) {
        const distance = S().distance(member, target);
        if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0 || distance > castRange) continue;
        candidates.push({
          spell, target, index, score: O().spellAttack(member, target, spell, setup),
          rangeModifier: policy?.availableRangeModifier
            ? policy.availableRangeModifier(member.state, spell.range, distance)
            : null,
        });
      }
    }
    candidates.sort((a, b) => b.score - a.score || a.spell.level - b.spell.level
      || a.target.state.current_hp - b.target.state.current_hp || a.index - b.index
      || a.target.combatant_id.localeCompare(b.target.combatant_id));
    return candidates.length ? {
      action: candidates[0].spell,
      target: candidates[0].target,
      expectedDamage: candidates[0].score,
      rangeModifier: candidates[0].rangeModifier || null,
    } : null;
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = { choose };
})();
