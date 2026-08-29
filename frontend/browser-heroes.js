(() => {
  "use strict";

  const attack = (id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType,
    reach: kind === "melee" ? 5 : 0,
    ...extra,
  });

  const karnok = {
    id: "karnok-stoneward-l1", class_id: "fighter", build_id: "great-weapon",
    name: "Karnok Stoneward", archetype: "Fighter", level: 1, kind: "character", size: "medium",
    armor_class: 17, max_hp: 12, speed_ft: 30, initiative_bonus: 1,
    attacks: [
      attack("karnok-greatsword", "Greatsword", "melee", 5, 2, 6, 3, "slashing", { animation: "heavy-slash" }),
      attack("karnok-shortbow", "Shortbow", "ranged", 3, 1, 6, 1, "piercing", {
        normal: 80, long: 320, projectile: "arrow", animation: "projectile",
      }),
    ],
    primary_attack_id: "karnok-greatsword",
    traits: ["savage-attacker", "adrenaline-rush", "relentless-endurance"],
    resources: { "second-wind": 2, "adrenaline-rush": 2, "relentless-endurance": 1 },
    visual: { armor: "chain-mail", main_hand: "greatsword", body_style: "humanoid" },
    source: "D&D 2024 Free Rules: Fighter, Orc, Soldier, Savage Attacker",
  };

  const rokhan = {
    id: "rokhan-stonefury-l1", class_id: "barbarian", build_id: "great-weapon",
    name: "Rokhan Stonefury", archetype: "Barbarian", level: 1, kind: "character", size: "medium",
    armor_class: 13, max_hp: 14, speed_ft: 30, initiative_bonus: 1,
    attacks: [
      attack("rokhan-greataxe", "Greataxe", "melee", 5, 1, 12, 3, "slashing", {
        animation: "heavy-slash", rageEligible: true,
      }),
      attack("rokhan-handaxe-thrown", "Handaxe", "ranged", 5, 1, 6, 3, "slashing", {
        normal: 20, long: 60, projectile: "handaxe", animation: "projectile", rageEligible: true,
      }),
    ],
    primary_attack_id: "rokhan-greataxe",
    traits: ["savage-attacker", "adrenaline-rush", "relentless-endurance"],
    resources: { rage: 2, "adrenaline-rush": 2, "relentless-endurance": 1 },
    rage_damage_bonus: 2,
    wearing_heavy_armor: false,
    visual: { armor: "unarmored", main_hand: "greataxe", body_style: "humanoid" },
    source: "D&D 2024 Free Rules: Barbarian, Orc, Soldier, Savage Attacker",
  };

  window.IRON_PIT_BROWSER_HEROES = Object.fromEntries([karnok, rokhan].map((item) => [item.id, item]));
})();
