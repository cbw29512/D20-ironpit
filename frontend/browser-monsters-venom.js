(() => {
  "use strict";

  const venomAttack = (id, name, bonus, diceCount, diceSize, damageBonus, poisonCount, poisonSize, extra = {}) => ({
    id, name, kind: "melee", bonus, diceCount, diceSize, damageBonus, damageType: "piercing",
    reach: extra.reach || 5, animation: name === "Sting" ? "sting" : "bite",
    onHitDamage: [{ source: "Venom", diceCount: poisonCount, diceSize: poisonSize, damageBonus: 0, damageType: "poison" }],
  });
  const monster = (id, name, cr, ac, hp, speed, initiative, attacks, saves, skills, bodyStyle) => ({
    id, name, archetype: name, challenge_rating: cr, kind: "monster", size: "medium",
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks, primary_attack_id: attacks[0].id, traits: [], resources: {},
    saving_throw_bonuses: saves, skill_bonuses: skills,
    visual: { armor: "natural", main_hand: attacks[0].name.toLowerCase(), body_style: bodyStyle },
    source: `SRD 5.2.1 ${name}`,
  });

  const items = [
    monster("srd-giant-venomous-snake", "Giant Venomous Snake", "1/4", 14, 11, 40, 4, [
      venomAttack("giant-venomous-snake-bite", "Bite", 6, 1, 4, 4, 1, 8, { reach: 10 }),
    ], { strength: 0, dexterity: 4, constitution: 1, intelligence: -4, wisdom: 0, charisma: -4 },
      { athletics: 0, acrobatics: 4, perception: 2 }, "giant-venomous-snake"),
    monster("srd-giant-wasp", "Giant Wasp", "1/2", 13, 22, 50, 2, [
      venomAttack("giant-wasp-sting", "Sting", 4, 1, 6, 2, 2, 4),
    ], { strength: 0, dexterity: 2, constitution: 0, intelligence: -5, wisdom: 0, charisma: -4 },
      { athletics: 0, acrobatics: 2 }, "giant-wasp"),
    monster("srd-giant-wolf-spider", "Giant Wolf Spider", "1/4", 13, 11, 40, 3, [
      venomAttack("giant-wolf-spider-bite", "Bite", 5, 1, 4, 3, 2, 4),
    ], { strength: 1, dexterity: 3, constitution: 1, intelligence: -4, wisdom: 1, charisma: -3 },
      { athletics: 1, acrobatics: 3, perception: 3, stealth: 7 }, "giant-wolf-spider"),
  ];

  Object.assign(window.IRON_PIT_BROWSER_MONSTERS, Object.fromEntries(items.map((item) => [item.id, item])));
})();
