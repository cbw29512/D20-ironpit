(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;

  function gcd(a, b) {
    let x = Math.abs(a), y = Math.abs(b);
    while (y) [x, y] = [y, x % y];
    return x;
  }

  function rayStep(source, mover) {
    const dx = mover.x - source.x, dy = mover.y - source.y;
    const divisor = gcd(dx, dy);
    if (!divisor) return [0, 0];
    return [dx / divisor, dy / divisor];
  }

  function pushStraightAway(mover, source, setup, distanceFt) {
    if (distanceFt < 0 || distanceFt % 5) throw new Error("Forced movement distance must be a nonnegative multiple of 5 feet.");
    if (!setup?.map_definition || !mover?.state?.position || !source?.state?.position) {
      throw new Error("Forced grid movement requires authoritative positions.");
    }
    const [stepX, stepY] = rayStep(source.state.position, mover.state.position);
    if (!stepX && !stepY) return 0;
    const members = [...setup.heroes, ...setup.monsters];
    let moved = 0;
    for (let i = 0; i < distanceFt / 5; i += 1) {
      const destination = { x: mover.state.position.x + stepX, y: mover.state.position.y + stepY };
      if (!G().inBounds(setup.map_definition, destination, mover.state.template.size)) break;
      if (window.IRON_PIT_BROWSER_GRID_BARRIERS?.blocksTransition(
        mover.state.position, destination, setup.persistent_barriers || [],
      )) break;
      const blocked = members.some((member) => member.combatant_id !== mover.combatant_id
        && member.state.position && G().overlaps(destination, mover.state.template.size,
          member.state.position, member.state.template.size));
      if (blocked) break;
      mover.state.position = destination;
      moved += 5;
    }
    return moved;
  }

  function pullStraightToward(mover, source, setup, distanceFt) {
    if (distanceFt < 0 || distanceFt % 5) throw new Error("Forced movement distance must be a nonnegative multiple of 5 feet.");
    if (!setup?.map_definition || !mover?.state?.position || !source?.state?.position) {
      throw new Error("Forced grid movement requires authoritative positions.");
    }
    const [awayX, awayY] = rayStep(source.state.position, mover.state.position);
    const stepX = -awayX, stepY = -awayY;
    if (!stepX && !stepY) return 0;
    const members = [...setup.heroes, ...setup.monsters];
    let moved = 0;
    for (let i = 0; i < distanceFt / 5; i += 1) {
      const destination = { x: mover.state.position.x + stepX, y: mover.state.position.y + stepY };
      if (!G().inBounds(setup.map_definition, destination, mover.state.template.size)) break;
      if (window.IRON_PIT_BROWSER_GRID_BARRIERS?.blocksTransition(
        mover.state.position, destination, setup.persistent_barriers || [],
      )) break;
      const blocked = members.some((member) => member.combatant_id !== mover.combatant_id
        && member.state.position && G().overlaps(destination, mover.state.template.size,
          member.state.position, member.state.template.size));
      if (blocked) break;
      mover.state.position = destination;
      moved += 5;
    }
    return moved;
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { pullStraightToward, pushStraightAway };
})();
