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
  ];

  window.IRON_PIT_BROWSER_MONSTERS = Object.fromEntries(monsters.map((item) => [item.id, item]));
})();
