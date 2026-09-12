(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function triggered(events, member) {
    const meleeIds = new Set((member.state.template.attacks || []).filter((attack) => attack.kind === "melee").map((attack) => attack.id));
    return events.some((event) => event.event_type === "attack" && event.actor_id === member.combatant_id
      && meleeIds.has(event.weapon_id) && (event.hp_before || 0) > 0 && (event.hp_after || 0) <= 0);
  }

  function resolve(sequence, round, member, setup, priorEvents, turnKey) {
    try {
      if (!member.state.template.traits?.includes("rampage") || !E().available(member.state, "bonus_action") || !triggered(priorEvents, member)) {
        return { events: [], sequence };
      }
      const bite = (member.state.template.attacks || []).find((attack) => attack.id === "bite");
      if (!bite) throw new Error("Rampage requires a compiled Bite attack.");
      let choice = F().chooseAttack(member, setup, [bite.id], "melee");
      const events = [];
      if (!choice) {
        const targets = F().targetOrder(member, setup);
        if (!targets.length) return { events, sequence };
        const target = targets.reduce((best, item) => S().distance(member, item) < S().distance(member, best) ? item : best);
        const originalMovement = member.state.movement_remaining_ft;
        member.state.movement_remaining_ft = Math.floor(member.state.template.speed_ft / 2);
        const moved = R().moveToward(sequence, round, member, target, setup, bite.reach || 5, "speed", { turnKey });
        events.push(...moved.events); sequence = moved.sequence;
        member.state.movement_remaining_ft = originalMovement;
        if (member.state.is_dead || member.state.is_unconscious) return { events, sequence };
        choice = F().chooseAttack(member, setup, [bite.id], "melee");
      }
      if (!choice) return { events, sequence };
      E().spend(member.state, "bonus_action");
      events.push(A().resolveAttack(sequence, round, member, choice.target, choice.attack, choice.distance, {
        spendAction: false, setup, turnKey, featureId: "rampage",
      }));
      return { events, sequence: sequence + 1 };
    } catch (error) {
      console.error("Failed browser Rampage resolution", { member: member.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_RAMPAGE = { resolve, triggered };
})();
