(() => {
  "use strict";

  const CLASS_ROWS = [
    ["barbarian", "Barbarian", "path-berserker", "Path of the Berserker"],
    ["bard", "Bard", "college-lore", "College of Lore"],
    ["cleric", "Cleric", "life-domain", "Life Domain"],
    ["druid", "Druid", "circle-land", "Circle of the Land"],
    ["fighter", "Fighter", "champion", "Champion"],
    ["monk", "Monk", "warrior-open-hand", "Warrior of the Open Hand"],
    ["paladin", "Paladin", "oath-devotion", "Oath of Devotion"],
    ["ranger", "Ranger", "hunter", "Hunter"],
    ["rogue", "Rogue", "thief", "Thief"],
    ["sorcerer", "Sorcerer", "draconic-sorcery", "Draconic Sorcery"],
    ["warlock", "Warlock", "fiend-patron", "Fiend Patron"],
    ["wizard", "Wizard", "evoker", "Evoker"],
  ];
  const BUILD_ROWS = {
    barbarian: [["great-weapon", "Great Weapon"], ["axe-shield", "Axe & Shield"], ["dual-wielder", "Dual Wielder"]],
    bard: [["support", "Support"], ["duelist", "Duelist"], ["controller", "Controller"]],
    cleric: [["guardian", "Guardian"], ["healer", "Healer"], ["war-priest", "War Priest"]],
    druid: [["wild-shaper", "Wild Shaper"], ["primal-caster", "Primal Caster"], ["warden", "Warden"]],
    fighter: [["guardian", "Sword & Shield"], ["great-weapon", "Great Weapon"], ["archer", "Archer"]],
    monk: [["striker", "Striker"], ["skirmisher", "Skirmisher"], ["defender", "Defender"]],
    paladin: [["guardian", "Guardian"], ["great-weapon", "Great Weapon"], ["avenger", "Avenger"]],
    ranger: [["archer", "Archer"], ["dual-wielder", "Dual Wielder"], ["warden", "Warden"]],
    rogue: [["skirmisher", "Skirmisher"], ["archer", "Archer"], ["duelist", "Duelist"]],
    sorcerer: [["blaster", "Blaster"], ["controller", "Controller"], ["survivor", "Survivor"]],
    warlock: [["eldritch-blaster", "Eldritch Blaster"], ["blade", "Blade"], ["controller", "Controller"]],
    wizard: [["evoker", "Evoker"], ["controller", "Controller"], ["defender", "Defender"]],
  };

  function heroId(classId, level, buildId, index) {
    const base = `hero-2024-${classId}-l${level}`;
    return index === 0 ? base : `${base}-${buildId}`;
  }

  function buildHeroes() {
    const cards = [];
    for (const [classId, className, subclassId, subclassName] of CLASS_ROWS) {
      for (let level = 1; level <= 20; level += 1) {
        BUILD_ROWS[classId].forEach(([buildId, buildName], index) => {
          const ready = classId === "fighter" && level === 1 && buildId === "great-weapon";
          cards.push({
            id: heroId(classId, level, buildId, index),
            name: ready ? "Karnok Stoneward" : `${className} ${level} — ${buildName}`,
            class_id: classId, class_name: className, level, build_id: buildId, build_name: buildName,
            subclass_id: level >= 3 ? subclassId : null, subclass_name: level >= 3 ? subclassName : null,
            coverage_status: ready ? "raw_ready" : "blocked",
            runnable_template_id: ready ? "karnok-stoneward-l1" : null,
            blockers: ready ? [] : ["legal-character-build-not-certified", "combat-feature-coverage-not-certified"],
          });
        });
      }
    }
    return cards;
  }

  function readyMonsterCards() {
    return Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => ({
      id: `catalog-${monster.id}`, name: monster.name, challenge_rating: monster.challenge_rating,
      monster_type: monster.archetype, coverage_status: "raw_ready", runnable_template_id: monster.id, blockers: [],
    }));
  }

  async function buildMonsters() {
    const ready = new Map(Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => [monster.name, monster.id]));
    try {
      const response = await fetch("data/srd_5_2_1_monsters.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`Monster catalog returned ${response.status}`);
      const rows = await response.json();
      if (!Array.isArray(rows) || rows.length !== 328) throw new Error("Expected 328 SRD monsters.");
      return rows.map((row) => {
        const templateId = ready.get(row.name) || null;
        return {
          id: row.id, name: row.name, challenge_rating: String(row.challenge).split(" ")[0], monster_type: row.type,
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
    const heroes = buildHeroes();
    const monsters = await buildMonsters();
    return { heroes, monsters, hero_count: heroes.length, monster_count: monsters.length };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();
