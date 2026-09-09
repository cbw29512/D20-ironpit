(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;

  function zonePositions(map, zone, member) {
    try {
      const side = G().footprintSide(member.state.template.size);
      const maxX = zone.x + zone.width_squares - side;
      const maxY = zone.y + zone.height_squares - side;
      if (maxX < zone.x || maxY < zone.y) return [];
      const xValues = Array.from({ length: maxX - zone.x + 1 }, (_, i) => zone.x + i);
      const backline = F().usesBackline(member.state.template);
      const frontEast = zone.front_edge === "east";
      const towardFront = !backline;
      if (frontEast === towardFront) xValues.reverse();
      const centerY = zone.y + (zone.height_squares - 1) / 2;
      const yValues = Array.from({ length: maxY - zone.y + 1 }, (_, i) => zone.y + i)
        .sort((a, b) => Math.abs((a + (side - 1) / 2) - centerY)
          - Math.abs((b + (side - 1) / 2) - centerY) || a - b);
      const positions = [];
      for (const x of xValues) {
        for (const y of yValues) {
          const position = { x, y };
          if (G().inBounds(map, position, member.state.template.size)) positions.push(position);
        }
      }
      return positions;
    } catch (error) {
      console.error("Failed to enumerate browser deployment positions", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function overlapsPlaced(member, position, placed) {
    try {
      return placed.some(({ member: other, position: otherPosition }) => G().overlaps(
        position, member.state.template.size, otherPosition, other.state.template.size,
      ));
    } catch (error) {
      console.error("Failed to test browser deployment overlap", { id: member?.combatant_id, error });
      throw error;
    }
  }

  function placementOrder(members) {
    try {
      return members.map((member, index) => ({ member, index }))
        .sort((a, b) => G().footprintSide(b.member.state.template.size)
          - G().footprintSide(a.member.state.template.size)
          || Number(F().usesBackline(a.member.state.template)) - Number(F().usesBackline(b.member.state.template))
          || a.index - b.index)
        .map(({ member }) => member);
    } catch (error) {
      console.error("Failed to order browser deployment combatants", { error });
      throw error;
    }
  }

  function packZone(map, zone, members) {
    try {
      const ordered = placementOrder(members), placed = [];
      function search(index) {
        try {
          if (index >= ordered.length) return true;
          const member = ordered[index];
          for (const position of zonePositions(map, zone, member)) {
            if (overlapsPlaced(member, position, placed)) continue;
            placed.push({ member, position });
            if (search(index + 1)) return true;
            placed.pop();
          }
          return false;
        } catch (error) {
          console.error("Browser deployment search failed", { index, error });
          throw error;
        }
      }
      if (!search(0)) throw new Error("Combatants cannot fit inside the requested deployment zone.");
      const byId = new Map(placed.map(({ member, position }) => [member.combatant_id, position]));
      return members.map((member) => ({ combatant_id: member.combatant_id, position: { ...byId.get(member.combatant_id) } }));
    } catch (error) {
      console.error("Failed to pack browser deployment zone", { count: members?.length, zone, error });
      throw error;
    }
  }

  function apply(members, assignments) {
    try {
      const byId = new Map(assignments.map((item) => [item.combatant_id, item.position]));
      if (byId.size !== members.length || members.some((member) => !byId.has(member.combatant_id))) {
        throw new Error("Deployment assignments must match the combatant set exactly.");
      }
      for (const member of members) member.state.position = { ...byId.get(member.combatant_id) };
    } catch (error) {
      console.error("Failed to apply browser grid placement", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_PLACEMENT = { apply, packZone };
})();
