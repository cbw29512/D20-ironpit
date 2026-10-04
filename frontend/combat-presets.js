(() => {
  "use strict";

  const allRecipes = () => window.IRON_PIT_COMBAT_PRESET_RECIPES.recipes;
  const xp = {
    "0": 10, "1/8": 25, "1/4": 50, "1/2": 100, "1": 200, "2": 450, "3": 700, "4": 1100,
    "5": 1800, "6": 2300, "7": 2900, "8": 3900, "9": 5000, "10": 5900, "11": 7200,
  };
  const thresholds = {
    2: [50, 100, 150, 200], 3: [75, 150, 225, 400], 4: [125, 250, 375, 500],
    5: [250, 500, 750, 1100], 6: [300, 600, 900, 1400], 7: [350, 750, 1100, 1700],
    9: [550, 1100, 1600, 2400], 11: [800, 1600, 2400, 3600], 15: [1400, 2800, 4300, 6400],
    20: [2800, 5700, 8500, 12700],
  };

  function monsterTemplateId(recipe, slug) {
    return recipe.ruleset === "2014" ? `2014-${slug}` : `srd-${slug}`;
  }

  function aspectFired(battle, spec) {
    try {
      return (battle.events || []).some((event) => {
        if (spec.kind === "feature") return event.feature_id === spec.value;
        if (spec.kind === "anyFeature") return spec.value.includes(event.feature_id);
        if (spec.kind === "condition") return (event.applied_condition_ids || []).includes(spec.value);
        if (spec.kind === "event") return event.event_type === spec.value;
        if (spec.kind === "source") return (event.damage_components || []).some((part) => part.source === spec.value);
        if (spec.kind === "text") return String(event.description || "").includes(spec.value);
        if (spec.kind === "concentration") return Boolean(event.concentration_started_effect_id);
        throw new Error(`Unknown preset aspect kind ${spec.kind}.`);
      });
    } catch (error) {
      console.error("Preset aspect check failed", { spec, error });
      throw error;
    }
  }

  function resolve(recipe, catalog) {
    try {
      if (catalog.ruleset !== recipe.ruleset) throw new Error(`Preset ${recipe.id} requires the ${recipe.ruleset} catalog.`);
      const heroes = recipe.classes.map((id) => catalog.heroes.find((card) => card.class_id === id && card.level === recipe.level));
      const monsters = recipe.monsters.map((id) => catalog.monsters.find((card) => card.runnable_template_id === monsterTemplateId(recipe, id)));
      if ([...heroes, ...monsters].some((card) => !card || card.ruleset !== recipe.ruleset || card.coverage_status !== "raw_ready" || !card.runnable_template_id)) {
        throw new Error(`Preset ${recipe.id} has unavailable cards.`);
      }
      const multipliers = [0.5, 1, 1.5, 2, 2.5];
      const index = (monsters.length === 1 ? 1 : monsters.length === 2 ? 2 : 3) + (heroes.length < 3 ? 1 : heroes.length >= 6 ? -1 : 0);
      const base = monsters.reduce((total, card) => {
        if (xp[card.challenge_rating] === undefined) throw new Error(`Unmapped preset CR ${card.challenge_rating}.`);
        return total + xp[card.challenge_rating];
      }, 0);
      const adjusted = base * multipliers[index];
      const limits = (thresholds[recipe.level] || thresholds[5]).map((value) => value * heroes.length);
      const difficulty = ["Below Easy", "Easy", "Medium", "Hard", "Deadly"][limits.filter((limit) => adjusted >= limit).length];
      return { heroes, monsters, adjusted, difficulty };
    } catch (error) {
      console.error("Combat preset validation failed", { preset: recipe.id, error });
      throw error;
    }
  }

  function renderGroup(host, label, group, catalogs, api) {
    const heading = document.createElement("h3");
    heading.className = "preset-group-heading";
    heading.textContent = label;
    host.append(heading);
    for (const recipe of group) {
      const cards = resolve(recipe, catalogs[recipe.ruleset]);
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.preset = recipe.id;
      button.dataset.ruleset = recipe.ruleset;
      const title = document.createElement("strong");
      const roster = document.createElement("span");
      const purpose = document.createElement("span");
      title.textContent = recipe.title;
      roster.textContent = `Level ${recipe.level} ${recipe.classes.join(" / ")} vs ${cards.monsters.map((card) => `${card.name} (CR ${card.challenge_rating})`).join(" / ")} · ${cards.difficulty} estimate (${cards.adjusted.toLocaleString()} adjusted XP)`;
      purpose.textContent = `Look for: ${recipe.purpose}`;
      button.append(title, roster, purpose);
      button.addEventListener("click", async () => {
        try {
          if (api.state.fighting || (api.state.session && !api.state.session.complete)) return;
          if (api.ensureRuleset) await api.ensureRuleset(recipe.ruleset);
          const catalog = api.state.catalog;
          const selection = resolve(recipe, catalog);
          api.load(selection.heroes, selection.monsters, `${recipe.title} loaded. Look for: ${recipe.purpose}`);
        } catch (error) {
          console.error("Combat preset loading failed", { preset: recipe.id, error });
          document.getElementById("status").textContent = "Preset could not be loaded. See console for details.";
        }
      });
      host.append(button);
    }
  }

  async function install(api) {
    try {
      const host = document.getElementById("combat-presets");
      if (!host) throw new Error("Combat preset panel is missing.");
      const catalogs = {
        "2014": api.state.catalog?.ruleset === "2014" ? api.state.catalog : await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2014"),
        "2024": await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2024"),
      };
      host.replaceChildren();
      renderGroup(host, "2014 certified fights", allRecipes().filter((recipe) => recipe.ruleset === "2014"), catalogs, api);
      renderGroup(host, "2024 certified fights", allRecipes().filter((recipe) => recipe.ruleset === "2024"), catalogs, api);
    } catch (error) {
      console.error("Combat preset panel initialization failed", error);
      throw error;
    }
  }

  function sync(state) {
    for (const button of document.querySelectorAll("[data-preset]")) {
      button.disabled = state.fighting || Boolean(state.session && !state.session.complete);
    }
  }

  window.IRON_PIT_COMBAT_PRESETS = {
    get recipes() { return allRecipes(); },
    resolve, install, sync, aspectFired, monsterTemplateId,
  };
})();
