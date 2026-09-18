(() => {
  "use strict";

  const C = () => window.IRON_PIT_BROWSER_CUNNING_ACTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const G = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const O = () => window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function movementBudget(member) {
    const base = member.state.movement_remaining_ft;
    const aggressive = member.state.template.traits?.includes("aggressive");
    const canBonusMove = aggressive && E().available(member.state, "bonus_action");
    return { base, max: base + (canBonusMove ? M().effectiveSpeed(member.state) : 0), canBonusMove };
  }

  function chooseIntent(member, setup, turnKey) {
    try {
      if (!E().available(member.state, "action") || !setup.map_definition) return null;
      if (!member.state.position) throw new Error("Grid offensive movement requires an authoritative attacker position.");
      const members = [...setup.heroes, ...setup.monsters];
      const budget = movementBudget(member);
      const candidates = [];
      let legalNow = false;
      for (const target of F().targetOrder(member, setup)) {
        if (!target.state.position) throw new Error("Grid offensive movement requires authoritative target positions.");
        const distance = S().distance(member, target);
        for (const option of O().rangesForTarget(member, target, turnKey)) {
          if (distance <= option.range) {
            legalNow = true;
            continue;
          }
          const plan = G().planToward(
            setup.map_definition,
            member,
            target,
            members,
            option.range,
            budget.max,
          );
          if (!plan.goal_reachable || !plan.path.length || plan.final_distance_ft >= distance) continue;
          candidates.push({
            cost: plan.movement_cost_ft,
            distance,
            targetId: target.combatant_id,
            family: option.family,
            range: option.range,
            usesBonusActionMovement: budget.canBonusMove && plan.movement_cost_ft > budget.base,
          });
        }
      }
      if (legalNow || !candidates.length) return null;
      candidates.sort((a, b) => a.cost - b.cost || a.distance - b.distance
        || a.targetId.localeCompare(b.targetId) || a.family.localeCompare(b.family) || b.range - a.range);
      const best = candidates[0];
      return {
        targetId: best.targetId,
        desiredDistanceFt: best.range,
        family: best.family,
        usesBonusActionMovement: best.usesBonusActionMovement,
      };
    } catch (error) {
      console.error("Failed browser offensive movement intent", { member: member.combatant_id, error });
      throw error;
    }
  }

  function move(sequence, round, member, setup, turnKey) {
    try {
      if (!setup.map_definition) return { events: [], sequence };
      const events = [];
      const dash = C()?.useDash(sequence, round, member, setup, turnKey);
      if (dash) {
        events.push(dash);
        sequence += 1;
      }
      const intent = chooseIntent(member, setup, turnKey);
      if (!intent) return { events, sequence };
      const target = [...setup.heroes, ...setup.monsters]
        .find((candidate) => candidate.combatant_id === intent.targetId);
      if (!target) throw new Error(`Missing offensive movement target ${intent.targetId}.`);
      if (intent.usesBonusActionMovement) {
        const speed = M().effectiveSpeed(member.state);
        E().spend(member.state, "bonus_action");
        member.state.movement_remaining_ft += speed;
        events.push({
          sequence: sequence++,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: member.state.template.name,
          feature_id: "aggressive",
          movement_ft: speed,
          animation: "advance",
          description: `${member.state.template.name} uses Aggressive to surge toward an enemy.`,
        });
      }
      const result = R().moveToward(
        sequence,
        round,
        member,
        target,
        setup,
        intent.desiredDistanceFt,
        "speed",
        { turnKey },
      );
      events.push(...result.events);
      return { events, sequence: result.sequence };
    } catch (error) {
      console.error("Failed browser movement-to-offense execution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT = { chooseIntent, move };
})();
