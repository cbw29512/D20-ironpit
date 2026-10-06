(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const Z = () => window.IRON_PIT_BROWSER_SUPPRESSION_ZONES;
  const DD = () => {
    const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
    if (!rules?.resolveDamage) throw new Error("Save-zone damage requires the shared damage resolver.");
    return rules;
  };

  function memberInZone(member, zone) {
    if (!member.state.position || !zone.position) return false;
    return G().footprintDistanceFt(
      member.state.position, member.state.template.size, zone.position, "medium",
    ) <= zone.radius_ft;
  }

  function expire(setup, round) {
    setup.save_zones = (setup.save_zones || []).filter((zone) => zone.expires_round > round);
  }

  function chooseCenter(caster, setup, action) {
    if (!setup.map_definition || !caster.state.position) return null;
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const living = enemies.filter((enemy) => enemy.state.is_alive && !enemy.state.is_dead && enemy.state.position);
    if (!living.length) return null;
    const target = living.slice().sort((a, b) =>
      S().distance(caster, a) - S().distance(caster, b) || a.combatant_id.localeCompare(b.combatant_id))[0];
    if (S().distance(caster, target) > (action.castRangeFt || 0)) return null;
    return { ...target.state.position };
  }

  function choose(caster, setup, turnKey) {
    if (Z()?.verbalBlocked(caster, setup)) return null;
    for (const action of caster.state.template.persistent_save_zone_actions || []) {
      if (action.damageDiceCount) continue;
      if (!E().available(caster.state, action.actionCost)) continue;
      if (action.concentration && caster.state.concentration) continue;
      if (action.expendsSpellSlot && !P()?.slotSpellAvailable(caster.state, turnKey)) continue;
      if (action.resourceId && (caster.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
      const center = chooseCenter(caster, setup, action);
      if (center) return { action, center };
    }
    return null;
  }

  function scaledDice(action, slotLevel) {
    return (action.damageDiceCount || 0) + Math.max(0, slotLevel - action.level) * (action.upcastDicePerLevel || 0);
  }

  function resolveTrigger(sequence, round, target, setup, zone, turnKey, trigger) {
    if (!(zone.triggers || []).includes(trigger) || !memberInZone(target, zone)) return null;
    if (target.combatant_id === zone.source_id || target.side === zone.source_side) return null;
    if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return null;
    if (zone.oncePerTurn !== false && (zone.triggered_turn_keys || {})[target.combatant_id] === turnKey) return null;
    zone.triggered_turn_keys = zone.triggered_turn_keys || {};
    if (zone.oncePerTurn !== false) zone.triggered_turn_keys[target.combatant_id] = turnKey;
    const saveTriggers = zone.saveTriggers || [];
    const requiresSave = !saveTriggers.length || saveTriggers.includes(trigger);
    const save = requiresSave
      ? window.IRON_PIT_BROWSER_SAVING_THROWS.resolveSavingThrow(
        target.state, zone.saveAbility, zone.dc, { magicalEffect: true, spellEffect: true, roundNumber: round },
      )
      : { roll: null, succeeded: false };
    const hpBefore = target.state.current_hp;
    let damageRoll = null, damageComponents = [];
    if ((zone.damageDiceCount || 0) && zone.damageType) {
      const rolls = window.IRON_PIT_DICE.rollMany(zone.damageDiceCount, zone.damageDiceSize);
      let rawTotal = rolls.reduce((sum, value) => sum + value, 0);
      if (save.succeeded && zone.successDamage === "none") rawTotal = 0;
      else if (save.succeeded && zone.successDamage === "half") rawTotal = Math.floor(rawTotal / 2);
      const applied = DD().resolveDamage(target.state, rawTotal, zone.damageType).applied;
      damageComponents = [{
        source: zone.action_id, notation: `${zone.damageDiceCount}d${zone.damageDiceSize}`,
        rolls, modifier: 0, damage_type: zone.damageType, total: rawTotal, applied_total: applied,
      }];
      damageRoll = { notation: damageComponents[0].notation, rolls, modifier: 0, total: applied };
      if (applied) {
        const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
        window.IRON_PIT_BROWSER_ATTACK.applyDamage(target.state, applied, false, [zone.damageType], states, setup);
      }
    }
    const appliedConditions = [];
    if (!save.succeeded && zone.failedSaveConditionId && target.state.is_alive) {
      const applied = window.IRON_PIT_BROWSER_TIMED.apply(target.state, zone.failedSaveConditionId, zone.source_id, {
        sourceEffectId: zone.action_id, appliedRound: round,
        expiresRound: round + (zone.failedSaveDurationRounds || 1),
        expiryTiming: "target_turn_end",
        suppressAction: Boolean(zone.failedSaveSuppressAction),
        suppressBonusAction: Boolean(zone.failedSaveSuppressBonusAction),
        useDefaultPoisonRecovery: false,
      });
      if (applied) appliedConditions.push(applied);
    }
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: zone.source_id, actor_name: zone.action_name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      saving_throw_roll: save.roll, save_ability: zone.saveAbility, save_dc: zone.dc,
      save_succeeded: save.succeeded, damage_roll: damageRoll, damage_components: damageComponents,
      applied_condition_ids: appliedConditions, hp_before: hpBefore, hp_after: target.state.current_hp,
      is_dead: target.state.is_dead, feature_id: zone.action_id, animation: zone.animation || "save-zone",
      description: requiresSave
        ? `${target.state.template.name} ${save.succeeded ? "succeeds" : "fails"} the save against ${zone.action_name}.`
        : `${target.state.template.name} takes damage from ${zone.action_name} with no save.`,
    };
  }

  function resolveWindow(sequence, round, member, setup, turnKey, trigger) {
    expire(setup, round);
    const events = [];
    for (const zone of [...(setup.save_zones || [])]) {
      const event = resolveTrigger(sequence, round, member, setup, zone, turnKey, trigger);
      if (event) { events.push(event); sequence += 1; }
    }
    return { events, sequence };
  }

  function cast(sequence, round, caster, setup, action, position, turnKey) {
    if (Z()?.verbalBlocked(caster, setup)) throw new Error(`${action.name} cannot be cast inside a Silence effect.`);
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
    let slotLevel = action.level;
    if (action.resourceId && String(action.resourceId).startsWith("spell-slot-")) {
      slotLevel = Number(String(action.resourceId).split("-").pop());
    }
    if (action.expendsSpellSlot) P().markSlotSpellCast(caster.state, turnKey);
    E().spend(caster.state, action.actionCost);
    if (action.resourceId) caster.state.resources[action.resourceId] -= action.resourceCost || 1;
    if (action.concentration) {
      window.IRON_PIT_BROWSER_CONCENTRATION.start(
        caster.state, caster.combatant_id, action.id, round,
        [...setup.heroes, ...setup.monsters].map((member) => member.state),
        round + action.durationRounds,
      );
    }
    setup.save_zones = setup.save_zones || [];
    const zone = {
      zone_id: `${caster.combatant_id}:${action.id}:${round}:${setup.save_zones.length + 1}`,
      source_id: caster.combatant_id, source_side: caster.side,
      action_id: action.id, action_name: action.name, position: { ...position },
      radius_ft: action.radiusFt, expires_round: round + action.durationRounds,
      saveAbility: action.saveAbility, dc: action.dc,       triggers: [...(action.triggers || [])],
      saveTriggers: [...(action.saveTriggers || [])],
      oncePerTurn: action.oncePerTurn !== false,
      damageDiceCount: scaledDice(action, slotLevel), damageDiceSize: action.damageDiceSize,
      damageType: action.damageType, successDamage: action.successDamage || "none",
      failedSaveConditionId: action.failedSaveConditionId,
      failedSaveDurationRounds: action.failedSaveDurationRounds || 1,
      failedSaveSuppressAction: Boolean(action.failedSaveSuppressAction),
      failedSaveSuppressBonusAction: Boolean(action.failedSaveSuppressBonusAction),
      concentration: Boolean(action.concentration), animation: action.animation || "save-zone",
      triggered_turn_keys: {},
    };
    setup.save_zones.push(zone);
    const events = [{
      sequence, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      feature_id: action.id,
      resource_remaining: action.resourceId ? caster.state.resources[action.resourceId] : null,
      concentration_started_effect_id: action.concentration ? action.id : null,
      animation: action.animation || "save-zone",
      description: `${caster.state.template.name} casts ${action.name}.`,
    }];
    sequence += 1;
    if ((action.triggers || []).includes("appear")) {
      for (const member of [...setup.heroes, ...setup.monsters]) {
        const event = resolveTrigger(sequence, round, member, setup, zone, turnKey, "appear");
        if (event) { events.push(event); sequence += 1; }
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_SAVE_ZONES = { choose, cast, expire, resolveWindow, memberInZone };
})();
