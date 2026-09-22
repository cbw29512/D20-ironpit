(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const S = () => window.IRON_PIT_BROWSER_STATE;
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
    if (target.state.is_dead || !target.state.is_alive || target.state.current_hp >= S().effectiveMaxHp(target.state) || swarm(target.state)) return false;
    if (distance(healer, target) > (action.range || 5)) return false;
    if (action.targetMode === "self") return target.combatant_id === healer.combatant_id;
    if (action.targetMode === "ally") return target.combatant_id !== healer.combatant_id && target.side === healer.side;
    if (action.targetMode === "other") return target.combatant_id !== healer.combatant_id;
    return target.side === healer.side;
  }

  function selfWorthwhile(member, action) {
    return bloodied(member.state) && ["action", "bonus_action"].includes(action.actionCost);
  }

  function chooseTarget(healer, setup, action, turnKey = null) {
    if (action.actionCost === "reaction" || !E().available(healer.state, action.actionCost)) return null;
    if (!resourceAvailable(healer, action, turnKey)) return null;
    const allies = healer.side === "heroes" ? setup.heroes : setup.monsters;
    const legal = allies.filter((target) => targetAllowed(healer, target, action));
    const others = legal.filter((target) => target.combatant_id !== healer.combatant_id);
    const downed = others.filter((target) => target.state.current_hp === 0);
    if (downed.length) return downed.reduce((best, item) => item.state.death_save_failures > best.state.death_save_failures ? item : best);
    const hurt = others.filter((target) => bloodied(target.state));
    if (hurt.length) return hurt.reduce((best, item) => item.state.current_hp / S().effectiveMaxHp(item.state) < best.state.current_hp / S().effectiveMaxHp(best.state) ? item : best);
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
    return [urgency, cost, useful >= 2 ? -useful : 0, target.state.current_hp / S().effectiveMaxHp(target.state)];
  }

  function chooseAction(healer, setup, turnKey = null) {
    const choices = (healer.state.template.healingActions || []).map((action) => ({ action, target: chooseTarget(healer, setup, action, turnKey) })).filter((item) => item.target);
    choices.sort((a, b) => {
      const pa = priority(healer, setup, a.action, a.target), pb = priority(healer, setup, b.action, b.target);
      return pa[0] - pb[0] || pa[1] - pb[1] || pa[2] - pb[2] || pa[3] - pb[3];
    });
    return choices[0] || null;
  }

  function restore(state, amount) {
    if (state.is_dead || amount <= 0 || swarm(state)) return 0;
    const before = state.current_hp;
    state.current_hp = Math.min(S().effectiveMaxHp(state), before + amount);
    const healed = state.current_hp - before;
    if (healed > 0) {
      state.is_alive = true; state.is_unconscious = false; state.is_stable = false;
      state.death_save_successes = 0; state.death_save_failures = 0;
    }
    return healed;
  }

  function groupTargets(healer, setup, action, turnKey = null) {
    if ((action.maxTargets || 1) <= 1 || !resourceAvailable(healer, action, turnKey)) return [];
    return worthwhileTargets(healer, setup, action)
      .sort((a, b) => (a.state.current_hp > 0) - (b.state.current_hp > 0)
        || a.state.current_hp / S().effectiveMaxHp(a.state) - b.state.current_hp / S().effectiveMaxHp(b.state)
        || a.combatant_id.localeCompare(b.combatant_id))
      .slice(0, action.maxTargets || 1);
  }

  function selfRider(sequence, round, healer, action, healedOther) {
    const rule = healer.state.template.slot_healing_other_self_rider;
    if (!rule || !healedOther || !slotHeal(action)) return null;
    const slotLevel = Number(action.resourceId.split("-").at(-1));
    const amount = (rule.flat_bonus || 0) + (rule.per_slot_level || 0) * slotLevel;
    const before = healer.state.current_hp, healed = restore(healer.state, amount);
    if (!healed) return null;
    return {
      sequence, round_number: round, event_type: "healing",
      actor_id: healer.combatant_id, actor_name: healer.state.template.name,
      target_id: healer.combatant_id, target_name: healer.state.template.name,
      hp_before: before, hp_after: healer.state.current_hp,
      death_save_successes: healer.state.death_save_successes,
      death_save_failures: healer.state.death_save_failures,
      is_stable: healer.state.is_stable, is_dead: healer.state.is_dead,
      feature_id: rule.source_id, animation: "healing",
      description: `${healer.state.template.name} restores ${healed} HP from ${rule.source_id.replaceAll("-", " ")}.`,
    };
  }

  function resolveGroup(sequence, round, healer, targets, action, turnKey = null) {
    if ((action.maxTargets || 1) <= 1 || !targets.length || targets.length > action.maxTargets) throw new Error("Illegal group healing target set.");
    if (targets.some((target) => !targetAllowed(healer, target, action)) || !resourceAvailable(healer, action, turnKey)) throw new Error("Illegal group healing target or turn.");
    if (slotHeal(action)) {
      if (!turnKey) throw new Error("Spell-slot group healing requires an active turn key.");
      C().markSlotSpellCast(healer.state, turnKey);
    }
    E().spend(healer.state, action.actionCost);
    healer.state.resources[action.resourceId] -= action.resourceCost || 1;
    const remaining = healer.state.resources[action.resourceId], events = [];
    for (const target of targets) {
      const maximized = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.healingMaximized(target.state) || false;
      const rolls = Array.from({ length: action.diceCount || 0 }, () => maximized ? (action.diceSize || 6) : window.IRON_PIT_DICE.roll(action.diceSize || 6));
      const total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.healingBonus || 0);
      const before = target.state.current_hp, healed = restore(target.state, total);
      events.push({
        sequence: sequence++, round_number: round, event_type: "healing",
        actor_id: healer.combatant_id, actor_name: healer.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        healing_roll: { notation: `${rolls.length}d${action.diceSize || 6}+${action.healingBonus || 0}`, rolls, modifier: action.healingBonus || 0, total },
        hp_before: before, hp_after: target.state.current_hp,
        death_save_successes: target.state.death_save_successes, death_save_failures: target.state.death_save_failures,
        is_stable: target.state.is_stable, is_dead: target.state.is_dead,
        feature_id: action.id, resource_remaining: remaining, animation: action.animation || "healing",
        description: `${healer.state.template.name} uses ${action.name} on ${target.state.template.name} and restores ${healed} HP.`,
      });
    }
    const rider = selfRider(sequence, round, healer, action, targets.some((target) => target.combatant_id !== healer.combatant_id));
    if (rider) events.push(rider);
    return { events, sequence: sequence + (rider ? 1 : 0) };
  }

  function resolve(sequence, round, healer, target, action, turnKey = null) {
    if (!targetAllowed(healer, target, action) || !resourceAvailable(healer, action, turnKey)) throw new Error("Illegal healing target or turn.");
    if (slotHeal(action)) {
      if (!turnKey) throw new Error("Spell-slot healing requires an active turn key.");
      C().markSlotSpellCast(healer.state, turnKey);
    }
    E().spend(healer.state, action.actionCost);
    const maximized = window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.healingMaximized(target.state) || false;
    const rolls = Array.from({ length: action.diceCount || 0 }, () => maximized ? (action.diceSize || 6) : window.IRON_PIT_DICE.roll(action.diceSize || 6));
    const total = rolls.reduce((sum, roll) => sum + roll, 0) + (action.healingBonus || 0);
    const hpBefore = target.state.current_hp, healed = restore(target.state, total);
    let remaining = null;
    if (action.resourceId) {
      healer.state.resources[action.resourceId] -= action.resourceCost || 1;
      remaining = healer.state.resources[action.resourceId];
    }
    return {
      sequence, round_number: round, event_type: "healing", actor_id: healer.combatant_id, actor_name: healer.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      healing_roll: { notation: rolls.length ? `${rolls.length}d${action.diceSize || 6}+${action.healingBonus || 0}` : String(action.healingBonus || 0), rolls, modifier: action.healingBonus || 0, total },
      hp_before: hpBefore, hp_after: target.state.current_hp, death_save_successes: target.state.death_save_successes,
      death_save_failures: target.state.death_save_failures, is_stable: target.state.is_stable, is_dead: target.state.is_dead,
      feature_id: action.id, resource_remaining: remaining, animation: action.animation || "healing",
      description: `${healer.state.template.name} uses ${action.name} on ${target.state.template.name} and restores ${healed} HP.`,
    };
  }

  window.IRON_PIT_BROWSER_HEALING = { bloodied, chooseAction, chooseTarget, groupTargets, resolve, resolveGroup, restore, selfRider };
})();
