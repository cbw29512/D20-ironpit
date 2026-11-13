(() => {
  "use strict";

  // Test-plan schema: {mode, editions, duel_total, presets, total, at(index)}.
  // Each case uses the existing battle engine; source cards are never edited.
  const EDITIONS = ["2014", "2024"];

  function roster(edition) {
    try {
      const heroes = Object.values(window.IRON_PIT_BROWSER_HEROES || {});
      const monsters = Object.values(edition === "2014"
        ? window.IRON_PIT_BROWSER_MONSTERS_2014 || {}
        : window.IRON_PIT_BROWSER_MONSTERS || {});
      const ids = rows => [...new Set(rows.filter(card =>
        card?.ruleset === edition && typeof card.id === "string"
      ).map(card => card.id))].sort();
      const hero_ids = ids(heroes), monster_ids = ids(monsters);
      if (!hero_ids.length || !monster_ids.length)
        throw new Error(`No playable ${edition} heroes or monsters are loaded.`);
      return {edition, hero_ids, monster_ids};
    } catch (error) {
      console.error("Failed to build certified roster sweep plan", {edition, error});
      throw error;
    }
  }

  async function sourcePresets() {
    try {
      const recipes = window.IRON_PIT_COMBAT_PRESET_RECIPES?.recipes;
      const resolver = window.IRON_PIT_COMBAT_PRESETS?.resolve;
      const catalog = window.IRON_PIT_BROWSER_CATALOG?.buildCatalog;
      if (!Array.isArray(recipes) || !resolver || !catalog)
        throw new Error("Source-owned combat preset catalog is unavailable.");
      const catalogs = {};
      for (const edition of EDITIONS)
        catalogs[edition] = await catalog(edition);
      const unavailable = Object.fromEntries(EDITIONS.map(edition => [
        edition, (catalogs[edition].monsters || []).filter(card =>
          card.coverage_status !== "raw_ready").length,
      ]));
      const entries = recipes.map(recipe => {
        const resolved = resolver(recipe, catalogs[recipe.ruleset]);
        return {
          kind: "preset", label: recipe.title || recipe.id, seed: recipe.seed,
          required_aspects: recipe.aspects || [],
          selection: {
            ruleset: recipe.ruleset,
            hero_ids: resolved.heroes.map(card => card.runnable_template_id),
            monster_ids: resolved.monsters.map(card => card.runnable_template_id),
          },
        };
      });
      return {entries, unavailable};
    } catch (error) {
      console.error("Could not resolve certified combat presets for full sweep", error);
      throw error;
    }
  }

  async function create(mode) {
    try {
      if (!["presets", "cards", "pairs"].includes(mode))
        throw new Error("Sweep mode must be 'presets', 'cards', or 'pairs'.");
      const editions = EDITIONS.map(roster);
      const {entries: presets, unavailable} = await sourcePresets();
      const counts = editions.map(entry => mode === "presets" ? 0
        : mode === "pairs" ? entry.hero_ids.length * entry.monster_ids.length
        : entry.hero_ids.length + entry.monster_ids.length);
      const duel_total = counts.reduce((sum, count) => sum + count, 0);
      const total = duel_total + presets.length;

      function at(index) {
        try {
          if (!Number.isInteger(index) || index < 0 || index >= total)
            throw new RangeError("Sweep case index is out of bounds.");
          if (index >= duel_total) return presets[index - duel_total];
          let n = index;
          for (let i = 0; i < editions.length; i += 1) {
            if (n >= counts[i]) { n -= counts[i]; continue; }
            const {edition, hero_ids, monster_ids} = editions[i];
            const h = hero_ids.length, m = monster_ids.length;
            const hi = mode === "pairs" ? Math.floor(n / m)
              : n < h ? n : (n - h) % h;
            const mi = mode === "pairs" ? n % m
              : n < h ? n % m : n - h;
            return {
              kind: "duel", label: `${hero_ids[hi]} vs ${monster_ids[mi]}`,
              selection: {ruleset: edition, hero_ids: [hero_ids[hi]],
                monster_ids: [monster_ids[mi]]},
            };
          }
          throw new Error("Unable to resolve a planned duel.");
        } catch (error) {
          console.error("Could not resolve test case from full roster plan", {index, error});
          throw error;
        }
      }
      return {mode, editions, unavailable, presets_count: presets.length,
        duel_total, total, at};
    } catch (error) {
      console.error("Test All plan could not be created", {mode, error});
      throw error;
    }
  }

  window.IRON_PIT_TEST_ALL_PLAN = {create, roster};
})();
