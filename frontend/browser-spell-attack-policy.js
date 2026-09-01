(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function slotAvailable(member, spell, turnKey) {
    if (spell.level === 0) return true;
    if (!C().slotSpellAvailable(member.state, turnKey)) return false;
    return (member.state.resources?.[`spell-slot-${spell.level}`] || 0) > 0;
  }

  function choose(member, setup, turnKey) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    const spells = (member.state.template.spell_attack_actions || [])
      .map((spell, index) => ({ spell, index }))
      .sort((a, b) => b.spell.level - a.spell.level || a.index - b.index);
    for (const { spell } of spells) {
      if (spell.actionCost === "reaction" || !E().available(member.state, spell.actionCost)) continue;
      if (!slotAvailable(member, spell, turnKey)) continue;
      const legal = enemies.filter((target) => target.state.is_alive && !target.state.is_dead
        && target.state.current_hp > 0 && S().distance(member, target) <= spell.range);
      legal.sort((a, b) => S().distance(member, a) - S().distance(member, b)
        || a.combatant_id.localeCompare(b.combatant_id));
      if (legal.length) return { action: spell, target: legal[0] };
    }
    return null;
  }

  window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY = { choose };
})();
