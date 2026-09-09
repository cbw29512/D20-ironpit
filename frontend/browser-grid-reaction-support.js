(() => {
  "use strict";

  const geometry = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;

  function distanceToPosition(reactor, mover, moverPosition) {
    try {
      if (!reactor.state.position) throw new Error(`${reactor.combatant_id} has no grid position.`);
      return geometry().footprintDistanceFt(
        reactor.state.position,
        reactor.state.template.size,
        moverPosition,
        mover.state.template.size,
      );
    } catch (error) {
      console.error("Failed browser grid reaction distance", { reactor: reactor.combatant_id, error });
      throw error;
    }
  }

  function approachesFearSource(mover, destination, setup) {
    try {
      if (!mover.state.active_effect_ids.includes("frightened")) return false;
      if (!mover.state.position) throw new Error(`${mover.combatant_id} has no grid position.`);
      const sourceIds = new Set((mover.state.timed_effects || [])
        .filter((effect) => effect.effect_id === "frightened")
        .map((effect) => effect.source_id));
      if (!sourceIds.size) return false;
      const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
      for (const sourceId of sourceIds) {
        const source = members.get(sourceId);
        if (!source?.state.position) continue;
        const before = geometry().footprintDistanceFt(
          mover.state.position,
          mover.state.template.size,
          source.state.position,
          source.state.template.size,
        );
        const after = geometry().footprintDistanceFt(
          destination,
          mover.state.template.size,
          source.state.position,
          source.state.template.size,
        );
        if (after < before) return true;
      }
      return false;
    } catch (error) {
      console.error("Failed browser frightened grid movement check", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT = { distanceToPosition, approachesFearSource };
})();