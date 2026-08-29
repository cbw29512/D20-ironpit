(() => {
  "use strict";

  const attack = (id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType, extra = {}) => ({
    id, name, kind, bonus, diceCount, diceSize, damageBonus, damageType,
    reach: kind === "melee" ? 5 : 0,
    ...extra,
  });

  const karnok = {
    id: "karnok-stoneward-l1",
    name: "Karnok Stoneward",
    archetype: "Fighter",
    level: 1,
    kind: "character",
    size: "medium",
    armor_class: 17,
    max_hp: 12,
    speed_ft: 30,
    initiative_bonus: 1,
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

  window.IRON_PIT_BROWSER_HEROES = { [karnok.id]: karnok };
})();
