(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function slotAvailable(member, spell, turnKey) {
    if (spell.level === 0) return true;
    if (!C().slotSpellAvailable(member.state, turnKey)) return false;
    return (member.state.resources?.[`spell-slot-${spell.level}`] || 0) > 0;
  }

  function choose(member, setup, turnKey) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    const candidates = [];
    for (const [index, spell] of (member.state.template.spell_attack_actions || []).entries()) {
      if (spell.actionCost === "reaction" || !E().available(member.state, spell.actionCost)) continue;
      if (!slotAvailable(member, spell, turnKey)) continue;
      for (const target of enemies) {
        if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0 || S().distance(member, target) > spell.range) continue;
        candidates.push({ spell, target, index, score: O().spellAttack(member, target, spell, setup) });
      }
    }
    candidates.sort((a, b) => b.score - a.score || a.spell.level - b.spell.level
      || a.target.state.current_hp - b.target.state.current_hp || a.index - b.index
      || a.target.combatant_id.localeCompare(b.target.combatant_id));
    return candidates.length ? { action: candidates[0].spell, target: candidates[0].target } : null;
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = { choose };
})();
