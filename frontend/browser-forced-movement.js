(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;

  function pushStraightAway(mover, source, setup, distanceFt) {
    if (distanceFt < 0 || distanceFt % 5) throw new Error("Forced movement distance must be a nonnegative multiple of 5 feet.");
    if (!setup?.map_definition || !mover?.state?.position || !source?.state?.position) {
      throw new Error("Forced grid movement requires authoritative positions.");
    }
    const dx = mover.state.position.x - source.state.position.x;
    const dy = mover.state.position.y - source.state.position.y;
    const stepX = dx === 0 ? 0 : (dx > 0 ? 1 : -1);
    const stepY = dy === 0 ? 0 : (dy > 0 ? 1 : -1);
    if (!stepX && !stepY) return 0;
    const members = [...setup.heroes, ...setup.monsters];
    let moved = 0;
    for (let i = 0; i < distanceFt / 5; i += 1) {
      const destination = { x: mover.state.position.x + stepX, y: mover.state.position.y + stepY };
      if (!G().inBounds(setup.map_definition, destination, mover.state.template.size)) break;
      const blocked = members.some((member) => member.combatant_id !== mover.combatant_id
        && member.state.position && G().overlaps(destination, mover.state.template.size,
          member.state.position, member.state.template.size));
      if (blocked) break;
      mover.state.position = destination;
      moved += 5;
    }
    return moved;
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { pushStraightAway };
})();
