(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const bloodied = (state) => state.current_hp * 2 <= S().effectiveMaxHp(state);
  const distance = (a, b) => Math.abs(a.position_ft - b.position_ft);
  const swarm = (state) => state.template.traits?.includes("swarm");
  const slotHeal = (action) => Boolean(action.resourceId?.startsWith("spell-slot-"));

  function resourceAvailable(member, action, turnKey = null) {
    if (!action.resourceId) return true;
    if (slotHeal(action) && (!turnKey || !C().slotSpellAvailable(member.state, turnKey))) return false;
    return (member.state.resources[action.resourceId] || 0) >= (action.resourceCost || 1);
  }

  function targetAllowed(healer, target, action) {
    if (target.state.is_dead || !target.state.is_alive
      || target.state.current_hp >= S().effectiveMaxHp(target.state) || swarm(target.state)) return false;
    const creatureType = String(target.state.template.creature_type || "").split(" (")[0].toLowerCase();
    const excluded = new Set((action.excludedCreatureTypes || []).map((value) => String(value).toLowerCase()));
    if (creatureType && excluded.has(creatureType)) return false;
    if (action.areaRadiusFt == null && distance(healer, target) > (action.range || 5)) return false;
    if (action.targetMode === "self") return target.combatant_id === healer.combatant_id;
    if (action.targetMode === "ally") return target.combatant_id !== healer.combatant_id && target.side === healer.side;
    if (action.targetMode === "other") return target.combatant_id !== healer.combatant_id;
    return target.side === healer.side;
  }

  const selfWorthwhile = (member, action) => bloodied(member.state)
    && ["action", "bonus_action"].includes(action.actionCost);

  function chooseTarget(healer, setup, action, turnKey = null) {
    if (action.actionCost === "reaction" || !E().available(healer.state, action.actionCost)) return null;
    if (!resourceAvailable(healer, action, turnKey)) return null;
    const allies = healer.side === "heroes" ? setup.heroes : setup.monsters;
    const legal = allies.filter((target) => targetAllowed(healer, target, action));
    const others = legal.filter((target) => target.combatant_id !== healer.combatant_id);
    const downed = others.filter((target) => target.state.current_hp === 0);
    if (downed.length) return downed.reduce((best, item) =>
      item.state.death_save_failures > best.state.death_save_failures ? item : best);
    const hurt = others.filter((target) => bloodied(target.state));
    if (hurt.length) return hurt.reduce((best, item) =>
      item.state.current_hp / S().effectiveMaxHp(item.state)
        < best.state.current_hp / S().effectiveMaxHp(best.state) ? item : best);
    const self = legal.find((target) => target.combatant_id === healer.combatant_id);
    return self && selfWorthwhile(healer, action) ? self : null;
  }

  function worthwhileTargets(healer, setup, action) {
    const allies = healer.side === "heroes" ? setup.heroes : setup.monsters;
    return allies.filter((target) => targetAllowed(healer, target, action)
      && (target.state.current_hp === 0 || bloodied(target.state)));
  }

  function priority(healer, setup, action, target) {
    const ally = target.combatant_id !== healer.combatant_id;
    const urgency = ally && target.state.current_hp === 0 ? 0 : ally ? 1 : 2;
    const cost = action.actionCost === "bonus_action" ? 0 : 1;
    const useful = Math.min(action.maxTargets || 1, worthwhileTargets(healer, setup, action).length);
    return [urgency, cost, useful >= 2 ? -useful : 0,
      target.state.current_hp / S().effectiveMaxHp(target.state)];
  }

  function chooseAction(healer, setup, turnKey = null) {
    const choices = (healer.state.template.healingActions || [])
      .map((action) => ({ action, target: chooseTarget(healer, setup, action, turnKey) }))
      .filter((item) => item.target);
    choices.sort((a, b) => {
      const pa = priority(healer, setup, a.action, a.target);
      const pb = priority(healer, setup, b.action, b.target);
      return pa[0] - pb[0] || pa[1] - pb[1] || pa[2] - pb[2] || pa[3] - pb[3];
    });
    return choices[0] || null;
  }

  function groupTargets(healer, setup, action, turnKey = null) {
    if ((action.maxTargets || 1) <= 1 || !resourceAvailable(healer, action, turnKey)) return [];
    let targets = worthwhileTargets(healer, setup, action)
      .sort((a, b) => (a.state.current_hp > 0) - (b.state.current_hp > 0)
        || a.state.current_hp / S().effectiveMaxHp(a.state)
          - b.state.current_hp / S().effectiveMaxHp(b.state)
        || a.combatant_id.localeCompare(b.combatant_id));
    if (action.areaRadiusFt != null) {
      const placement = A()?.bestFriendlyPlacement(
        healer, setup, action.areaRadiusFt, action.range || 5,
        targets.map((item) => item.combatant_id),
      );
      if (!placement) return [];
      const allowed = new Set(placement.targetIds);
      targets = targets.filter((item) => allowed.has(item.combatant_id));
    }
    return targets.slice(0, action.maxTargets || 1);
  }

  function areaTargetsFit(healer, setup, action, targets) {
    if (action.areaRadiusFt == null) return true;
    if (!setup) return false;
    const ids = targets.map((target) => target.combatant_id);
    return Boolean(A()?.bestFriendlyPlacement(
      healer, setup, action.areaRadiusFt, action.range || 5, ids, ids,
    ));
  }

  window.IRON_PIT_BROWSER_HEALING_POLICY = {
    areaTargetsFit, bloodied, chooseAction, chooseTarget, groupTargets,
    resourceAvailable, slotHeal, swarm, targetAllowed, worthwhileTargets,
  };
})();
