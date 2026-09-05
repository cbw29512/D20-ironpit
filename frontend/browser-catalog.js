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

  function readyHeroIndex() {
    return new Map(Object.values(window.IRON_PIT_BROWSER_HEROES).map((hero) => [
      `${hero.class_id}:${hero.level}`,
      hero,
    ]));
  }

  function buildHeroes() {
    const cards = [], readyHeroes = readyHeroIndex();
    for (const [classId, className, heroName, subclassId, subclassName] of HERO_ROWS) {
      for (let level = 1; level <= 20; level += 1) {
        const runtime = readyHeroes.get(`${classId}:${level}`) || null;
        cards.push({
          id: `hero-2024-${classId}-l${level}`,
          name: heroName,
          class_id: classId,
          class_name: className,
          level,
          build_id: "canonical",
          build_name: "Canonical RAW Progression",
          subclass_id: level >= 3 ? subclassId : null,
          subclass_name: level >= 3 ? subclassName : null,
          coverage_status: runtime ? "raw_ready" : "blocked",
          runnable_template_id: runtime?.id || null,
          blockers: runtime ? [] : ["hero-level-not-certified", "combat-feature-coverage-not-certified"],
        });
      }
    }
    return cards;
  }

  function readyMonsterCards() {
    return Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => ({
      id: `catalog-${monster.id}`, name: monster.name, challenge_rating: monster.challenge_rating,
      monster_type: monster.archetype, size: monster.size, coverage_status: "raw_ready", runnable_template_id: monster.id, blockers: [],
    }));
  }

  async function buildMonsters() {
    const ready = new Map(Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => [monster.name, monster.id]));
    try {
      const response = await fetch("data/srd_5_2_1_monsters.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`Monster catalog returned ${response.status}`);
      const rows = await response.json();
      if (!Array.isArray(rows) || rows.length !== 330) throw new Error("Expected 330 SRD monsters.");
      return rows.map((row) => {
        const templateId = ready.get(row.name) || null;
        return {
          id: row.id, name: row.name, challenge_rating: String(row.challenge).split(" ")[0], monster_type: row.type, size: row.size,
          armor_class: row.armorClass, hit_points: row.hitPoints, speed: row.speed,
          coverage_status: templateId ? "raw_ready" : "blocked", runnable_template_id: templateId,
          blockers: templateId ? [] : ["monster-combat-mechanics-not-certified"],
        };
      });
    } catch (error) {
      console.warn("Full static monster catalog unavailable; using certified runtime subset.", error);
      return readyMonsterCards();
    }
  }

  async function buildCatalog() {
    const heroes = buildHeroes(), monsters = await buildMonsters();
    return { heroes, monsters, hero_count: heroes.length, monster_count: monsters.length };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();
