(() => {
  "use strict";

  const geometry = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const frightened = () => window.IRON_PIT_BROWSER_FRIGHTENED;
  const movement = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT;
  const reactions = () => window.IRON_PIT_BROWSER_REACTIONS;
  const grapple = () => window.IRON_PIT_BROWSER_GRAPPLE;

  function distanceToPosition(reactor, mover, moverPosition) {
    try {
      if (!reactor.state.position) throw new Error(`${reactor.combatant_id} has no grid position.`);
      return geometry().footprintDistanceFt(
        reactor.state.position, reactor.state.template.size,
        moverPosition, mover.state.template.size,
      );
    } catch (error) {
      console.error("Failed browser grid reaction distance", { reactor: reactor.combatant_id, error }); throw error;
    }
  }
  function approachesFearSource(mover, destination, setup) {
    try {
      if (!mover.state.active_effect_ids.includes("frightened")) return false;
      if (!mover.state.position) throw new Error(`${mover.combatant_id} has no grid position.`);
      const rules = frightened();
      if (!rules) throw new Error("Browser Frightened runtime is not loaded.");
      for (const source of rules.sources(mover.state, setup)) {
        if (!source.state.position) throw new Error(`Frightened source ${source.combatant_id} has no grid position.`);
        const before = geometry().footprintDistanceFt(
          mover.state.position, mover.state.template.size,
          source.state.position, source.state.template.size,
        );
        const after = geometry().footprintDistanceFt(
          destination, mover.state.template.size,
          source.state.position, source.state.template.size,
        );
        if (after < before) return true;
      }
      return false;
    } catch (error) {
      console.error("Failed browser frightened grid movement check", { mover: mover.combatant_id, error }); throw error;
    }
  }
  function executePath(sequence, round, mover, setup, path, target = null, movementSource = "speed", options = {}) {
    try {
      if (!setup.map_definition || !mover.state.position) throw new Error("Grid path execution requires map and mover position.");
      const members = [...setup.heroes, ...setup.monsters];
      const reactors = mover.side === "heroes" ? setup.monsters : setup.heroes;
      const events = [];
      let lastMovement = null;
      for (const destination of path) {
        if (approachesFearSource(mover, destination, setup)) break;
        const beforePosition = { ...mover.state.position };
        const stepCost = movement().movementStepCostFt(setup.map_definition, mover, destination, members);
        if (stepCost == null || stepCost > mover.state.movement_remaining_ft) break;
        const wasProne = mover.state.active_effect_ids.includes("prone");
        for (const reactor of reactors) {
          if (!reactor.state.position) continue;
          const event = reactions()?.resolveOpportunityAttack(
            sequence, round, reactor, mover, setup,
            distanceToPosition(reactor, mover, beforePosition),
            distanceToPosition(reactor, mover, destination),
            movementSource, options,
          );
          if (!event) continue;
          events.push(event); sequence += 1;
          const newlyProne = !wasProne && mover.state.active_effect_ids.includes("prone");
          if (mover.state.is_dead || mover.state.is_unconscious || grapple()?.speedIsZero(mover.state) || newlyProne) {
            return { events, sequence, movement: lastMovement };
          }
        }
        const beforeDistance = target ? distanceToPosition(target, mover, beforePosition) : null;
        mover.state.position = { ...destination };
        mover.state.movement_remaining_ft -= stepCost;
        const afterDistance = target ? distanceToPosition(target, mover, mover.state.position) : null;
        lastMovement = {
          sequence, round_number: round, event_type: "movement",
          actor_id: mover.combatant_id, actor_name: mover.state.template.name,
          target_id: target?.combatant_id || null, target_name: target?.state?.template?.name || null,
          distance_before_ft: beforeDistance, distance_after_ft: afterDistance,
          movement_ft: setup.map_definition.cell_size_ft || 5, movement_cost_ft: stepCost,
          grid_position_before: beforePosition, grid_position_after: { ...mover.state.position },
          grid_path: [{ ...mover.state.position }], animation: "advance",
          description: stepCost === 5 ? `${mover.state.template.name} moves 5 feet.`
            : `${mover.state.template.name} moves 5 feet, spending ${stepCost} feet of movement.`,
        };
        events.push(lastMovement); sequence += 1;
        if (mover.state.movement_remaining_ft <= 0) break;
      }
      return { events, sequence, movement: lastMovement };
    } catch (error) {
      console.error("Failed browser grid path execution", { mover: mover.combatant_id, error }); throw error;
    }
  }

  window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT = {
    distanceToPosition, approachesFearSource, executePath,
  };
})();
