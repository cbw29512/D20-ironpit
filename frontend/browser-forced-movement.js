(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const sign = (value) => Number(value > 0) - Number(value < 0);

  function center(member) {
    const position = member.state.position;
    if (!position) throw new Error("Forced movement requires authoritative grid positions.");
    const side = G().footprintSide(member.state.template.size);
    const offset = (side - 1) / 2;
    return [position.x + offset, position.y + offset];
  }

  function occupiedByOther(target, candidate, setup) {
    return [...setup.heroes, ...setup.monsters].some((member) => {
      if (member.combatant_id === target.combatant_id || !member.state.position || member.state.is_dead) return false;
      return G().overlaps(
        candidate,
        target.state.template.size,
        member.state.position,
        member.state.template.size,
      );
    });
  }

  function pushAway(source, target, distanceFt, setup) {
    if (!Number.isInteger(distanceFt) || distanceFt < 0 || distanceFt % 5) {
      throw new Error("Forced push distance must be a nonnegative 5-foot increment.");
    }
    if (!distanceFt) return 0;
    if (!setup?.map_definition || !target.state.position) {
      throw new Error("Forced push requires an authoritative battle map and target position.");
    }
    const [sx, sy] = center(source), [tx, ty] = center(target);
    const dx = sign(tx - sx), dy = sign(ty - sy);
    if (!dx && !dy) throw new Error("Forced push direction is undefined for overlapping centers.");
    let current = { ...target.state.position }, moved = 0;
    for (let step = 0; step < distanceFt / 5; step += 1) {
      const candidate = { x: current.x + dx, y: current.y + dy };
      if (!G().inBounds(setup.map_definition, candidate, target.state.template.size)) break;
      if (occupiedByOther(target, candidate, setup)) break;
      current = candidate;
      moved += 5;
    }
    target.state.position = current;
    return moved;
  }

  window.IRON_PIT_BROWSER_FORCED_MOVEMENT = { pushAway };
})();