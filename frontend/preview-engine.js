(() => {
  "use strict";

  const dice = window.IRON_PIT_DICE;
  const effects = window.IRON_PIT_EFFECTS;
  const preview = window.IRON_PIT_PREVIEW;
  const weapons = {
    longsword: { id: "longsword", name: "Longsword", attackBonus: 5, count: 1, size: 8, damageBonus: 3, animation: "melee", masteryProperty: "sap" },
    handaxe: { id: "handaxe", name: "Handaxe", attackBonus: 5, count: 1, size: 6, damageBonus: 3, animation: "projectile", projectile: "axe", masteryProperty: "vex", normalRange: 20, longRange: 60 },
    scimitar: { id: "scimitar", name: "Scimitar", attackBonus: 4, count: 1, size: 6, damageBonus: 2, animation: "melee", masteryProperty: "nick" },
    shortbow: { id: "shortbow", name: "Shortbow", attackBonus: 4, count: 1, size: 6, damageBonus: 2, animation: "projectile", projectile: "arrow", masteryProperty: "vex", normalRange: 80, longRange: 320 },
  };

  function d20(modifier, mode = "normal") {
    try {
      const rolls = mode === "normal" ? [dice.roll(20)] : dice.rollMany(2, 20);
      const selected = mode === "advantage" ? Math.max(...rolls) : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
      return { notation: mode === "normal" ? "1d20" : "2d20", rolls, selected_roll: selected, modifier, total: selected + modifier, mode };
    } catch (error) { console.error("Preview d20 resolution failed", error); throw error; }
  }

  function damage(weapon, critical) {
    try {
      const count = weapon.count * (critical ? 2 : 1);
      const rolls = dice.rollMany(count, weapon.size);
      return { notation: `${count}d${weapon.size}+${weapon.damageBonus}`, rolls, modifier: weapon.damageBonus, total: rolls.reduce((a, b) => a + b, 0) + weapon.damageBonus };
    } catch (error) { console.error("Preview damage resolution failed", error); throw error; }
  }

  function pushStatus(events, actor, changes) {
    if (!changes?.length) return;
    events.push({ event_type: "status", actor_id: actor.template.id, description: "Combat-card effects update.", effect_changes: changes, log_visible: false, animation: "status" });
  }

  function attack(actor, target, weapon, baseMode = "normal") {
    try {
      const mode = effects.resolveRollMode(baseMode, actor.attackRollEffects, target.template.id);
      const roll = d20(weapon.attackBonus, mode);
      const effectChanges = effects.consumeAttackEffects(actor, target.template.id);
      const natural = roll.selected_roll;
      const critical = natural === 20;
      const hit = natural !== 1 && (critical || roll.total >= target.template.armor_class);
      const damageRoll = hit ? damage(weapon, critical) : null;
      if (hit) target.hp = Math.max(0, target.hp - damageRoll.total);
      const mastery = hit && target.hp > 0
        ? effects.applyWeaponMastery(actor, target, weapon, damageRoll.total)
        : { featureId: null, changes: [] };
      effectChanges.push(...mastery.changes);
      const modeText = mode === "normal" ? "" : ` at ${mode[0].toUpperCase()}${mode.slice(1)}`;
      const featureText = mastery.featureId === "sap" ? " Sap hinders the target's next attack roll." : mastery.featureId === "vex" ? " Vex grants Advantage on the next attack against this target." : "";
      return {
        event_type: "attack", actor_id: actor.template.id, target_id: target.template.id,
        description: `${actor.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${weapon.name}${modeText}.${featureText}`,
        attack_roll: roll, damage_roll: damageRoll, hit, critical, hp_after: target.hp,
        animation: weapon.animation, projectile: weapon.projectile || null,
        feature_id: mastery.featureId, weapon_id: weapon.id, effect_changes: effectChanges,
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
        events.push({ event_type: "healing", actor_id: fighter.template.id, description: `${fighter.template.name} uses Second Wind and heals ${total} HP.`, healing_roll: { notation: "1d10+1", rolls: [die], modifier: 1, total }, hp_after: fighter.hp });
      }
    } catch (error) { console.error("Preview Second Wind failed", error); throw error; }
  }

  function moveToward(state, actor, target, desired, events) {
    try {
      if (state.distance <= desired) return false;
      const moved = Math.min(actor.template.speed_ft, state.distance - desired);
      const before = state.distance;
      state.distance -= moved;
      events.push({ event_type: "movement", actor_id: actor.template.id, description: `${actor.template.name} moves ${moved} ft toward ${target.template.name}.`, movement_ft: moved, distance_before_ft: before, distance_after_ft: state.distance });
      return true;
    } catch (error) { console.error("Preview movement failed", error); throw error; }
  }

  function fighterTurn(state, fighter, goblin, events, mode) {
    try {
      pushStatus(events, fighter, effects.expireAtSourceTurn([fighter, goblin], fighter.template.id));
      secondWind(state, fighter, events);
      if (mode === "ranged" && state.distance > 5) {
        if (state.distance > weapons.handaxe.longRange) {
          moveToward(state, fighter, goblin, weapons.handaxe.normalRange, events);
          if (state.distance > weapons.handaxe.longRange) {
            events.push({ event_type: "dash", actor_id: fighter.template.id, description: `${fighter.template.name} uses Dash.` });
            moveToward(state, fighter, goblin, weapons.handaxe.normalRange, events);
            pushStatus(events, fighter, effects.endSourceTurn([fighter, goblin], fighter.template.id));
            return;
          }
        }
        const rangeMode = state.distance > weapons.handaxe.normalRange ? "disadvantage" : "normal";
        events.push(attack(fighter, goblin, weapons.handaxe, rangeMode));
      } else {
        moveToward(state, fighter, goblin, 5, events);
        events.push(attack(fighter, goblin, weapons.longsword));
      }
      pushStatus(events, fighter, effects.endSourceTurn([fighter, goblin], fighter.template.id));
    } catch (error) { console.error("Preview Fighter turn failed", error); throw error; }
  }

  function goblinTurn(state, goblin, fighter, events, mode) {
    try {
      pushStatus(events, goblin, effects.expireAtSourceTurn([fighter, goblin], goblin.template.id));
      if (mode === "ranged" && state.distance > 5) {
        const rangeMode = state.distance > weapons.shortbow.normalRange ? "disadvantage" : "normal";
        events.push(attack(goblin, fighter, weapons.shortbow, rangeMode));
      } else {
        moveToward(state, goblin, fighter, 5, events);
        events.push(attack(goblin, fighter, weapons.scimitar));
      }
      pushStatus(events, goblin, effects.endSourceTurn([fighter, goblin], goblin.template.id));
    } catch (error) { console.error("Preview Goblin turn failed", error); throw error; }
  }

  function buildBattle(startingDistance, mode = startingDistance <= 5 ? "melee" : "ranged") {
    try {
      if (!dice || !effects || !preview?.roster) throw new Error("Preview dependencies are unavailable.");
      const fighter = { template: preview.roster.fighter, hp: preview.roster.fighter.max_hp, attackRollEffects: [] };
      const goblin = { template: preview.roster.monster, hp: preview.roster.monster.max_hp, attackRollEffects: [] };
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
          if (actor === "fighter") fighterTurn(state, fighter, goblin, events, mode);
          else goblinTurn(state, goblin, fighter, events, mode);
        }
      }
      const winner = fighter.hp > 0 ? fighter.template.name : goblin.hp > 0 ? goblin.template.name : null;
      events.push({ event_type: winner ? "victory" : "draw", description: winner ? `${winner} wins the duel.` : "The duel ends in a draw." });
      return { fighter: { template: fighter.template }, monster: { template: goblin.template }, battlefield: { starting_distance_ft: startingDistance }, events, winner_name: winner, rounds: resolvedRound };
    } catch (error) { console.error("Secure preview battle generation failed", error); throw error; }
  }

  preview.buildBattle = buildBattle;
})();
