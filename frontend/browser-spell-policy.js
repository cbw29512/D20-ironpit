(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const O = () => window.IRON_PIT_BROWSER_OFFENSE_VALUE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function scaledSpell(action, slotLevel) {
    if (action.level === 0) {
      if (slotLevel !== 0) throw new Error("Cantrips cannot expend spell slots.");
      return action;
    }
    if (slotLevel < action.level || slotLevel > 9) throw new Error(`Illegal slot level ${slotLevel} for ${action.name}.`);
    const levelsAbove = slotLevel - action.level;
    if (!levelsAbove) return action;
    if (!(action.upcastDicePerLevel > 0)) throw new Error(`${action.name} has no certified higher-slot scaling.`);
    if (action.damageComponents?.length) throw new Error("Multi-component spell upcasting requires component-specific scaling data.");
    return { ...action, damageDiceCount: (action.damageDiceCount || 0) + levelsAbove * action.upcastDicePerLevel };
  }

  function slotLevels(caster, action, turnKey) {
    return C().legalSlotLevels(caster.state, turnKey, action.level, {
      higherSlotScaling: (action.upcastDicePerLevel || 0) > 0,
    });
  }

  function slotLevel(caster, action, turnKey) {
    const levels = slotLevels(caster, action, turnKey);
    return levels.length ? levels.at(-1) : null;
  }

  function legalSingleTargets(caster, setup, action) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead
      && target.state.current_hp > 0 && S().distance(caster, target) <= action.range
      && (!action.requiresTargetHearing || !target.state.active_effect_ids.includes("deafened"))
      && (!action.requiresTargetSight || window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(caster.state, target.state)));
  }

  function chooseActionAtSlot(caster, setup, action, castLevel, protectedAllyIds = []) {
    try {
      if (!action || action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) return null;
      const scaled = scaledSpell(action, castLevel);
      const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      if (action.area) {
        const placements = window.IRON_PIT_BROWSER_AREA_TARGETING
          .legalPlacements(caster, setup, action.area, action.range)
          .filter((placement) => !(placement.friendlyIds || []).length);
        if (!placements.length) return null;
        placements.sort((a, b) =>
          b.enemyIds.length - a.enemyIds.length || a.friendlyIds.length - b.friendlyIds.length);
        const placement = placements[0];
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        return { action, slotLevel: castLevel, targetIds: [...placement.enemyIds], placement, expectedDamage: score };
      }
      if (action.areaRadius) {
        const placement = A().bestPlacement(caster, setup, action.areaRadius, action.range, protectedAllyIds);
        if (!placement) return null;
        const score = placement.enemyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0)
          - placement.friendlyIds.reduce((sum, id) => sum + O().saveSpell(members.get(id), scaled), 0);
        return { action, slotLevel: castLevel,
          targetIds: [...placement.enemyIds, ...placement.friendlyIds], placement, expectedDamage: score };
      }
      const legal = legalSingleTargets(caster, setup, action);
      if (!legal.length) return null;
      legal.sort((a, b) => O().saveSpell(b, scaled) - O().saveSpell(a, scaled)
        || a.state.current_hp - b.state.current_hp || a.combatant_id.localeCompare(b.combatant_id));
      const target = legal[0];
      return { action, slotLevel: castLevel, targetIds: [target.combatant_id],
        placement: null, expectedDamage: O().saveSpell(target, scaled) };
    } catch (error) {
      console.error("Browser fixed-slot save-spell selection failed", { caster: caster?.combatant_id, spell: action?.id, error });
      throw error;
    }
  }

  function choose(caster, setup, turnKey, protectedAllyIds = []) {
    try {
      const candidates = [];
      for (const [index, action] of (caster.state.template.spell_save_actions || []).entries()) {
        if (action.actionCost === "reaction" || action.concentration || !E().available(caster.state, action.actionCost)) continue;
        for (const castLevel of slotLevels(caster, action, turnKey)) {
          const selected = chooseActionAtSlot(caster, setup, action, castLevel, protectedAllyIds);
          if (selected) candidates.push({ ...selected, index, score: selected.expectedDamage });
        }
      }
      candidates.sort((a, b) => b.score - a.score || a.action.level - b.action.level
        || a.index - b.index);
      if (!candidates.length) return null;
      const best = candidates[0];
      return { action: best.action, slotLevel: best.slotLevel, targetIds: best.targetIds,
        placement: best.placement, expectedDamage: best.expectedDamage };
    } catch (error) {
      console.error("Browser save-spell selection failed", { caster: caster?.combatant_id, error });
      throw error;
    }
  }

  function chooseById(caster, setup, turnKey, spellId, protectedAllyIds = []) {
    try {
      const action = (caster.state.template.spell_save_actions || []).find((item) => item.id === spellId);
      if (!action) return null;
      const levels = slotLevels(caster, action, turnKey);
      if (!levels.length) return null;
      return chooseActionAtSlot(caster, setup, action, levels.at(-1), protectedAllyIds);
    } catch (error) {
      console.error("Browser named save-spell selection failed", { caster: caster?.combatant_id, spellId, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_SPELL_POLICY = {
    choose, chooseActionAtSlot, chooseById, scaledSpell, slotLevel, slotLevels,
  };
})();
