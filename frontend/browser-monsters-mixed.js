(() => {
  "use strict";

  const bite = {
    id: "giant-constrictor-snake-bite", name: "Bite", kind: "melee", bonus: 6,
    diceCount: 2, diceSize: 6, damageBonus: 4, damageType: "piercing", reach: 10,
    animation: "bite",
  };
  const constrict = {
    id: "giant-constrictor-snake-constrict", name: "Constrict", saveAbility: "strength",
    dc: 14, range: 10, targetMaxSize: "large", damageDiceCount: 2, damageDiceSize: 8,
    damageBonus: 4, damageType: "bludgeoning", successDamage: "none",
    grappleEscapeDc: 14, animation: "constrict",
  };
  const monster = {
    id: "srd-giant-constrictor-snake", name: "Giant Constrictor Snake",
    archetype: "Giant Constrictor Snake", challenge_rating: "2", kind: "monster", size: "huge",
    armor_class: 12, max_hp: 60, speed_ft: 30, initiative_bonus: 2,
    attacks: [bite], primary_attack_id: bite.id,
    saving_throw_actions: [constrict],
    attack_action: {
      id: "giant-constrictor-snake-multiattack", name: "Multiattack",
      slots: [
        { attackIds: [bite.id], saveActionIds: [] },
        { attackIds: [], saveActionIds: [constrict.id] },
      ],
    },
    saving_throw_bonuses: {
      strength: 4, dexterity: 2, constitution: 1, intelligence: -5, wisdom: 0, charisma: -4,
    },
    skill_bonuses: { athletics: 4, acrobatics: 2, perception: 2 },
    traits: [], resources: {},
    source: "SRD 5.2.1 Giant Constrictor Snake p. 355",
  };

  window.IRON_PIT_BROWSER_MONSTERS[monster.id] = monster;
})();
