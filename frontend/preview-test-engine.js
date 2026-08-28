(() => {
  "use strict";

  const dice = window.IRON_PIT_DICE;
  const effects = window.IRON_PIT_EFFECTS;
  const catalog = window.IRON_PIT_TEST_ROSTER;

  function d20(modifier, mode = "normal") {
    const rolls = mode === "normal" ? [dice.roll(20)] : dice.rollMany(2, 20);
    const selected = mode === "advantage" ? Math.max(...rolls) : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
    return { notation: rolls.length === 2 ? "2d20" : "1d20", rolls, selected_roll: selected, modifier, total: selected + modifier, mode };
  }

  function damage(actor, weapon, critical, mode, sneakAttack) {
    const components = [];
    const weaponRolls = dice.rollMany(weapon.count * (critical ? 2 : 1), weapon.size);
    components.push({ source: weapon.name, rolls: weaponRolls, total: weaponRolls.reduce((a, b) => a + b, 0) + weapon.damageBonus });
    if (sneakAttack) {
      const sneakRolls = dice.rollMany(actor.template.sneakAttackDice * (critical ? 2 : 1), 6);
      components.push({ source: "Sneak Attack", rolls: sneakRolls, total: sneakRolls.reduce((a, b) => a + b, 0) });
    }
    if (mode === "advantage" && weapon.conditionalAdvantageDie) {
      const extra = dice.rollMany(critical ? 2 : 1, weapon.conditionalAdvantageDie);
      components.push({ source: "Advantage damage", rolls: extra, total: extra.reduce((a, b) => a + b, 0) });
    }
    const rolls = components.flatMap((component) => component.rolls);
    return {
      notation: components.map((component) => component.source).join(" + "), rolls,
      modifier: weapon.damageBonus, total: components.reduce((sum, component) => sum + component.total, 0), components,
    };
  }

  function attack(actor, target, profile, baseMode = "normal") {
    const weapon = profile.weapon;
    const mode = effects.resolveRollMode(baseMode, actor.attackRollEffects, target.template.id);
    const roll = d20(actor.template.attackBonus, mode);
    const effectChanges = effects.consumeAttackEffects(actor, target.template.id);
    const natural = roll.selected_roll;
    const critical = natural === 20;
    const hit = natural !== 1 && (critical || roll.total >= target.template.armor_class);
    const sneakAttack = Boolean(hit && actor.template.sneakAttackDice && mode === "advantage" && !actor.sneakUsed);
    if (sneakAttack) actor.sneakUsed = true;
    const damageRoll = hit ? damage(actor, weapon, critical, mode, sneakAttack) : null;
    if (damageRoll) target.hp = Math.max(0, target.hp - damageRoll.total);
    const mastery = hit && target.hp > 0
      ? effects.applyWeaponMastery(actor, target, weapon, damageRoll.total)
      : { featureId: null, changes: [] };
    effectChanges.push(...mastery.changes);
    const modeText = mode === "normal" ? "" : ` at ${mode[0].toUpperCase()}${mode.slice(1)}`;
    const featureText = mastery.featureId === "sap" ? " Sap hinders the next attack." : mastery.featureId === "vex" ? " Vex marks the target." : "";
    return {
      event_type: "attack", actor_id: actor.template.id, target_id: target.template.id,
      description: `${actor.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${weapon.name}${modeText}.${sneakAttack ? " Sneak Attack adds precision damage." : ""}${featureText}`,
      attack_roll: roll, damage_roll: damageRoll, damage_components: damageRoll?.components || [],
      hit, critical, hp_after: target.hp, animation: weapon.kind === "ranged" ? "projectile" : "slash",
      projectile: weapon.projectile, weapon_id: weapon.id, feature_id: mastery.featureId,
      effect_changes: effectChanges,
    };
  }

  function statusEvent(changes) {
    return changes.length ? { event_type: "status", actor_id: "arena", description: "Combat effects update.", log_visible: false, effect_changes: changes } : null;
  }

  function chooseAttack(template, mode, distance) {
    const melee = template.attacks.find((profile) => profile.weapon.kind === "melee");
    const ranged = template.attacks.find((profile) => profile.weapon.kind === "ranged");
    if (distance <= 5 || mode === "melee") return melee || ranged || null;
    return ranged || null;
  }

  function moveToward(state, actor, target, events) {
    if (state.distance <= 5) return;
    const moved = Math.min(actor.template.speed_ft, state.distance - 5);
    const before = state.distance;
    state.distance -= moved;
    events.push({ event_type: "movement", actor_id: actor.template.id, description: `${actor.template.name} moves ${moved} ft toward ${target.template.name}.`, movement_ft: moved, distance_before_ft: before, distance_after_ft: state.distance, animation: "advance" });
  }

  function secondWind(state, actor, events) {
    if (!actor.template.features.includes("second-wind") || actor.hp > actor.template.max_hp / 2 || state.secondWindUses <= 0) return;
    const roll = dice.roll(10);
    const total = roll + 1;
    actor.hp = Math.min(actor.template.max_hp, actor.hp + total);
    state.secondWindUses -= 1;
    events.push({ event_type: "healing", actor_id: actor.template.id, description: `${actor.template.name} uses Second Wind and heals ${total} HP.`, healing_roll: { notation: "1d10+1", rolls: [roll], modifier: 1, total }, hp_after: actor.hp });
  }

  function takeTurn(state, actor, target, events, mode) {
    actor.sneakUsed = false;
    const start = statusEvent(effects.expireAtSourceTurn([actor, target], actor.template.id));
    if (start) events.push(start);
    secondWind(state, actor, events);
    let profile = chooseAttack(actor.template, mode, state.distance);
    if (!profile) {
      moveToward(state, actor, target, events);
      if (state.distance > 5) {
        events.push({ event_type: "dash", actor_id: actor.template.id, description: `${actor.template.name} uses Dash.` });
        moveToward(state, actor, target, events);
      }
      profile = chooseAttack(actor.template, "melee", state.distance);
    }
    if (profile) events.push(attack(actor, target, profile));
    const end = statusEvent(effects.endSourceTurn([actor, target], actor.template.id));
    if (end) events.push(end);
  }

  function buildTestBattle(characterId, monsterId, mode = "melee") {
    if (!catalog?.characters?.[characterId] || !catalog?.monsters?.[monsterId]) throw new Error("Selected test combatant is unavailable.");
    const character = { template: catalog.characters[characterId], hp: catalog.characters[characterId].max_hp, attackRollEffects: [], sneakUsed: false };
    const monster = { template: catalog.monsters[monsterId], hp: catalog.monsters[monsterId].max_hp, attackRollEffects: [], sneakUsed: false };
    const state = { distance: mode === "melee" ? 5 : 20, secondWindUses: 2 };
    const events = [];
    const characterInit = d20(character.template.initiative_bonus);
    const monsterInit = d20(monster.template.initiative_bonus);
    events.push({ event_type: "initiative", actor_id: character.template.id, description: `${character.template.name} rolls initiative ${characterInit.total}.`, attack_roll: characterInit });
    events.push({ event_type: "initiative", actor_id: monster.template.id, description: `${monster.template.name} rolls initiative ${monsterInit.total}.`, attack_roll: monsterInit });
    const order = characterInit.total >= monsterInit.total ? [character, monster] : [monster, character];
    let rounds = 0;
    for (let round = 1; round <= 50 && character.hp > 0 && monster.hp > 0; round += 1) {
      rounds = round;
      for (const actor of order) {
        if (character.hp <= 0 || monster.hp <= 0) break;
        takeTurn(state, actor, actor === character ? monster : character, events, mode);
      }
    }
    const winner = character.hp > 0 ? character.template.name : monster.hp > 0 ? monster.template.name : null;
    events.push({ event_type: winner ? "victory" : "draw", actor_id: winner ? (winner === character.template.name ? character.template.id : monster.template.id) : "arena", description: winner ? `${winner} wins the duel.` : "The duel ends in a draw.", animation: winner ? "victory" : "draw" });
    return { fighter: { template: character.template }, monster: { template: monster.template }, battlefield: { starting_distance_ft: mode === "melee" ? 5 : 20 }, events, winner_name: winner, rounds };
  }

  window.IRON_PIT_TEST_ENGINE = { buildTestBattle };
})();
