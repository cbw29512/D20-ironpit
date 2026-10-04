(() => {
  "use strict";

  function cellIsDifficult(zones, cell, mover) {
    const A = window.IRON_PIT_BROWSER_AREA_SHAPES;
    const point = A.cellCenterFt(cell.x, cell.y);
    const countered = window.IRON_PIT_BROWSER_DEBUFF_COUNTERS?.difficultTerrainMultiplier
      ? window.IRON_PIT_BROWSER_DEBUFF_COUNTERS.difficultTerrainMultiplier(mover.state, true) <= 1
      : false;
    if (countered) return false;
    return zones.some((zone) => {
      const center = A.cellCenterFt(zone.center.x, zone.center.y);
      return A.radiusContains(center, point, zone.radius_ft || zone.radiusFt);
    });
  }

  function destinationIsDifficult(zones, mover, destination) {
    const G = window.IRON_PIT_BROWSER_GRID_GEOMETRY;
    return G.occupiedCells(destination, mover.state.template.size)
      .some(([x, y]) => cellIsDifficult(zones, { x, y }, mover));
  }

  function applySpellTerrain(setup, caster, action, center, round) {
    if (!action.createsDifficultTerrain && !action.creates_difficult_terrain) return null;
    const radius = action.area?.radiusFt || action.area?.radius_ft || action.areaRadius;
    if (!radius) throw new Error(`${action.name} creates Difficult Terrain without a radius.`);
    const zone = {
      zone_id: `${caster.combatant_id}:${action.id}:${round}:${(setup.temporary_terrain_zones || []).length + 1}`,
      source_id: caster.combatant_id,
      action_id: action.id,
      action_name: action.name,
      center: { ...center },
      radius_ft: radius,
      source_is_magical: true,
      expires_round: round + (action.difficultTerrainDurationRounds || action.difficult_terrain_duration_rounds || 1),
      expiry_timing: "source_turn_end",
    };
    setup.temporary_terrain_zones = [...(setup.temporary_terrain_zones || []), zone];
    return zone;
  }

  function expireSource(setup, sourceId, round) {
    setup.temporary_terrain_zones = (setup.temporary_terrain_zones || []).filter((zone) =>
      !(zone.source_id === sourceId && (zone.expires_round || 0) <= round));
  }

  window.IRON_PIT_BROWSER_TEMPORARY_TERRAIN = {
    destinationIsDifficult, applySpellTerrain, expireSource,
  };
})();
