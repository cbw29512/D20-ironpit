(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_SAVES;
  const SC = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function hazards(setup) {
    if (!Array.isArray(setup.persistent_hazards)) setup.persistent_hazards = [];
    return setup.persistent_hazards;
  }

  function positionLegal(setup, action, position) {
    if (!setup.map_definition || !G().inBounds(setup.map_definition, position, action.footprintSize)) return false;
    const members = [...setup.heroes, ...setup.monsters];
    if (members.some((member) => member.state.position && G().overlaps(
      position, action.footprintSize, member.state.position, member.state.template.size,
    ))) return false;
    return !hazards(setup).some((item) => G().overlaps(
      position, action.footprintSize, item.position, item.footprintSize,
    ));
  }

  function cast(sequence, round, caster, setup, action, position, turnKey) {
    if (!setup.map_definition || !caster.state.position) throw new Error("Persistent hazards require the authoritative grid.");
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
    const distance = G().footprintDistanceFt(
      caster.state.position, caster.state.template.size, position, action.footprintSize,
    );
    if (distance > action.castRangeFt) throw new Error(`${action.name} placement exceeds its cast range.`);
    if (!positionLegal(setup, action, position)) throw new Error(`${action.name} requires a legal unoccupied placement.`);
    const resourceId = `spell-slot-${action.level}`;
    const resource = action.level > 0 ? caster.state.resources?.[resourceId] : null;
    if (action.level > 0 && !(resource > 0)) throw new Error(`No level ${action.level} spell slot remains.`);
    if (action.level > 0) {
      SC().markSlotSpellCast(caster.state, turnKey);
      caster.state.resources[resourceId] -= 1;
    }
    E().spend(caster.state, action.actionCost);
    const list = hazards(setup);
    list.push({
      hazardId: `${caster.combatant_id}:${action.id}:${round}:${list.length + 1}`,
      sourceId: caster.combatant_id,
      sourceSide: caster.side,
      actionId: action.id,
      actionName: action.name,
      position: { ...position },
      footprintSize: action.footprintSize,
      triggerRadiusFt: action.triggerRadiusFt,
      saveAbility: action.saveAbility,
      dc: action.dc,
      failureDamage: action.failureDamage,
      successDamage: action.successDamage,
      damageType: action.damageType,
      remainingDamageCapacity: action.maxTotalDamage,
      expiresRound: round + action.durationRounds,
      triggeredTurnKeys: {},
      animation: action.animation || "persistent-hazard",
    });
    return {
      event: {
        sequence, round_number: round, event_type: "feature",
        actor_id: caster.combatant_id, actor_name: caster.state.template.name,
        feature_id: action.id,
        resource_remaining: action.level > 0 ? caster.state.resources[resourceId] : null,
        animation: action.animation || "persistent-hazard",
        description: `${caster.state.template.name} creates ${action.name}.`,
      },
      sequence: sequence + 1,
    };
  }

  function resolveEntries(sequence, round, mover, setup, turnKey) {
    if (!mover.state.position) return { events: [], sequence };
    hazards(setup);
    setup.persistent_hazards = setup.persistent_hazards.filter((item) =>
      round < item.expiresRound && item.remainingDamageCapacity > 0
    );
    const events = [], states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
    for (const item of [...setup.persistent_hazards]) {
      if (item.sourceSide === mover.side) continue;
      if (item.triggeredTurnKeys[mover.combatant_id] === turnKey) continue;
      const distance = G().footprintDistanceFt(
        mover.state.position, mover.state.template.size, item.position, item.footprintSize,
      );
      if (distance > item.triggerRadiusFt) continue;
      item.triggeredTurnKeys[mover.combatant_id] = turnKey;
      const save = S().resolveSavingThrow(mover.state, item.saveAbility, item.dc);
      const raw = save.succeeded ? item.successDamage : item.failureDamage;
      const applied = A().adjustedDamage(mover.state, raw, item.damageType);
      const before = mover.state.current_hp;
      if (applied > 0) A().applyDamage(mover.state, applied, false, [item.damageType], states);
      item.remainingDamageCapacity = Math.max(0, item.remainingDamageCapacity - applied);
      const survivalLog = window.IRON_PIT_BROWSER_UNDEAD_FORTITUDE?.consumeLog(mover.state) || "";
      events.push({
        sequence, round_number: round, event_type: "saving_throw",
        actor_id: item.sourceId, actor_name: item.actionName,
        target_id: mover.combatant_id, target_name: mover.state.template.name,
        saving_throw_roll: save.roll, save_ability: item.saveAbility, save_dc: item.dc,
        save_succeeded: save.succeeded,
        damage_roll: { notation: String(raw), rolls: [], modifier: 0, total: applied },
        damage_components: [{
          source: item.actionName, notation: String(raw), rolls: [], modifier: 0,
          damage_type: item.damageType, total: raw, applied_total: applied,
        }],
        hp_before: before, hp_after: mover.state.current_hp, is_dead: mover.state.is_dead,
        feature_id: item.actionId, animation: item.animation,
        description: `${mover.state.template.name} ${save.succeeded ? "succeeds" : "fails"} the save against ${item.actionName} and takes ${applied} ${item.damageType} damage.${survivalLog}`,
      });
      sequence += 1;
      if (item.remainingDamageCapacity <= 0) {
        setup.persistent_hazards = setup.persistent_hazards.filter((hazard) => hazard.hazardId !== item.hazardId);
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_PERSISTENT_HAZARDS = { cast, positionLegal, resolveEntries };
})();
