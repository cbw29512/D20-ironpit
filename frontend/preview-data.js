(() => {
  "use strict";

  try {
    const fighter = {
      id: "aldric-vane-l1",
      name: "Aldric Vane",
      archetype: "Fighter",
      level: 1,
      challenge_rating: null,
      max_hp: 12,
      weapon_attack: { weapon: { name: "Longsword" } },
      alternate_weapon_attacks: [],
      visual: { armor: "chain-mail", off_hand: "shield" },
    };

    const monster = {
      id: "srd-goblin-warrior",
      name: "Goblin Warrior",
      archetype: "Goblin Warrior",
      level: null,
      challenge_rating: "1/4",
      max_hp: 10,
      weapon_attack: { weapon: { name: "Scimitar" } },
      alternate_weapon_attacks: [{ weapon: { name: "Shortbow" } }],
      visual: { armor: "leather", off_hand: "shield" },
    };

    const attackRoll = (rolls, selected, modifier, mode = "normal") => ({
      notation: "1d20",
      rolls,
      selected_roll: selected,
      modifier,
      total: selected + modifier,
      mode,
    });

    const meleeEvents = [
      { event_type: "initiative", description: "Aldric Vane rolls initiative 15." },
      { event_type: "initiative", description: "Goblin Warrior rolls initiative 12." },
      {
        event_type: "attack", actor_id: fighter.id, target_id: monster.id,
        description: "Aldric Vane: HIT with Longsword.",
        attack_roll: attackRoll([14], 14, 5), damage_roll: { total: 7 },
        hit: true, critical: false, hp_after: 3, animation: "melee", projectile: null,
      },
      {
        event_type: "attack", actor_id: monster.id, target_id: fighter.id,
        description: "Goblin Warrior: HIT with Scimitar.",
        attack_roll: attackRoll([16], 16, 4), damage_roll: { total: 6 },
        hit: true, critical: false, hp_after: 6, animation: "melee", projectile: null,
      },
      {
        event_type: "healing", actor_id: fighter.id,
        description: "Aldric Vane uses Second Wind and heals 6 HP.",
        healing_roll: { total: 6 }, hp_after: 12,
      },
      {
        event_type: "attack", actor_id: fighter.id, target_id: monster.id,
        description: "Aldric Vane: CRITICAL HIT with Longsword.",
        attack_roll: attackRoll([20], 20, 5), damage_roll: { total: 14 },
        hit: true, critical: true, hp_after: 0, animation: "melee", projectile: null,
      },
      { event_type: "victory", description: "Aldric Vane wins the duel." },
    ];

    const rangedEvents = [
      { event_type: "initiative", description: "Goblin Warrior rolls initiative 18." },
      { event_type: "initiative", description: "Aldric Vane rolls initiative 13." },
      {
        event_type: "attack", actor_id: monster.id, target_id: fighter.id,
        description: "Goblin Warrior: HIT with Shortbow from 90 ft at Disadvantage.",
        attack_roll: attackRoll([18, 17], 17, 4, "disadvantage"), damage_roll: { total: 5 },
        hit: true, critical: false, hp_after: 7, animation: "projectile", projectile: "arrow",
      },
      {
        event_type: "movement", actor_id: fighter.id,
        description: "Aldric Vane moves 30 ft toward Goblin Warrior.",
        movement_ft: 30, distance_before_ft: 90, distance_after_ft: 60,
      },
      { event_type: "dash", actor_id: fighter.id, description: "Aldric Vane uses Dash." },
      {
        event_type: "movement", actor_id: fighter.id,
        description: "Aldric Vane moves another 30 ft.",
        movement_ft: 30, distance_before_ft: 60, distance_after_ft: 30,
      },
      {
        event_type: "attack", actor_id: monster.id, target_id: fighter.id,
        description: "Goblin Warrior: CRITICAL HIT with Shortbow.",
        attack_roll: attackRoll([20], 20, 4), damage_roll: { total: 8 },
        hit: true, critical: true, hp_after: 0, animation: "projectile", projectile: "arrow",
      },
      { event_type: "victory", description: "Goblin Warrior wins the ranged demonstration." },
    ];

    const battle = (events, distance, winner, rounds) => ({
      fighter: { template: fighter },
      monster: { template: monster },
      battlefield: { starting_distance_ft: distance },
      events,
      winner_name: winner,
      rounds,
    });

    window.IRON_PIT_PREVIEW = {
      roster: { fighter, monster },
      melee: battle(meleeEvents, 5, fighter.name, 2),
      ranged: battle(rangedEvents, 90, monster.name, 2),
    };
  } catch (error) {
    console.error("Preview battle data initialization failed", error);
    window.IRON_PIT_PREVIEW = null;
  }
})();
