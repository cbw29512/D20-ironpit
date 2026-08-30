(() => {
  "use strict";

  const attack = (id, name, kind, bonus, count, size, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount: count, diceSize: size, damageBonus, damageType,
    animation: kind === "ranged" ? "projectile" : "slash", ...extra,
  });
  const monster = (id, name, cr, size, ac, hp, speed, initiative, attacks, extra = {}) => ({
    id, name, archetype: name, challenge_rating: cr, kind: "monster", size,
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks, primary_attack_id: attacks[0].id, traits: [], resources: {}, ...extra,
  });
  const daggerPair = (prefix) => [
    attack(`${prefix}-dagger-melee`, "Dagger", "melee", 4, 1, 4, 2, "piercing", { reach: 5 }),
    attack(`${prefix}-dagger-ranged`, "Dagger", "ranged", 4, 1, 4, 2, "piercing", {
      normal: 20, long: 60, projectile: "dagger",
    }),
  ];

  const goblin = monster("srd-goblin-minion", "Goblin Minion", "1/8", "small", 12, 7, 30, 2,
    daggerPair("goblin-minion"), {
      visual: { armor: "clothes", main_hand: "dagger", body_style: "goblinoid" },
      source: "SRD 5.2.1 Goblin Minion p. 290",
    });

  const kobold = monster("srd-kobold-warrior", "Kobold Warrior", "1/8", "small", 14, 7, 30, 2,
    daggerPair("kobold-warrior"), {
      traits: ["pack-tactics"],
      visual: { armor: "natural", main_hand: "dagger", body_style: "kobold" },
      source: "SRD 5.2.1 Kobold Warrior p. 302",
    });

  const hobLongsword = attack("hobgoblin-longsword", "Longsword", "melee", 3, 2, 10, 1, "slashing", { reach: 5 });
  const hobLongbow = attack("hobgoblin-longbow", "Longbow", "ranged", 3, 1, 8, 1, "piercing", {
    normal: 150, long: 600, projectile: "arrow",
    onHitDamage: [{ source: "Poison", diceCount: 3, diceSize: 4, damageBonus: 0, damageType: "poison" }],
  });
  const hobgoblin = monster("srd-hobgoblin-warrior", "Hobgoblin Warrior", "1/2", "medium", 18, 11, 30, 3,
    [hobLongsword, hobLongbow], {
      traits: ["pack-tactics"],
      visual: { armor: "half-plate", main_hand: "longsword", off_hand: "shield", body_style: "humanoid" },
      source: "SRD 5.2.1 Hobgoblin Warrior p. 298",
    });

  const rend = attack("hippogriff-rend", "Rend", "melee", 5, 1, 8, 3, "slashing", { reach: 5, animation: "claw" });
  const hippogriff = monster("srd-hippogriff", "Hippogriff", "1", "large", 11, 26, 60, 1, [rend], {
    attack_action: { id: "hippogriff-multiattack", name: "Multiattack", slots: [[rend.id], [rend.id]] },
    visual: { armor: "feathers", main_hand: "claws", body_style: "hippogriff" },
    source: "SRD 5.2.1 Hippogriff p. 298",
  });

  for (const item of [goblin, kobold, hobgoblin, hippogriff]) {
    window.IRON_PIT_BROWSER_MONSTERS[item.id] = item;
  }
})();
