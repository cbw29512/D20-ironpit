(() => {
  "use strict";

  const attack = (id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType,
    reach: kind === "melee" ? 5 : 0,
    ...extra,
  });

  const monster = (id, name, cr, size, ac, hp, speed, initiative, attacks, extra = {}) => ({
    id, name, archetype: name, challenge_rating: cr, kind: "monster", size,
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks, primary_attack_id: attacks[0].id, traits: [], resources: {}, source: `SRD 5.2.1 ${name}`,
    ...extra,
  });

  const charge = (minimumMove, diceCount, diceSize, damageType, proneMaxSize) => ({
    minimumMove, diceCount, diceSize, damageType, proneMaxSize,
  });

  const monsters = [
    monster("srd-goblin-warrior", "Goblin Warrior", "1/4", "small", 15, 10, 30, 2, [
      attack("goblin-scimitar", "Scimitar", "melee", 4, 1, 6, 2, "slashing", { conditionalAdvantage: [1, 4] }),
      attack("goblin-shortbow", "Shortbow", "ranged", 4, 1, 6, 2, "piercing", {
        normal: 80, long: 320, projectile: "arrow", animation: "projectile", conditionalAdvantage: [1, 4],
      }),
    ]),
    monster("srd-bandit", "Bandit", "1/8", "medium", 12, 11, 30, 1, [
      attack("bandit-scimitar", "Scimitar", "melee", 3, 1, 6, 1, "slashing"),
      attack("bandit-light-crossbow", "Light Crossbow", "ranged", 3, 1, 8, 1, "piercing", {
        normal: 80, long: 320, projectile: "bolt", animation: "projectile",
      }),
    ]),
    monster("srd-commoner", "Commoner", "0", "medium", 10, 4, 30, 0, [
      attack("commoner-club", "Club", "melee", 2, 1, 4, 0, "bludgeoning"),
    ]),
    monster("srd-guard", "Guard", "1/8", "medium", 16, 11, 30, 1, [
      attack("guard-spear-melee", "Spear", "melee", 3, 1, 6, 1, "piercing"),
      attack("guard-spear-thrown", "Spear", "ranged", 3, 1, 6, 1, "piercing", {
        normal: 20, long: 60, projectile: "spear", animation: "projectile",
      }),
    ]),
    monster("srd-giant-rat", "Giant Rat", "1/8", "small", 13, 7, 30, 3, [
      attack("giant-rat-bite", "Bite", "melee", 5, 1, 4, 3, "piercing", { animation: "bite" }),
    ], { traits: ["pack-tactics"] }),
    monster("srd-giant-weasel", "Giant Weasel", "1/8", "medium", 13, 9, 40, 3, [
      attack("giant-weasel-bite", "Bite", "melee", 5, 1, 4, 3, "piercing", { animation: "bite" }),
    ]),
    monster("srd-axe-beak", "Axe Beak", "1/4", "large", 11, 19, 50, 1, [
      attack("axe-beak-beak", "Beak", "melee", 4, 1, 6, 2, "slashing", { animation: "bite" }),
    ]),
    monster("srd-giant-lizard", "Giant Lizard", "1/4", "large", 12, 19, 40, 1, [
      attack("giant-lizard-bite", "Bite", "melee", 4, 1, 8, 2, "piercing", { animation: "bite" }),
    ]),
    monster("srd-wolf", "Wolf", "1/4", "medium", 12, 11, 40, 2, [
      attack("wolf-bite", "Bite", "melee", 4, 1, 6, 2, "piercing", { animation: "bite", proneMaxSize: "medium" }),
    ], { traits: ["pack-tactics"] }),
    monster("srd-dire-wolf", "Dire Wolf", "1", "large", 14, 22, 50, 2, [
      attack("dire-wolf-bite", "Bite", "melee", 5, 1, 10, 3, "piercing", { animation: "bite", proneMaxSize: "large" }),
    ], { traits: ["pack-tactics"] }),
    monster("srd-black-bear", "Black Bear", "1/2", "medium", 11, 19, 30, 1, [
      attack("black-bear-rend", "Rend", "melee", 4, 1, 6, 2, "slashing", { animation: "heavy-slash" }),
    ], { attack_action: { id: "black-bear-multiattack", slots: [["black-bear-rend"], ["black-bear-rend"]] } }),
    monster("srd-brown-bear", "Brown Bear", "1", "large", 11, 22, 40, 1, [
      attack("brown-bear-bite", "Bite", "melee", 5, 1, 8, 3, "piercing", { animation: "bite" }),
      attack("brown-bear-claw", "Claw", "melee", 5, 1, 4, 3, "slashing", { animation: "heavy-slash", proneMaxSize: "large" }),
    ], { attack_action: { id: "brown-bear-multiattack", slots: [["brown-bear-bite"], ["brown-bear-claw"]] } }),
    monster("srd-baboon", "Baboon", "0", "small", 12, 3, 30, 2, [
      attack("baboon-bite", "Bite", "melee", 1, 1, 4, -1, "piercing", { animation: "bite" }),
    ], { traits: ["pack-tactics"] }),
    monster("srd-camel", "Camel", "1/8", "large", 10, 17, 50, -1, [
      attack("camel-bite", "Bite", "melee", 4, 1, 4, 2, "bludgeoning", { animation: "bite" }),
    ]),
    monster("srd-deer", "Deer", "0", "medium", 13, 4, 50, 3, [
      attack("deer-ram", "Ram", "melee", 2, 1, 4, 0, "bludgeoning", { animation: "heavy-strike" }),
    ]),
    monster("srd-draft-horse", "Draft Horse", "1/4", "large", 10, 15, 40, 0, [
      attack("draft-horse-hooves", "Hooves", "melee", 6, 1, 4, 4, "bludgeoning", { animation: "heavy-strike" }),
    ]),
    monster("srd-giant-badger", "Giant Badger", "1/4", "medium", 13, 15, 30, 0, [
      attack("giant-badger-bite", "Bite", "melee", 3, 2, 4, 1, "piercing", { animation: "bite" }),
    ], { damage_resistances: ["poison"] }),
    monster("srd-boar", "Boar", "1/4", "medium", 11, 13, 40, 0, [
      attack("boar-gore", "Gore", "melee", 3, 1, 6, 1, "piercing", {
        animation: "heavy-strike", charge: charge(20, 1, 6, "piercing", "medium"),
      }),
    ], { traits: ["charge", "bloodied-fury"] }),
    monster("srd-elk", "Elk", "1/4", "large", 10, 11, 50, 0, [
      attack("elk-ram", "Ram", "melee", 5, 1, 6, 3, "bludgeoning", {
        animation: "heavy-strike", charge: charge(20, 1, 6, "bludgeoning", "large"),
      }),
    ], { traits: ["charge"] }),
    monster("srd-giant-boar", "Giant Boar", "2", "large", 13, 42, 40, 0, [
      attack("giant-boar-gore", "Gore", "melee", 5, 2, 6, 3, "piercing", {
        animation: "heavy-strike", charge: charge(20, 2, 6, "piercing", "large"),
      }),
    ], { traits: ["charge", "bloodied-fury"] }),
  ];

  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));
})();
