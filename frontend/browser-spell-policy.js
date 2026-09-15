(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_AREA_TARGETING;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function slotLevel(caster, action, turnKey) {
    return C().actionResourceAvailable(caster.state, action, turnKey) ? action.level : null;
  }

  function legalSingleTargets(caster, setup, action) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= action.range);
  }

  function normalizedArea(action) {
    if (action.area) return action.area;
    return action.areaRadius ? { shape: "radius", origin: "point", radiusFt: action.areaRadius } : null;
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    void protectedAllyIds;
    const candidates = [], members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
      if (action.actionCost === "reaction" || action.concentration || !E().available(caster.state, action.actionCost)) continue;
      const castLevel = slotLevel(caster, action, turnKey);
      if (castLevel == null) continue;
      const area = normalizedArea(action);
      if (area) {
        const placements = T().legalPlacements(caster, setup, area, action.range);
        if (!placements.length) continue;
        const scored = placements.map((placement) => ({ placement,
          score: placement.targetIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), action), 0) }));
        scored.sort((a, b) => b.score - a.score || b.placement.targetIds.length - a.placement.targetIds.length
          || a.placement.targetIds.join("|").localeCompare(b.placement.targetIds.join("|")));
        candidates.push({ action, index, score: scored[0].score, slotLevel: castLevel,
          targetIds: [...scored[0].placement.targetIds], placement: scored[0].placement });
        continue;
      }
      for (const target of legalSingleTargets(caster, setup, action)) {
        candidates.push({ action, index, score: O().saveSpell(target, action), slotLevel: castLevel,
          targetIds: [target.combatant_id], placement: null, hp: target.state.current_hp });
      }
    }
    candidates.sort((a, b) => b.score - a.score || a.action.level - b.action.level
      || (a.hp ?? Number.MAX_SAFE_INTEGER) - (b.hp ?? Number.MAX_SAFE_INTEGER) || a.index - b.index);
    if (!candidates.length) return null;
    const best = candidates[0];
    return { action: best.action, slotLevel: best.slotLevel, targetIds: best.targetIds,
      placement: best.placement, expectedDamage: best.score };
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = { choose, normalizedArea, slotLevel };
})();