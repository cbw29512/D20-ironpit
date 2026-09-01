(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function slotLevel(caster, action, turnKey) {
    if (action.level === 0) return 0;
    if (!C().slotSpellAvailable(caster.state, turnKey)) return null;
    const resourceId = `spell-slot-${action.level}`;
    return (caster.state.resources?.[resourceId] || 0) > 0 ? action.level : null;
  }

  function singleTarget(caster, setup, action) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const legal = enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= action.range);
    if (!legal.length) return null;
    return legal.reduce((best, target) => S().distance(caster, target) < S().distance(caster, best) ? target : best);
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    const spells = (caster.state.template.spell_save_actions || [])
      .map((action, index) => ({ action, index }))
      .sort((a, b) => b.action.level - a.action.level || a.index - b.index);
    for (const { action } of spells) {
      if (action.actionCost === "reaction" || action.concentration) continue;
      if (!E().available(caster.state, action.actionCost)) continue;
      const castLevel = slotLevel(caster, action, turnKey);
      if (castLevel == null) continue;
      if (action.areaRadius) {
        const placement = A().bestPlacement(caster, setup, action.areaRadius, action.range, protectedAllyIds);
        if (!placement) continue;
        return { action, slotLevel: castLevel, targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement };
      }
      const target = singleTarget(caster, setup, action);
      if (target) return { action, slotLevel: castLevel, targetIds: [target.combatant_id], placement: null };
    }
    return null;
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = { choose, slotLevel };
})();
