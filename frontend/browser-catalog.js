(() => {
  "use strict";

  const D = () => window.IRON_PIT_PREGEN_DATA;

  function heroId(classId, level, buildId, index) {
    const base = `hero-2024-${classId}-l${level}`;
    return index === 0 ? base : `${base}-${buildId}`;
  }

  function readyHeroIndex() {
    return new Map(Object.values(window.IRON_PIT_BROWSER_HEROES).map((hero) => [
      `${hero.class_id}:${hero.level}:${hero.build_id}`,
      hero,
    ]));
  }

  function buildHeroes() {
    const cards = [], readyHeroes = readyHeroIndex();
    for (const [classId, className, subclassId, subclassName] of D().CLASS_ROWS) {
      for (let level = 1; level <= 20; level += 1) {
        D().BUILD_ROWS[classId].forEach(([buildId, buildName], index) => {
          const runtime = readyHeroes.get(`${classId}:${level}:${buildId}`) || null;
          const full = Boolean(runtime?.full_feature_coverage);
          cards.push({
            id: heroId(classId, level, buildId, index),
            name: runtime?.name || `${className} ${level} — ${buildName}`,
            class_id: classId, class_name: className, level, build_id: buildId, build_name: buildName,
            subclass_id: level >= 3 ? subclassId : null, subclass_name: level >= 3 ? subclassName : null,
            coverage_status: runtime ? (full ? "raw_ready" : "raw_playable") : "blocked",
            automation_coverage: runtime?.automation_coverage || "none",
            runnable_template_id: runtime?.id || null,
            blockers: runtime ? [] : ["legal-character-runtime-missing"],
            feature_gaps: runtime && !full ? ["advanced-class-and-subclass-actions-still-expanding"] : [],
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
      if (!Array.isArray(rows) || rows.length !== 330) throw new Error("Expected 330 SRD monsters.");
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
    const heroes = buildHeroes(), monsters = await buildMonsters();
    return { heroes, monsters, hero_count: heroes.length, monster_count: monsters.length };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();
