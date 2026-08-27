(() => {
  "use strict";

  const dice = window.IRON_PIT_DICE;
  const preview = window.IRON_PIT_PREVIEW;
  const weapons = {
    longsword: { name: "Longsword", attackBonus: 5, count: 1, size: 8, damageBonus: 3, animation: "melee" },
    scimitar: { name: "Scimitar", attackBonus: 4, count: 1, size: 6, damageBonus: 2, animation: "melee" },
    shortbow: { name: "Shortbow", attackBonus: 4, count: 1, size: 6, damageBonus: 2, animation: "projectile", projectile: "arrow" },
  };

  function d20(modifier, mode = "normal") {
    try {
      const rolls = mode === "normal" ? [dice.roll(20)] : dice.rollMany(2, 20);
      const selected = mode === "advantage" ? Math.max(...rolls) : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
      return { notation: "1d20", rolls, selected_roll: selected, modifier, total: selected + modifier, mode };
    } catch (error) { console.error("Preview d20 resolution failed", error); throw error; }
  }

  function damage(weapon, critical) {
    try {
      const count = weapon.count * (critical ? 2 : 1);
      const rolls = dice.rollMany(count, weapon.size);
      return { notation: `${count}d${weapon.size}+${weapon.damageBonus}`, rolls, modifier: weapon.damageBonus, total: rolls.reduce((a, b) => a + b, 0) + weapon.damageBonus };
    } catch (error) { console.error("Preview damage resolution failed", error); throw error; }
  }

  function attack(state, actor, target, weapon, mode = "normal") {
    try {
      const roll = d20(weapon.attackBonus, mode);
      const natural = roll.selected_roll;
      const critical = natural === 20;
      const hit = natural !== 1 && (critical || roll.total >= target.template.armor_class);
      const damageRoll = hit ? damage(weapon, critical) : null;
      if (hit) target.hp = Math.max(0, target.hp - damageRoll.total);
      const modeText = mode === "normal" ? "" : ` at ${mode[0].toUpperCase()}${mode.slice(1)}`;
      return {
        event_type: "attack", actor_id: actor.template.id, target_id: target.template.id,
        description: `${actor.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${weapon.name}${modeText}.`,
        attack_roll: roll, damage_roll: damageRoll, hit, critical, hp_after: target.hp,
        animation: weapon.animation, projectile: weapon.projectile || null,
      };
    } catch (error) { console.error("Preview attack failed", error); throw error; }
  }

  function secondWind(state, fighter, events) {
    try {
      if (fighter.hp > 0 && fighter.hp <= 6 && state.secondWindUses > 0) {
        const die = dice.roll(10);
        const total = die + 1;
        fighter.hp = Math.min(fighter.template.max_hp, fighter.hp + total);
        state.secondWindUses -= 1;
        events.push({
          event_type: "healing", actor_id: fighter.template.id,
          description: `${fighter.template.name} uses Second Wind and heals ${total} HP.`,
          healing_roll: { notation: "1d10+1", rolls: [die], modifier: 1, total }, hp_after: fighter.hp,
        });
      }
    } catch (error) { console.error("Preview Second Wind failed", error); throw error; }
  }

  function fighterTurn(state, fighter, goblin, events) {
    try {
      secondWind(state, fighter, events);
      if (state.distance > 5) {
        const move = Math.min(30, state.distance - 5);
        const before = state.distance;
        state.distance -= move;
        events.push({ event_type: "movement", actor_id: fighter.template.id, description: `${fighter.template.name} moves ${move} ft toward ${goblin.template.name}.`, movement_ft: move, distance_before_ft: before, distance_after_ft: state.distance });
        if (state.distance > 5) {
          events.push({ event_type: "dash", actor_id: fighter.template.id, description: `${fighter.template.name} uses Dash.` });
          const dashMove = Math.min(30, state.distance - 5);
          const dashBefore = state.distance;
          state.distance -= dashMove;
          events.push({ event_type: "movement", actor_id: fighter.template.id, description: `${fighter.template.name} moves another ${dashMove} ft.`, movement_ft: dashMove, distance_before_ft: dashBefore, distance_after_ft: state.distance });
          return;
        }
      }
      events.push(attack(state, fighter, goblin, weapons.longsword));
    } catch (error) { console.error("Preview Fighter turn failed", error); throw error; }
  }

  function goblinTurn(state, goblin, fighter, events) {
    try {
      if (state.distance <= 5) events.push(attack(state, goblin, fighter, weapons.scimitar));
      else events.push(attack(state, goblin, fighter, weapons.shortbow, state.distance > 80 ? "disadvantage" : "normal"));
    } catch (error) { console.error("Preview Goblin turn failed", error); throw error; }
  }

  function buildBattle(startingDistance) {
    try {
      if (!dice || !preview?.roster) throw new Error("Preview dependencies are unavailable.");
      const fighter = { template: preview.roster.fighter, hp: preview.roster.fighter.max_hp };
      const goblin = { template: preview.roster.monster, hp: preview.roster.monster.max_hp };
      const state = { distance: startingDistance, secondWindUses: 2 };
      const events = [];
      const fighterInit = d20(fighter.template.initiative_bonus);
      const goblinInit = d20(goblin.template.initiative_bonus);
      events.push({ event_type: "initiative", description: `${fighter.template.name} rolls initiative ${fighterInit.total}.` });
      events.push({ event_type: "initiative", description: `${goblin.template.name} rolls initiative ${goblinInit.total}.` });
      const order = fighterInit.total > goblinInit.total || (fighterInit.total === goblinInit.total && fighter.template.initiative_bonus >= goblin.template.initiative_bonus) ? ["fighter", "goblin"] : ["goblin", "fighter"];
      let resolvedRound = 0;
      for (let round = 1; round <= 50 && fighter.hp > 0 && goblin.hp > 0; round += 1) {
        resolvedRound = round;
        for (const actor of order) {
          if (fighter.hp <= 0 || goblin.hp <= 0) break;
          if (actor === "fighter") fighterTurn(state, fighter, goblin, events);
          else goblinTurn(state, goblin, fighter, events);
        }
      }
      const winner = fighter.hp > 0 ? fighter.template.name : goblin.hp > 0 ? goblin.template.name : null;
      events.push({ event_type: winner ? "victory" : "draw", description: winner ? `${winner} wins the duel.` : "The duel ends in a draw." });
      return { fighter: { template: fighter.template }, monster: { template: goblin.template }, battlefield: { starting_distance_ft: startingDistance }, events, winner_name: winner, rounds: resolvedRound };
    } catch (error) { console.error("Secure preview battle generation failed", error); throw error; }
  }

  preview.buildBattle = buildBattle;
})();
