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
      const casts = C().legalSlotLevels(caster.state, turnKey, action.level, {
        higherSlotScaling: (action.projectilesPerSlotAbove || 0) > 0,
      }).map((slotLevel) => ({ slotLevel, alternateCast: null }));
      casts.push(...(caster.state.template.alternate_spell_cast_grants || [])
        .filter((grant) => grant.spell_id === action.id)
        .filter((grant) => !grant.resource_id
          || (caster.state.resources?.[grant.resource_id] || 0) >= (grant.resource_cost || 1))
        .map((grant) => ({ slotLevel: grant.cast_level, alternateCast: grant })));
      for (const { slotLevel, alternateCast } of casts) {
        const projectileCount = action.projectileCount
          + (slotLevel - action.level) * (action.projectilesPerSlotAbove || 0);
        for (const target of enemies) {
          const distance = S().distance(caster, target);
          if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0
            || distance > action.range || window.IRON_PIT_BROWSER_GRID_BARRIERS && !window.IRON_PIT_BROWSER_GRID_BARRIERS.clearBetweenMembers(caster, target, setup)) continue;
          candidates.push({
            action, target, slotLevel, projectileCount, index, alternateCast,
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
