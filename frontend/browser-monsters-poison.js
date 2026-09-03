(() => {
  "use strict";

  const bite = {
    id: "giant-centipede-bite", name: "Bite", kind: "melee", bonus: 4,
    diceCount: 1, diceSize: 4, damageBonus: 2, damageType: "piercing", reach: 5,
    animation: "bite", controlEffect: {
      conditionId: "poisoned",
      expiresAtStartOfSourceTurn: true,
      expiryTiming: "source_turn_start",
    },
  };
  const centipede = {
    id: "srd-giant-centipede", name: "Giant Centipede", archetype: "Giant Centipede",
    challenge_rating: "1/4", kind: "monster", size: "small", armor_class: 14,
    max_hp: 9, speed_ft: 30, initiative_bonus: 2, attacks: [bite],
    primary_attack_id: bite.id, traits: [], resources: {},
    saving_throw_bonuses: { strength: -3, dexterity: 2, constitution: 1, intelligence: -5, wisdom: -2, charisma: -4 },
    skill_bonuses: { athletics: -3, acrobatics: 2 },
    visual: { armor: "natural", main_hand: "bite", body_style: "giant-centipede" },
    source: "SRD 5.2.1 Giant Centipede p. 349",
  };

  window.IRON_PIT_BROWSER_MONSTERS[centipede.id] = centipede;
})();
