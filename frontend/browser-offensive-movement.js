(() => {
  "use strict";

  const T = () => window.IRON_PIT_BROWSER_TACTICAL_ACTIONS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const FR = () => window.IRON_PIT_BROWSER_FORMATION_ROWS;

  function isBackline(member) {
    try {
      if (typeof FR()?.isBackline === "function") return Boolean(FR().isBackline(member));
      if (typeof F()?.isBackline === "function") return Boolean(F().isBackline(member));
      if (typeof F()?.usesBackline === "function") return Boolean(F().usesBackline(member.state.template));
      return member.state.formation_row === "back";
    } catch (error) {
      console.error("Failed to read browser backline for movement", { id: member?.combatant_id, error });
      throw error;
    }
  }
  const G = () => window.IRON_PIT_BROWSER_GRID_MOVEMENT;
  const O = () => window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function chooseIntent(member, setup, turnKey) {
    try {
      if (!E().available(member.state, "action") || !setup.map_definition) return null;
      if (!member.state.position) throw new Error("Grid offensive movement requires an authoritative attacker position.");
      const members = [...setup.heroes, ...setup.monsters];
      const meleeReach = [], meleeProgress = [], rangedProgress = [];
      let meleeNow = false, otherNow = false;
      for (const target of F().targetOrder(member, setup)) {
        if (!target.state.position) throw new Error("Grid offensive movement requires authoritative target positions.");
        const distance = S().distance(member, target);
        for (const option of O().rangesForTarget(member, target, turnKey)) {
          if (distance <= option.range) {
            if (option.family === "melee") meleeNow = true;
            else otherNow = true;
            continue;
          }
          const plan = G().planToward(
            setup.map_definition,
            member,
            target,
            members,
            option.range,
            member.state.movement_remaining_ft,
            setup.persistent_barriers || [],
          );
          if (!plan.path.length) continue;
          const row = {
            cost: plan.movement_cost_ft,
            distance,
            targetId: target.combatant_id,
            family: option.family,
            range: option.range,
          };
          if (option.family === "melee" && plan.final_distance_ft <= option.range) meleeReach.push(row);
          else if (option.family === "melee" && plan.final_distance_ft < distance) meleeProgress.push(row);
          else if (plan.final_distance_ft < distance) rangedProgress.push(row);
        }
      }
      if (meleeNow) return null;
      const candidates = isBackline(member)
        ? (meleeReach.length ? meleeReach : (otherNow ? [] : rangedProgress.length ? rangedProgress : meleeProgress))
        : (meleeReach.length ? meleeReach : meleeProgress);
      if (!candidates.length) return null;
      candidates.sort((a, b) => a.cost - b.cost || a.distance - b.distance
        || a.targetId.localeCompare(b.targetId) || a.family.localeCompare(b.family) || b.range - a.range);
      const best = candidates[0];
      return { targetId: best.targetId, desiredDistanceFt: best.range, family: best.family };
    } catch (error) {
      console.error("Failed browser offensive movement intent", { member: member.combatant_id, error });
      throw error;
    }
  }

  function meleeCanBeEnabled(member, setup, turnKey) {
    try {
      if (F().meleeCanLandNow(member, setup)) return true;
      if (!setup.map_definition || !member.state.position) return false;
      const members = [...setup.heroes, ...setup.monsters];
      for (const target of F().targetOrder(member, setup)) {
        if (!target.state.position) throw new Error("Grid offensive movement requires authoritative target positions.");
        for (const option of O().rangesForTarget(member, target, turnKey)) {
          if (option.family !== "melee") continue;
          const plan = G().planToward(
            setup.map_definition, member, target, members, option.range,
            member.state.movement_remaining_ft, setup.persistent_barriers || [],
          );
          if (plan.goal_reachable && plan.path.length && plan.final_distance_ft <= option.range) return true;
        }
      }
      return false;
    } catch (error) {
      console.error("Failed browser melee-enable probe", { member: member.combatant_id, error });
      throw error;
    }
  }

  function move(sequence, round, member, setup, turnKey) {
    try {
      if (!setup.map_definition) return { events: [], sequence };
      const events = [];
      const dash = T()?.useOffensiveDash(sequence, round, member, setup, turnKey);
      if (dash) { events.push(dash); sequence += 1; }
      const intent = chooseIntent(member, setup, turnKey);
      if (!intent) return { events, sequence };
      const target = [...setup.heroes, ...setup.monsters]
        .find((candidate) => candidate.combatant_id === intent.targetId);
      if (!target) throw new Error(`Missing offensive movement target ${intent.targetId}.`);
      const result = R().moveToward(
        sequence, round, member, target, setup, intent.desiredDistanceFt, "speed", { turnKey },
      );
      events.push(...result.events);
      return { events, sequence: result.sequence };
    } catch (error) {
      console.error("Failed browser movement-to-offense execution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT = { chooseIntent, meleeCanBeEnabled, move };
})();