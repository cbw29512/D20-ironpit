(() => {
  "use strict";

  const HERO_ROWS = [
    ["barbarian", "Barbarian", "Rokhan Stonefury", "path-berserker", "Path of the Berserker"],
    ["bard", "Bard", "Lyra Silverstring", "college-lore", "College of Lore"],
    ["cleric", "Cleric", "Seraphine Dawnshield", "life-domain", "Life Domain"],
    ["druid", "Druid", "Thalen Greenbough", "circle-land", "Circle of the Land"],
    ["fighter", "Fighter", "Karnok Stoneward", "champion", "Champion"],
    ["monk", "Monk", "Kael Stillwater", "warrior-open-hand", "Warrior of the Open Hand"],
    ["paladin", "Paladin", "Aurelia Brightshield", "oath-devotion", "Oath of Devotion"],
    ["ranger", "Ranger", "Rowan Ashtrail", "hunter", "Hunter"],
    ["rogue", "Rogue", "Mara Quickstep", "thief", "Thief"],
    ["sorcerer", "Sorcerer", "Nyra Emberveil", "draconic-sorcery", "Draconic Sorcery"],
    ["warlock", "Warlock", "Varek Ashenmark", "fiend-patron", "Fiend Patron"],
    ["wizard", "Wizard", "Elian Starweaver", "evoker", "Evoker"],
  ];

  function readyHeroIndex(registry = window.IRON_PIT_BROWSER_HEROES) {
    return new Map(Object.values(registry || {}).map((hero) => [`${hero.class_id}:${hero.level}`, hero]));
  }

  function buildHeroes2024() {
    const cards = [], readyHeroes = readyHeroIndex();
    for (const [classId, className, heroName, subclassId, subclassName] of HERO_ROWS) {
      for (let level = 1; level <= 20; level += 1) {
        const runtime = readyHeroes.get(`${classId}:${level}`) || null;
        cards.push({
          id: `hero-2024-${classId}-l${level}`, name: heroName, class_id: classId, class_name: className,
          level, build_id: "canonical", build_name: "Canonical RAW Progression",
          subclass_id: level >= 3 ? subclassId : null, subclass_name: level >= 3 ? subclassName : null,
          ruleset: "2024", kind: "character", coverage_status: runtime ? "raw_ready" : "blocked",
          runnable_template_id: runtime?.id || null,
          blockers: runtime ? [] : ["hero-level-not-certified", "combat-feature-coverage-not-certified"],
        });
      }
    }
    return cards;
  }

  function buildHeroes2014() {
    const readyHeroes = readyHeroIndex(window.IRON_PIT_BROWSER_HEROES_2014);
    return Array.from({ length: 10 }, (_, index) => {
      const level = index + 1, runtime = readyHeroes.get(`fighter:${level}`) || null;
      return {
        id: `hero-2014-fighter-l${level}`, name: "Karnok Stoneward", class_id: "fighter", class_name: "Fighter",
        level, build_id: "canonical-2014", build_name: "Canonical 2014 RAW Progression",
        subclass_id: level >= 3 ? "champion" : null, subclass_name: level >= 3 ? "Champion" : null,
        ruleset: "2014", kind: "character", coverage_status: runtime ? "raw_ready" : "blocked",
        runnable_template_id: runtime?.id || null,
        blockers: runtime ? [] : ["hero-level-not-certified", "combat-feature-coverage-not-certified"],
      };
    });
  }

  function readyMonsterCards(registry = window.IRON_PIT_BROWSER_MONSTERS) {
    return Object.values(registry || {}).map((monster) => ({
      id: `catalog-${monster.id}`, name: monster.name, challenge_rating: monster.challenge_rating,
      monster_type: monster.archetype, armor_class: monster.armor_class, hit_points: monster.max_hp,
      ruleset: monster.ruleset, kind: "monster", coverage_status: "raw_ready",
      runnable_template_id: monster.id, blockers: [],
    }));
  }

  async function buildMonsters2024() {
    const ready = new Map(Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => [monster.name, monster.id]));
    try {
      const response = await fetch("data/srd_5_2_1_monsters.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`Monster catalog returned ${response.status}`);
      const rows = await response.json();
      if (!Array.isArray(rows) || rows.length !== 330) throw new Error("Expected 330 SRD monsters.");
      return rows.map((row) => {
        const templateId = ready.get(row.name) || null;
        return {
          id: row.id, name: row.name, challenge_rating: String(row.challenge).split(" ")[0], monster_type: row.type,
          armor_class: row.armorClass, hit_points: row.hitPoints, speed: row.speed, ruleset: "2024", kind: "monster",
          coverage_status: templateId ? "raw_ready" : "blocked", runnable_template_id: templateId,
          blockers: templateId ? [] : ["monster-combat-mechanics-not-certified"],
        };
      });
    } catch (error) {
      console.warn("Full static monster catalog unavailable; using certified runtime subset.", error);
      return readyMonsterCards();
    }
  }

  function build2014() {
    if (window.IRON_PIT_2014_MVP_READY !== true) throw new Error("Certified 2014 browser monster bundle did not load.");
    if (!window.IRON_PIT_BROWSER_HEROES_2014) throw new Error("Certified 2014 browser pregen bundle did not load.");
    const heroes = buildHeroes2014(), monsters = readyMonsterCards(window.IRON_PIT_BROWSER_MONSTERS_2014);
    const readyHeroes = heroes.filter((card) => card.coverage_status === "raw_ready");
    if (monsters.length < 100) throw new Error(`2014 playtest requires at least 100 certified monsters; found ${monsters.length}.`);
    if (readyHeroes.length !== 10) throw new Error(`2014 playtest requires Fighter levels 1-10; found ${readyHeroes.length}.`);
    if (monsters.some((card) => card.ruleset !== "2014" || card.kind !== "monster")) throw new Error("2014 monster catalog crossed the ruleset boundary.");
    return {
      heroes, monsters,
      hero_count: heroes.length, monster_count: 327, hero_ready_count: readyHeroes.length,
      monster_ready_count: monsters.length, ruleset: "2014", test_lane: false,
    };
  }

  async function buildCatalog(ruleset = "2024") {
    if (ruleset === "2014") return build2014();
    if (ruleset !== "2024") throw new Error(`Unsupported browser ruleset: ${ruleset}`);
    const heroes = buildHeroes2024(), monsters = await buildMonsters2024();
    return {
      heroes, monsters, hero_count: heroes.length, monster_count: monsters.length,
      hero_ready_count: heroes.filter((item) => item.coverage_status === "raw_ready").length,
      monster_ready_count: monsters.filter((item) => item.coverage_status === "raw_ready").length,
      ruleset: "2024", test_lane: false,
    };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();