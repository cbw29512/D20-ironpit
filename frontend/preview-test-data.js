(() => {
  "use strict";

  function attack(id, weapon) { return { id, weapon }; }
  function weapon(id, name, kind, count, size, bonus, options = {}) {
    return {
      id, name, kind, count, size, damageBonus: bonus,
      normalRange: options.normalRange ?? null,
      longRange: options.longRange ?? null,
      projectile: options.projectile ?? null,
      masteryProperty: options.masteryProperty ?? null,
      conditionalAdvantageDie: options.conditionalAdvantageDie ?? null,
    };
  }

  const characters = {
    "aldric-vane-l1": {
      id: "aldric-vane-l1", name: "Aldric Vane", archetype: "Fighter", level: 1,
      challenge_rating: null, armor_class: 19, max_hp: 12, speed_ft: 30, initiative_bonus: 1,
      attacks: [
        attack("aldric-longsword", weapon("longsword", "Longsword", "melee", 1, 8, 3, { masteryProperty: "sap" })),
        attack("aldric-handaxe-throw", weapon("handaxe", "Handaxe", "ranged", 1, 6, 3, { normalRange: 20, longRange: 60, projectile: "axe", masteryProperty: "vex" })),
      ],
      attackBonus: 5, weapon_masteries: ["longsword", "javelin", "handaxe"],
      features: ["second-wind"], visual: { armor: "chain-mail", off_hand: "shield", body_style: "fighter" },
    },
    "mara-vale-l1": {
      id: "mara-vale-l1", name: "Mara Vale", archetype: "Rogue", level: 1,
      challenge_rating: null, armor_class: 14, max_hp: 10, speed_ft: 30, initiative_bonus: 3,
      attacks: [
        attack("mara-shortsword", weapon("shortsword", "Shortsword", "melee", 1, 6, 3, { masteryProperty: "vex" })),
        attack("mara-shortbow", weapon("shortbow", "Shortbow", "ranged", 1, 6, 3, { normalRange: 80, longRange: 320, projectile: "arrow", masteryProperty: "vex" })),
      ],
      attackBonus: 5, weapon_masteries: ["shortsword", "shortbow"], sneakAttackDice: 1,
      skill_bonuses: { stealth: 7, perception: 2 }, passive_perception: 12,
      features: ["sneak-attack"], visual: { armor: "leather", off_hand: null, body_style: "rogue" },
    },
  };

  const monsters = {
    "srd-bandit": {
      id: "srd-bandit", name: "Bandit", archetype: "Bandit", level: null,
      challenge_rating: "1/8", armor_class: 12, max_hp: 11, speed_ft: 30, initiative_bonus: 1,
      openingDistance: 20,
      attacks: [
        attack("bandit-scimitar", weapon("scimitar", "Scimitar", "melee", 1, 6, 1)),
        attack("bandit-light-crossbow", weapon("light-crossbow", "Light Crossbow", "ranged", 1, 8, 1, { normalRange: 80, longRange: 320, projectile: "bolt" })),
      ],
      attackBonus: 3, weapon_masteries: [], features: [], passive_perception: 10,
      visual: { armor: "leather", off_hand: null, body_style: "bandit" },
    },
    "srd-guard": {
      id: "srd-guard", name: "Guard", archetype: "Guard", level: null,
      challenge_rating: "1/8", armor_class: 16, max_hp: 11, speed_ft: 30, initiative_bonus: 1,
      openingDistance: 5,
      attacks: [
        attack("guard-spear-melee", weapon("spear", "Spear", "melee", 1, 6, 1)),
        attack("guard-spear-thrown", weapon("spear", "Spear", "ranged", 1, 6, 1, { normalRange: 20, longRange: 60, projectile: "spear" })),
      ],
      attackBonus: 3, weapon_masteries: [], features: [], skill_bonuses: { perception: 2 }, passive_perception: 12,
      visual: { armor: "chain-shirt", off_hand: "shield", body_style: "guard" },
    },
  };

  window.IRON_PIT_TEST_ROSTER = { characters, monsters };
})();
