(() => {
  "use strict";
  // Selection recipes only: immutable source cards, ordinary placement and engine execution.
  const recipes = [
    ["duel", "1v1 · Monk discipline", 5, ["monk"], ["brown-bear"], "Ki, Flurry of Blows, Stunning Strike, Open Hand effects and multiattack."],
    ["goblins", "1v2 · Barbarian vs two Goblins", 3, ["barbarian"], ["goblin", "goblin"], "Rage, Reckless Attack, Frenzy, weapon resistance and two-opponent targeting pressure."],
    ["partners", "2v2 · Steel and healing", 5, ["fighter", "cleric"], ["brown-bear", "dire-wolf"], "Extra Attack, Action Surge, healing, concentration, Pack Tactics and prone saves."],
    ["casters", "3v3 · Fireproof opposition", 7, ["wizard", "sorcerer", "bard"], ["hell-hound", "hell-hound", "hell-hound"], "Spell selection against fire immunity, area saves, breath recharge, Metamagic and Bard support."],
    ["auras", "4v4 · Mixed arms", 9, ["paladin", "ranger", "druid", "warlock"], ["minotaur", "hell-hound", "owlbear", "blue-dragon-wyrmling"], "Smite, save auras, ranged attacks, concentration, charge, multiattack and breath geometry."],
    ["pressure", "5v5 · Breath and trampling", 11, ["barbarian", "rogue", "cleric", "monk", "wizard"], ["elephant", "elephant", "red-dragon-wyrmling", "red-dragon-wyrmling", "red-dragon-wyrmling"], "Sneak Attack, Uncanny Dodge, Evasion, healing under pressure, prone and area damage."],
    ["party", "6v6 · Full party stress test", 15, ["fighter", "paladin", "cleric", "rogue", "sorcerer", "warlock"], ["young-black-dragon", "young-black-dragon", "young-black-dragon", "giant-ape", "giant-ape", "giant-ape"], "Team targeting, auras, reactions, ranged rock attacks, acid breaths, large footprints and resource use."],
    ["grapple", "2v2 · Escape the coils", 4, ["monk", "rogue"], ["giant-constrictor-snake", "giant-constrictor-snake"], "Grappled and Restrained, escape checks, movement restrictions and attack advantage/disadvantage."],
    ["poison", "3v3 · Poison and recovery", 6, ["paladin", "cleric", "ranger"], ["giant-scorpion", "giant-scorpion", "giant-scorpion"], "Poison damage saves, grapple attacks, healing, Lay on Hands and saving-throw support."],
    ["undead", "2v2 · Undead endurance", 2, ["cleric", "fighter"], ["zombie", "skeleton"], "Undead Fortitude, radiant damage interactions, bludgeoning vulnerability and low-level survival."],
    ["capstones", "6v6 · Level 20 martial abilities", 20, ["barbarian", "fighter", "monk", "paladin", "rogue", "ranger"], ["roc", "roc", "roc", "roc", "roc", "roc"], "High-level class resources, expanded criticals, Quivering Palm, defensive abilities and Gargantuan-creature grapples."],
    ["archmages", "6v6 · Level 20 spell abilities", 20, ["bard", "cleric", "druid", "sorcerer", "warlock", "wizard"], ["young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon", "young-red-dragon"], "High-level spell choice, HP-threshold spells where available, concentration, healing, resistance and slot spending."],
  ].map(([id, title, level, classes, monsters, purpose]) => Object.freeze({ id, title, level, classes: Object.freeze(classes), monsters: Object.freeze(monsters), purpose }));
  Object.freeze(recipes);
  const xp = { "1/4": 50, "1": 200, "2": 450, "3": 700, "4": 1100, "7": 2900, "10": 5900, "11": 7200, "1/8": 25 };
  const thresholds = { 2: [50,100,150,200], 3: [75,150,225,400], 4: [125,250,375,500], 5: [250,500,750,1100], 6: [300,600,900,1400], 7: [350,750,1100,1700], 9: [550,1100,1600,2400], 11: [800,1600,2400,3600], 15: [1400,2800,4300,6400], 20: [2800,5700,8500,12700] };
  function resolve(recipe, catalog) {
    try {
      if (catalog.ruleset !== "2014") throw new Error("Combat presets require the certified 2014 catalog.");
      const heroes = recipe.classes.map((id) => catalog.heroes.find((card) => card.class_id === id && card.level === recipe.level));
      const monsters = recipe.monsters.map((id) => catalog.monsters.find((card) => card.runnable_template_id === `2014-${id}`));
      if ([...heroes, ...monsters].some((card) => !card || card.ruleset !== "2014" || card.coverage_status !== "raw_ready" || !card.runnable_template_id)) throw new Error(`Preset ${recipe.id} has unavailable cards.`);
      const multipliers = [0.5, 1, 1.5, 2, 2.5];
      const index = (monsters.length === 1 ? 1 : monsters.length === 2 ? 2 : 3) + (heroes.length < 3 ? 1 : heroes.length >= 6 ? -1 : 0);
      const base = monsters.reduce((total, card) => {
        if (xp[card.challenge_rating] === undefined) throw new Error(`Unmapped preset CR ${card.challenge_rating}.`);
        return total + xp[card.challenge_rating];
      }, 0);
      const adjusted = base * multipliers[index], limits = thresholds[recipe.level].map((value) => value * heroes.length);
      const difficulty = ["Below Easy", "Easy", "Medium", "Hard", "Deadly"][limits.filter((limit) => adjusted >= limit).length];
      return { heroes, monsters, adjusted, difficulty };
    } catch (error) { console.error("2014 combat preset validation failed", { preset: recipe.id, error }); throw error; }
  }
  function install(api) {
    try {
      const host = document.getElementById("combat-presets");
      if (!host) throw new Error("Combat preset panel is missing.");
      for (const recipe of recipes) {
        const cards = resolve(recipe, api.state.catalog), button = document.createElement("button");
        button.type = "button"; button.dataset.preset = recipe.id;
        const title = document.createElement("strong"), roster = document.createElement("span"), purpose = document.createElement("span");
        title.textContent = recipe.title;
        roster.textContent = `Level ${recipe.level} ${recipe.classes.join(" / ")} vs ${cards.monsters.map((card) => `${card.name} (CR ${card.challenge_rating})`).join(" / ")} · ${cards.difficulty} estimate (${cards.adjusted.toLocaleString()} adjusted XP)`;
        purpose.textContent = `Look for: ${recipe.purpose}`;
        button.append(title, roster, purpose);
        button.addEventListener("click", () => {
          try {
            if (api.state.fighting || (api.state.session && !api.state.session.complete)) return;
            const selection = resolve(recipe, api.state.catalog);
            api.load(selection.heroes, selection.monsters, `${recipe.title} loaded. Look for: ${recipe.purpose}`);
          } catch (error) { console.error("Combat preset loading failed", { preset: recipe.id, error }); document.getElementById("status").textContent = "Preset could not be loaded. See console for details."; }
        });
        host.append(button);
      }
    } catch (error) { console.error("Combat preset panel initialization failed", error); throw error; }
  }
  function sync(state) {
    for (const button of document.querySelectorAll("[data-preset]")) button.disabled = state.fighting || Boolean(state.session && !state.session.complete);
  }
  window.IRON_PIT_COMBAT_PRESETS = { recipes, resolve, install, sync };
})();
