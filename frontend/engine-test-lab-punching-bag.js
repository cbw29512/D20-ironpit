(() => {
  "use strict";
  // Source schema: standard homebrew draft, compiled by the same custom
  // monster compiler used by the editor. Never enters the certified rosters.
  const EDITIONS = new Set(["2014", "2024"]);
  function draft(edition) {
    try {
      if (!EDITIONS.has(edition)) throw new Error("Unsupported bag edition.");
      return {
        schema_version: 1, id: "punching-bag", name: "Punching Bag",
        archetype: "Homebrew Training Opponent", kind: "monster", ruleset: edition,
        size: "medium", creature_type: "humanoid", challenge_rating: "0",
        armor_class: 10, max_hp: 10000, speed_ft: 0, initiative_bonus: -10,
        attacks: [{
          id: "harmless-tap", name: "Harmless Tap", attack_kind: "melee",
          attack_bonus: -50, damage: {count: 1, size: 2, bonus: -2},
          damage_type: "bludgeoning", animation: "slash",
        }],
        primary_attack_id: "harmless-tap",
        visual: {armor: "natural", main_hand: "weapon", body_style: "humanoid"},
        source: "User-authorized test-only homebrew; excluded from SRD rosters",
      };
    } catch (error) {
      console.error("Could not define homebrew Punching Bag", {edition, error});
      throw error;
    }
  }
  function template(edition) {
    try {
      const compiler = window.IRON_PIT_CUSTOM_MONSTER_RUNTIME;
      if (!compiler?.compile) throw new Error("Homebrew compiler is not loaded.");
      const compiled = compiler.compile(draft(edition));
      if (compiled.armor_class !== 10 || compiled.max_hp !== 10000
          || compiled.ruleset !== edition || compiled.kind !== "monster")
        throw new Error("Punching Bag did not compile to its locked test stats.");
      const attack = compiled.attacks[0];
      if (attack.diceCount !== 1 || attack.diceSize !== 2
          || attack.damageBonus !== -2 || attack.onHitDamage?.length)
        throw new Error("Punching Bag attack must remain harmless.");
      return compiled;
    } catch (error) {
      console.error("Could not compile test-only homebrew Punching Bag", {edition, error});
      throw error;
    }
  }
  window.IRON_PIT_TEST_PUNCHING_BAG = {draft, template};
})();
