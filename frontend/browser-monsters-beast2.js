(() => {
  "use strict";

  const attack = (id, name, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind: "melee", bonus, diceCount, diceSize, damageBonus, damageType,
    reach: 5, animation: name === "Bite" ? "bite" : "heavy-strike", ...extra,
  });

  const monster = (id, name, cr, size, ac, hp, speed, initiative, attacks, extra = {}) => ({
    id, name, archetype: name, challenge_rating: cr, kind: "monster", size,
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks, primary_attack_id: attacks[0].id, traits: [], resources: {},
    source: `SRD 5.2.1 ${name}`, ...extra,
  });

  const charge = (minimumMove, diceCount, diceSize, damageType, proneMaxSize) => ({
    minimumMove, diceCount, diceSize, damageType, proneMaxSize,
  });

  const items = [
    monster("srd-eagle", "Eagle", "0", "small", 12, 4, 60, 2, [
      attack("eagle-talons", "Talons", 4, 1, 4, 2, "slashing"),
    ]),
    monster("srd-panther", "Panther", "1/4", "medium", 13, 13, 50, 3, [
      attack("panther-rend", "Rend", 5, 1, 6, 3, "slashing"),
    ]),
    monster("srd-plesiosaurus", "Plesiosaurus", "2", "large", 13, 68, 20, 2, [
      attack("plesiosaurus-bite", "Bite", 6, 2, 6, 4, "piercing", { reach: 10 }),
    ]),
    monster("srd-polar-bear", "Polar Bear", "2", "large", 12, 42, 40, 2, [
      attack("polar-bear-rend", "Rend", 7, 1, 8, 5, "slashing"),
    ], { damage_resistances: ["cold"], attack_action: { id: "srd-polar-bear-multiattack", slots: [["polar-bear-rend"], ["polar-bear-rend"]] } }),
    monster("srd-pony", "Pony", "1/8", "medium", 10, 11, 40, 0, [
      attack("pony-hooves", "Hooves", 4, 1, 4, 2, "bludgeoning"),
    ]),
    monster("srd-pteranodon", "Pteranodon", "1/4", "medium", 13, 13, 60, 2, [
      attack("pteranodon-bite", "Bite", 4, 1, 8, 2, "piercing"),
    ]),
    monster("srd-riding-horse", "Riding Horse", "1/4", "large", 11, 13, 60, 1, [
      attack("riding-horse-hooves", "Hooves", 5, 1, 8, 3, "bludgeoning"),
    ]),
    monster("srd-tiger", "Tiger", "1", "large", 13, 30, 40, 3, [
      attack("tiger-rend", "Rend", 5, 2, 6, 3, "slashing", { proneMaxSize: "large" }),
    ]),
    monster("srd-vulture", "Vulture", "0", "medium", 10, 5, 50, 0, [
      attack("vulture-beak", "Beak", 2, 1, 4, 0, "piercing"),
    ], { traits: ["pack-tactics"] }),
    monster("srd-giant-fire-beetle", "Giant Fire Beetle", "0", "small", 13, 4, 30, 0, [
      attack("giant-fire-beetle-bite", "Bite", 1, 0, 2, 0, "fire", { fixedDamage: 1 }),
    ], { damage_resistances: ["fire"] }),
    monster("srd-giant-goat", "Giant Goat", "1/2", "large", 11, 19, 40, 1, [
      attack("giant-goat-ram", "Ram", 5, 1, 6, 3, "bludgeoning", {
        charge: charge(20, 2, 4, "bludgeoning", "large"),
      }),
    ], { traits: ["charge"] }),
    monster("srd-giant-owl", "Giant Owl", "1/4", "large", 12, 19, 60, 2, [
      attack("giant-owl-talons", "Talons", 4, 1, 10, 2, "slashing"),
    ], { damage_resistances: ["necrotic", "radiant"] }),
    monster("srd-hyena", "Hyena", "0", "medium", 11, 5, 50, 1, [
      attack("hyena-bite", "Bite", 2, 1, 6, 0, "piercing"),
    ], { traits: ["pack-tactics"] }),
  ];

  Object.assign(window.IRON_PIT_BROWSER_MONSTERS, Object.fromEntries(items.map((item) => [item.id, item])));
})();
