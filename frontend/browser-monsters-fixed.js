(() => {
  "use strict";

  const fixedAttack = (id, name, bonus, damageType, animation) => ({
    id, name, kind: "melee", bonus, diceCount: 0, diceSize: 2, damageBonus: 0,
    damageType, fixedDamage: 1, reach: 5, animation,
  });

  const monster = (id, name, size, ac, hp, speed, initiative, attack, page, extra = {}) => ({
    id, name, archetype: name, challenge_rating: "0", kind: "monster", size,
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks: [attack], primary_attack_id: attack.id, traits: [], resources: {},
    source: `SRD 5.2.1 ${name} p. ${page}`, ...extra,
  });

  const items = [
    monster("srd-awakened-shrub", "Awakened Shrub", "small", 9, 10, 20, -1,
      fixedAttack("awakened-shrub-rake", "Rake", 1, "slashing", "heavy-slash"), 260,
      { damage_resistances: ["piercing"], damage_vulnerabilities: ["fire"] }),
    monster("srd-badger", "Badger", "tiny", 11, 5, 20, 0,
      fixedAttack("badger-bite", "Bite", 2, "piercing", "bite"), 345,
      { damage_resistances: ["poison"] }),
    monster("srd-bat", "Bat", "tiny", 12, 1, 30, 2,
      fixedAttack("bat-bite", "Bite", 4, "piercing", "bite"), 345),
    monster("srd-cat", "Cat", "tiny", 12, 2, 40, 2,
      fixedAttack("cat-scratch", "Scratch", 4, "slashing", "slash"), 346),
    monster("srd-crab", "Crab", "tiny", 11, 3, 20, 0,
      fixedAttack("crab-claw", "Claw", 2, "bludgeoning", "heavy-strike"), 346),
    monster("srd-frog", "Frog", "tiny", 11, 1, 20, 1,
      fixedAttack("frog-bite", "Bite", 3, "piercing", "bite"), 348),
    monster("srd-hawk", "Hawk", "tiny", 13, 1, 60, 3,
      fixedAttack("hawk-talons", "Talons", 5, "slashing", "slash"), 355),
    monster("srd-lizard", "Lizard", "tiny", 10, 2, 20, 0,
      fixedAttack("lizard-bite", "Bite", 2, "piercing", "bite"), 357),
    monster("srd-owl", "Owl", "tiny", 11, 1, 60, 1,
      fixedAttack("owl-talons", "Talons", 3, "slashing", "slash"), 358),
    monster("srd-rat", "Rat", "tiny", 10, 1, 20, 0,
      fixedAttack("rat-bite", "Bite", 2, "piercing", "bite"), 359),
    monster("srd-raven", "Raven", "tiny", 12, 2, 50, 2,
      fixedAttack("raven-beak", "Beak", 4, "piercing", "bite"), 359),
    monster("srd-weasel", "Weasel", "tiny", 13, 1, 30, 3,
      fixedAttack("weasel-bite", "Bite", 5, "piercing", "bite"), 364),
  ];

  Object.assign(window.IRON_PIT_BROWSER_MONSTERS, Object.fromEntries(items.map((item) => [item.id, item])));
})();
