(() => {
  "use strict";

  const ZONE_DEAFEN = "suppression-zone-deafen";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  function memberInZone(member, zone) {
    if (!member.state.position || !zone.position) return false;
    return G().footprintDistanceFt(
      member.state.position, member.state.template.size, zone.position, "tiny",
    ) <= zone.radius_ft;
  }

  function covering(member, setup) {
    return (setup.suppression_zones || []).filter((zone) => memberInZone(member, zone));
  }

  function verbalBlocked(member, setup) {
    return covering(member, setup).some((zone) => zone.blocks_verbal_spells || zone.blocksVerbalSpells);
  }

  function expire(setup, round) {
    setup.suppression_zones = (setup.suppression_zones || []).filter((zone) => zone.expires_round > round);
  }

  function syncDeafen(member, deafened, round) {
    const owned = (member.state.timed_effects || []).filter((effect) => effect.source_effect_id === ZONE_DEAFEN);
    if (deafened && !owned.length) {
      window.IRON_PIT_BROWSER_TIMED.apply(member.state, "deafened", "suppression-zone", {
        sourceEffectId: ZONE_DEAFEN, appliedRound: round, useDefaultPoisonRecovery: false,
      });
      return;
    }
    if (deafened) return;
    for (const effect of owned) window.IRON_PIT_BROWSER_TIMED.removeEffect(member.state, effect);
  }

  function sync(setup, round = 1) {
    for (const member of [...setup.heroes, ...setup.monsters]) {
      const zones = covering(member, setup);
      syncDeafen(member, zones.some((zone) => zone.deafens !== false), round);
      const thunder = zones.some((zone) => zone.thunder_immunity !== false && zone.thunderImmunity !== false);
      const immunities = (member.state.zone_damage_immunities || []).filter((item) => item !== "thunder");
      if (thunder) immunities.push("thunder");
      member.state.zone_damage_immunities = immunities;
    }
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
    if (verbalBlocked(caster, setup)) return null;
    for (const action of caster.state.template.suppression_zone_actions || []) {
      if (!E().available(caster.state, action.actionCost)) continue;
      if (action.concentration && caster.state.concentration) continue;
      if (action.expendsSpellSlot && !P()?.slotSpellAvailable(caster.state, turnKey)) continue;
      const resourceId = action.resourceId;
      if (resourceId && (caster.state.resources[resourceId] || 0) < (action.resourceCost || 1)) continue;
      const center = chooseCenter(caster, setup, action);
      if (center) return { action, center };
    }
    return null;
  }

  function cast(sequence, round, caster, setup, action, position, turnKey) {
    if (verbalBlocked(caster, setup)) throw new Error(`${action.name} cannot be cast inside a Silence effect.`);
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.actionCost} is unavailable for ${action.name}.`);
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
    setup.suppression_zones = setup.suppression_zones || [];
    setup.suppression_zones.push({
      zone_id: `${caster.combatant_id}:${action.id}:${round}:${setup.suppression_zones.length + 1}`,
      source_id: caster.combatant_id, action_id: action.id, action_name: action.name,
      position: { ...position }, radius_ft: action.radiusFt, expires_round: round + action.durationRounds,
      deafens: action.deafens !== false, blocks_verbal_spells: action.blocksVerbalSpells !== false,
      thunder_immunity: action.thunderImmunity !== false, concentration: Boolean(action.concentration),
    });
    sync(setup, round);
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: caster.combatant_id, actor_name: caster.state.template.name,
      feature_id: action.id,
      resource_remaining: action.resourceId ? caster.state.resources[action.resourceId] : null,
      concentration_started_effect_id: action.concentration ? action.id : null,
      animation: action.animation || "silence",
      description: `${caster.state.template.name} casts ${action.name}.`,
    };
  }

  window.IRON_PIT_BROWSER_SUPPRESSION_ZONES = {
    covering, verbalBlocked, expire, sync, choose, cast,
  };
})();
