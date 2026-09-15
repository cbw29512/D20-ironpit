(() => {
  "use strict";

  function buildHeroes() {
    const runtimes = Object.values(window.IRON_PIT_BROWSER_HEROES || {});
    if (!runtimes.length) throw new Error("No certified 2014 hero-side test harness was exported.");
    return runtimes.map((runtime) => {
      if (runtime.ruleset !== "2014" || runtime.test_harness !== true) {
        throw new Error(`Non-2014 hero runtime leaked into playtest: ${runtime.id}`);
      }
      return {
        id: `hero-playtest-${runtime.id}`,
        name: runtime.name,
        class_id: runtime.class_id,
        class_name: runtime.class_name,
        level: 1,
        build_id: runtime.build_id,
        build_name: "2014 SRD Test Harness",
        subclass_id: null,
        subclass_name: null,
        coverage_status: "raw_ready",
        runnable_template_id: runtime.id,
        blockers: [],
      };
    });
  }

  function readyMonsterCards() {
    return Object.values(window.IRON_PIT_BROWSER_MONSTERS).map((monster) => ({
      id: `catalog-${monster.id}`,
      name: monster.name,
      challenge_rating: monster.challenge_rating,
      monster_type: monster.creature_type || monster.archetype,
      coverage_status: "raw_ready",
      runnable_template_id: monster.id,
      blockers: [],
    }));
  }

  function mark2014Playtest(monsterCount, harnessCount) {
    document.title = "The Iron Pit — D&D 5e 2014 Playtest";
    const hero = document.querySelector("header.compact-hero");
    const rulesNotes = hero ? hero.querySelectorAll(".rules-note") : [];
    const eyebrow = hero ? hero.querySelector("p.eyebrow") : null;
    const intro = hero ? hero.querySelector("p:not(.eyebrow):not(.rules-note)") : null;
    if (eyebrow) eyebrow.textContent = "D&D 5e 2014 · SRD PLAYTEST";
    if (intro) intro.textContent = `${monsterCount} ledger-certified 2014 SRD monsters are enabled for live testing.`;
    if (rulesNotes[0]) rulesNotes[0].textContent = "Beta safety gate: uncertified 2014 monsters are hidden and cannot enter combat.";
    if (rulesNotes[1]) rulesNotes[1].textContent = `${harnessCount} certified 2014 SRD NPC stat blocks are exposed on the hero side as a temporary engine test harness; they are not final player pregens.`;
    const logNote = document.querySelector(".log-panel .rules-note");
    if (logNote) logNote.textContent = "D&D 5e 2014 · pure-ruleset engine playtest · expandable rules audit";
  }

  async function buildMonsters() {
    const monsters = readyMonsterCards();
    if (!monsters.length) throw new Error("No certified 2014 monsters were exported for the playtest.");
    return monsters;
  }

  async function buildCatalog() {
    if (window.IRON_PIT_RULESET !== "2014" || window.IRON_PIT_HERO_RULESET !== "2014") {
      throw new Error("2014 playtest requires both monster and hero-side runtimes to use ruleset 2014.");
    }
    const heroes = buildHeroes(), monsters = await buildMonsters();
    mark2014Playtest(monsters.length, heroes.length);
    window.IRON_PIT_PLAYTEST = {
      ruleset: "2014",
      certified_monsters: monsters.length,
      hero_scope: "four ledger-certified 2014 SRD NPC stat blocks used only as an engine test harness",
      final_pregens: false,
    };
    return { heroes, monsters, hero_count: heroes.length, monster_count: monsters.length };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();
