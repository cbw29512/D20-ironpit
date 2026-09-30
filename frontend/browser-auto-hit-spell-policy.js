(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function choose(caster, setup, turnKey) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const candidates = [];
    for (const [index, action] of (caster.state.template.auto_hit_spell_actions || []).entries()) {
      if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) continue;
      for (const slotLevel of C().legalSlotLevels(caster.state, turnKey, action.level, {
        higherSlotScaling: (action.projectilesPerSlotAbove || 0) > 0,
      })) {
        const projectileCount = action.projectileCount
          + (slotLevel - action.level) * (action.projectilesPerSlotAbove || 0);
        for (const target of enemies) {
          const distance = S().distance(caster, target);
          if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0
            || distance > action.range || !window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(caster, target, setup)) continue;
          candidates.push({
            action, target, slotLevel, projectileCount, index,
            expectedDamage: O().autoHitSpell(target, action, projectileCount),
            damageMaximizer: C().safeDamageMaximizer(caster.state, action.id, slotLevel),
          });
        }
      }
    }
    candidates.sort((a, b) => b.expectedDamage - a.expectedDamage
      || a.action.level - b.action.level
      || a.target.state.current_hp - b.target.state.current_hp
      || a.index - b.index
      || a.target.combatant_id.localeCompare(b.target.combatant_id));
    return candidates[0] || null;
  }

  window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY = { choose };
})();
