(() => {
  "use strict";

  try {
    const fighter = {
      id: "aldric-vane-l1",
      name: "Aldric Vane",
      archetype: "Fighter",
      level: 1,
      challenge_rating: null,
      armor_class: 18,
      max_hp: 12,
      speed_ft: 30,
      initiative_bonus: 1,
      weapon_attack: { weapon: { id: "longsword", name: "Longsword", mastery_property: "sap" } },
      alternate_weapon_attacks: [],
      weapon_masteries: ["longsword"],
      visual: { armor: "chain-mail", off_hand: "shield" },
    };

    const monster = {
      id: "srd-goblin-warrior",
      name: "Goblin Warrior",
      archetype: "Goblin Warrior",
      level: null,
      challenge_rating: "1/4",
      armor_class: 15,
      max_hp: 10,
      speed_ft: 30,
      initiative_bonus: 2,
      weapon_attack: { weapon: { id: "scimitar", name: "Scimitar", mastery_property: "nick" } },
      alternate_weapon_attacks: [{ weapon: { id: "shortbow", name: "Shortbow", mastery_property: "vex" } }],
      weapon_masteries: [],
      visual: { armor: "leather", off_hand: "shield" },
    };

    window.IRON_PIT_PREVIEW = { roster: { fighter, monster } };
  } catch (error) {
    console.error("Preview roster initialization failed", error);
    window.IRON_PIT_PREVIEW = null;
  }
})();
