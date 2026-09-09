(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const X = () => window.IRON_PIT_BROWSER_REACTIONS;
  const G = () => window.IRON_PIT_BROWSER_GRAPPLE;
  const GM = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT;
  const GS = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT_SUPPORT;
  const GR = () => window.IRON_PIT_BROWSER_GRID_REACTION_SUPPORT;

  function preview(mover, target, desired) {
    try {
      if (desired < 0) throw new Error("Desired distance cannot be negative.");
      const before = S().distance(mover, target);
      const moved = Math.min(Math.max(0, before - desired), mover.state.movement_remaining_ft);
      const direction = mover.position_ft < target.position_ft ? 1 : -1;
      return { position: mover.position_ft + direction * moved, moved };
    } catch (error) {
      console.error("Failed legacy browser movement preview", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function gridMoveToward(sequence, round, mover, target, setup, desired, movementSource, options) {
    try {
      if (!setup.map_definition || !mover.state.position || !target.state.position) {
        throw new Error("Grid movement requires map and combatant positions.");
      }
      const members = [...setup.heroes, ...setup.monsters];
      const plan = GM().planToward(
        setup.map_definition, mover, target, members, desired, mover.state.movement_remaining_ft,
      );
      if (!plan.path.length) return { events: [], sequence, movement: null };
      const events = [], reactors = mover.side === "heroes" ? setup.monsters : setup.heroes;
      let lastMovement = null;
      for (const destination of plan.path) {
        if (GR().approachesFearSource(mover, destination, setup)) break;
        const beforePosition = { ...mover.state.position };
        const stepCost = GS().movementStepCostFt(setup.map_definition, mover, destination, members);
        if (stepCost == null || stepCost > mover.state.movement_remaining_ft) break;
        const wasProne = mover.state.active_effect_ids.includes("prone");
        for (const reactor of reactors) {
          if (!reactor.state.position) continue;
          const event = X()?.resolveOpportunityAttack(
            sequence, round, reactor, mover, setup,
            GR().distanceToPosition(reactor, mover, beforePosition),
            GR().distanceToPosition(reactor, mover, destination),
            movementSource, options,
          );
          if (!event) continue;
          events.push(event); sequence += 1;
          const newlyProne = !wasProne && mover.state.active_effect_ids.includes("prone");
          if (mover.state.is_dead || mover.state.is_unconscious || G()?.speedIsZero(mover.state) || newlyProne) {
            return { events, sequence, movement: lastMovement };
          }
        }
        const beforeDistance = S().distance(mover, target);
        mover.state.position = { ...destination };
        mover.state.movement_remaining_ft -= stepCost;
        const afterDistance = S().distance(mover, target);
        lastMovement = {
          sequence, round_number: round, event_type: "movement",
          actor_id: mover.combatant_id, actor_name: mover.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          distance_before_ft: beforeDistance, distance_after_ft: afterDistance,
          movement_ft: setup.map_definition.cell_size_ft || 5, movement_cost_ft: stepCost,
          grid_position_before: beforePosition, grid_position_after: { ...mover.state.position },
          grid_path: [{ ...mover.state.position }], animation: "advance",
          description: stepCost === 5 ? `${mover.state.template.name} moves 5 feet.`
            : `${mover.state.template.name} moves 5 feet, spending ${stepCost} feet of movement.`,
        };
        events.push(lastMovement); sequence += 1;
        if (afterDistance <= desired || mover.state.movement_remaining_ft <= 0) break;
      }
      return { events, sequence, movement: lastMovement };
    } catch (error) {
      console.error("Failed browser grid reaction movement", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  function moveToward(sequence, round, mover, target, setup, desired, movementSource = "speed", options = {}) {
    try {
      if (setup?.map_definition) {
        if (!mover.state.position || !target.state.position) throw new Error("Grid encounter cannot mix position authority.");
        return gridMoveToward(sequence, round, mover, target, setup, desired, movementSource, options);
      }
      const proposal = preview(mover, target, desired);
      if (!proposal.moved) return { events: [], sequence, movement: null };
      const events = [], wasProne = mover.state.active_effect_ids.includes("prone");
      if (setup && X()) {
        const reactors = mover.side === "heroes" ? setup.monsters : setup.heroes;
        for (const reactor of reactors) {
          const before = Math.abs(reactor.position_ft - mover.position_ft);
          const after = Math.abs(reactor.position_ft - proposal.position);
          const event = X().resolveOpportunityAttack(sequence, round, reactor, mover, setup, before, after, movementSource, options);
          if (!event) continue;
          events.push(event); sequence += 1;
          const newlyProne = !wasProne && mover.state.active_effect_ids.includes("prone");
          if (mover.state.is_dead || mover.state.is_unconscious || G()?.speedIsZero(mover.state) || newlyProne) {
            return { events, sequence, movement: null };
          }
        }
      }
      const movement = S().moveToward(mover, target, desired);
      return { events, sequence, movement };
    } catch (error) {
      console.error("Failed browser reaction-aware movement", { mover: mover.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_REACTION_MOVEMENT = { moveToward };
})();