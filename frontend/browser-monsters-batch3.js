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
    attacks, primary_attack_id: attacks[0].id, traits: [], resources: {},
    source: `SRD 5.2.1 ${name}`, ...extra,
  });

  const items = [
    monster("srd-ogre", "Ogre", "2", "large", 11, 68, 40, -1, [
      attack("ogre-greatclub", "Greatclub", "melee", 6, 2, 8, 4, "bludgeoning", { animation: "heavy-strike" }),
      attack("ogre-javelin-melee", "Javelin", "melee", 6, 2, 6, 4, "piercing", { animation: "heavy-strike" }),
      attack("ogre-javelin", "Javelin", "ranged", 6, 2, 6, 4, "piercing", {
        normal: 30, long: 120, projectile: "spear", animation: "projectile",
      }),
    ]),
    monster("srd-owlbear", "Owlbear", "3", "large", 13, 59, 40, 1, [
      attack("owlbear-rend", "Rend", "melee", 7, 2, 8, 5, "slashing", { animation: "heavy-slash" }),
    ], { attack_action: { id: "owlbear-multiattack", slots: [["owlbear-rend"], ["owlbear-rend"]] } }),
    monster("srd-saber-toothed-tiger", "Saber-Toothed Tiger", "2", "large", 13, 52, 40, 3, [
      attack("saber-toothed-tiger-rend", "Rend", "melee", 6, 2, 6, 4, "slashing", { animation: "heavy-slash" }),
    ], { attack_action: { id: "saber-toothed-tiger-multiattack", slots: [["saber-toothed-tiger-rend"], ["saber-toothed-tiger-rend"]] } }),
    monster("srd-scout", "Scout", "1/2", "medium", 13, 16, 30, 2, [
      attack("scout-longbow", "Longbow", "ranged", 4, 1, 8, 2, "piercing", {
        normal: 150, long: 600, projectile: "arrow", animation: "projectile",
      }),
      attack("scout-shortsword", "Shortsword", "melee", 4, 1, 6, 2, "piercing", { animation: "quick-strike" }),
    ], { attack_action: { id: "scout-multiattack", slots: [
      ["scout-longbow", "scout-shortsword"], ["scout-longbow", "scout-shortsword"],
    ] } }),
    monster("srd-warrior-infantry", "Warrior Infantry", "1/8", "medium", 13, 9, 30, 0, [
      attack("warrior-infantry-spear-melee", "Spear", "melee", 3, 1, 6, 1, "piercing", { animation: "quick-strike" }),
      attack("warrior-infantry-spear-ranged", "Spear", "ranged", 3, 1, 6, 1, "piercing", {
        normal: 20, long: 60, projectile: "spear", animation: "projectile",
      }),
    ], { traits: ["pack-tactics"] }),
  ];

  Object.assign(window.IRON_PIT_BROWSER_MONSTERS, Object.fromEntries(items.map((item) => [item.id, item])));
})();
