(() => {
  "use strict";
  // Reuse the exact seeded production engine. Only the lab can temporarily
  // put a homebrew monster on the heroes side as a non-hero sparring target.
  // No official card is modified; the registry pointer is always restored.
  function sourceCard(entry) {
    try {
      const heroes = window.IRON_PIT_BROWSER_HEROES || {};
      const monsters = entry.edition === "2014"
        ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {}
        : window.IRON_PIT_BROWSER_MONSTERS || {};
      const card = (entry.source_kind === "pregen" ? heroes : monsters)[entry.source_id];
      if (!card || card.ruleset !== entry.edition ||
          card.kind !== (entry.source_kind === "pregen" ? "character" : "monster"))
        throw new Error("Uncertified or cross-edition Punching Bag source card.");
      return card;
    } catch (error) {
      console.error("Punching Bag source card validation failed", {entry, error});
      throw error;
    }
  }

  function run(entry, seed) {
    try {
      if (entry.kind !== "punching_bag")
        throw new Error("Punching Bag fight requires a Punching Bag plan item.");
      const source = sourceCard(entry);
      const before = JSON.stringify(source);
      const bag = window.IRON_PIT_TEST_PUNCHING_BAG?.template(entry.edition);
      if (!bag) throw new Error("Homebrew Punching Bag is unavailable.");
      const originalHeroes = window.IRON_PIT_BROWSER_HEROES;
      const selection = entry.source_kind === "pregen"
        ? {ruleset: entry.edition, hero_ids: [entry.source_id],
           monster_ids: [bag.id], compiled_monsters: {[bag.id]: bag}}
        : {ruleset: entry.edition, hero_ids: [bag.id],
           monster_ids: [entry.source_id]};
      let replay;
      try {
        if (entry.source_kind === "monster") {
          if (Object.hasOwn(originalHeroes || {}, bag.id))
            throw new Error("Punching Bag ID collides with a certified hero.");
          window.IRON_PIT_BROWSER_HEROES = {...originalHeroes, [bag.id]: bag};
        }
        const turbo = window.IRON_PIT_BROWSER_TURBO;
        if (!turbo?.runSeeded) throw new Error("Certified seeded engine is missing.");
        replay = turbo.runSeeded(selection, seed);
      } finally {
        window.IRON_PIT_BROWSER_HEROES = originalHeroes;
      }
      const members = [...replay.battle.setup.heroes, ...replay.battle.setup.monsters];
      const fighter = members.find(m => m.state.template.id === entry.source_id);
      const dummy = members.find(m => m.state.template.id === bag.id);
      if (!fighter || !dummy || fighter.combatant_id === dummy.combatant_id)
        throw new Error("The fight did not contain the requested card and bag.");
      if (JSON.stringify(source) !== before)
        throw new Error("The certified source card mutated during a bag fight.");
      if (dummy.state.template.armor_class !== 10 ||
          dummy.state.template.max_hp !== 10000)
        throw new Error("Punching Bag combat state has incorrect source stats.");
      return {replay, source, source_actor_id: fighter.combatant_id,
        bag_actor_id: dummy.combatant_id, selection};
    } catch (error) {
      console.error("Punching Bag seeded fight failed", {entry, seed, error});
      throw error;
    }
  }

  window.IRON_PIT_TEST_BAG_FIGHT = {run, sourceCard};
})();
