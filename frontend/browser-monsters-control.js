(() => {
  "use strict";

  const attack = (id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType,
    reach: kind === "melee" ? 5 : 0,
    ...extra,
  });
  const monster = (id, name, cr, size, ac, hp, speed, initiative, attacks, saves, skills, extra = {}) => ({
    id, name, archetype: name, challenge_rating: cr, kind: "monster", size,
    armor_class: ac, max_hp: hp, speed_ft: speed, initiative_bonus: initiative,
    attacks, primary_attack_id: attacks[0].id, saving_throw_bonuses: saves,
    skill_bonuses: skills, traits: [], resources: {}, source: `SRD 5.2.1 ${name}`, ...extra,
  });

  const items = [
    monster("srd-crocodile", "Crocodile", "1/2", "large", 12, 13, 20, 0, [
      attack("crocodile-bite", "Bite", "melee", 4, 1, 8, 2, "piercing", {
        animation: "bite",
        controlEffect: { maxTargetSize: "medium", grappleEscapeDc: 12, restrainsWhileGrappled: true },
      }),
    ], { strength: 2, dexterity: 0, constitution: 3, intelligence: -4, wisdom: 0, charisma: -3 },
       { athletics: 2, acrobatics: 0 }),
    monster("srd-giant-crab", "Giant Crab", "1/8", "medium", 15, 13, 30, 1, [
      attack("giant-crab-claw", "Claw", "melee", 3, 1, 6, 1, "bludgeoning", {
        animation: "claw", controlEffect: { maxTargetSize: "medium", grappleEscapeDc: 11 },
      }),
    ], { strength: 1, dexterity: 1, constitution: 0, intelligence: -5, wisdom: -1, charisma: -4 },
       { athletics: 1, acrobatics: 1 }),
    monster("srd-constrictor-snake", "Constrictor Snake", "1/4", "large", 13, 13, 30, 2, [
      attack("constrictor-snake-bite", "Bite", "melee", 4, 1, 8, 2, "piercing", { animation: "bite" }),
    ], { strength: 2, dexterity: 2, constitution: 1, intelligence: -5, wisdom: 0, charisma: -4 },
       { athletics: 2, acrobatics: 2 }, {
         saving_throw_actions: [{
           id: "constrictor-snake-constrict", name: "Constrict", saveAbility: "strength", dc: 12, range: 5,
           targetMaxSize: "medium", damageDiceCount: 3, damageDiceSize: 4, damageBonus: 0,
           damageType: "bludgeoning", successDamage: "none", grappleEscapeDc: 12, animation: "constrict",
         }],
       }),
  ];

  Object.assign(window.IRON_PIT_BROWSER_MONSTERS, Object.fromEntries(items.map((item) => [item.id, item])));
})();
