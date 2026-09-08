(() => {
  "use strict";
  const CELL = 5;
  const living = (member) => member.state.is_alive && !member.state.is_dead && member.state.current_hp > 0;
  const rows = (actor, setup) => actor.side === "heroes" ? [setup.monsters, setup.heroes] : [setup.heroes, setup.monsters];
  const coord = (member, members) => [members.indexOf(member) * CELL, member.position_ft];
  const distance = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

  function directedInside(area, source, point, aim) {
    const dx = aim[0] - source[0], dy = aim[1] - source[1], magnitude = Math.hypot(dx, dy);
    if (!magnitude) return false;
    const ux = dx / magnitude, uy = dy / magnitude;
    const px = point[0] - source[0], py = point[1] - source[1];
    const forward = px * ux + py * uy;
    if (forward < 0 || forward > area.lengthFt) return false;
    const perpendicular = Math.abs(px * uy - py * ux);
    return area.shape === "line" ? perpendicular <= (area.widthFt || CELL) / 2 : perpendicular <= forward / 2;
  }

  function bestDirected(actor, setup, enemies, area) {
    const [enemyRows, ownRows] = rows(actor, setup), source = coord(actor, ownRows), candidates = [];
    for (const aimed of enemies) {
      const aim = coord(aimed, enemyRows);
      const ids = enemies.filter((member) => directedInside(area, source, coord(member, enemyRows), aim))
        .map((member) => member.combatant_id);
      if (ids.length) candidates.push(ids);
    }
    candidates.sort((a, b) => b.length - a.length || a.join().localeCompare(b.join()));
    return candidates[0] || [];
  }

  function pointInside(area, center, point) { return distance(center, point) <= (area.radiusFt || 0); }
  function bestPoint(actor, setup, enemies, area) {
    const [enemyRows, ownRows] = rows(actor, setup), source = coord(actor, ownRows);
    const centers = enemies.map((member) => coord(member, enemyRows))
      .filter((center) => distance(center, source) <= (area.originRangeFt || 0));
    const candidates = centers.map((center) => enemies.filter((member) => pointInside(area, center, coord(member, enemyRows)))
      .map((member) => member.combatant_id));
    candidates.sort((a, b) => b.length - a.length || a.join().localeCompare(b.join()));
    return candidates[0] || [];
  }

  function targetIds(actor, setup, action) {
    const area = action.area;
    if (!area) return [];
    const [enemyRows, ownRows] = rows(actor, setup), enemies = enemyRows.filter(living);
    if (!enemies.length) return [];
    if (area.shape === "cone" || area.shape === "line") return bestDirected(actor, setup, enemies, area);
    if (area.shape === "emanation") {
      const source = coord(actor, ownRows);
      return enemies.filter((member) => pointInside(area, source, coord(member, enemyRows))).map((member) => member.combatant_id);
    }
    return bestPoint(actor, setup, enemies, area);
  }

  window.IRON_PIT_BROWSER_AREA_TARGETING = { targetIds };
})();
