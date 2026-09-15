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
      for (let level = 1; level <= 10; level += 1) {
        const runtime = readyHeroes.get(`${classId}:${level}`) || null;
        cards.push({
          id: `hero-playtest-${classId}-l${level}`,
          name: heroName,
          class_id: classId,
          class_name: className,
          level,
          build_id: "canonical",
          build_name: "Certified Test Pregen",
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
      id: `catalog-${monster.id}`,
      name: monster.name,
      challenge_rating: monster.challenge_rating,
      monster_type: monster.creature_type || monster.archetype,
      coverage_status: "raw_ready",
      runnable_template_id: monster.id,
      blockers: [],
    }));
  }

  function mark2014Playtest(monsterCount) {
    document.title = "The Iron Pit — D&D 5e 2014 Playtest";
    const hero = document.querySelector("header.compact-hero");
    const rulesNotes = hero ? hero.querySelectorAll(".rules-note") : [];
    const eyebrow = hero ? hero.querySelector("p.eyebrow") : null;
    const intro = hero ? hero.querySelector("p:not(.eyebrow):not(.rules-note)") : null;
    if (eyebrow) eyebrow.textContent = "D&D 5e 2014 · SRD PLAYTEST";
    if (intro) intro.textContent = `${monsterCount} ledger-certified 2014 SRD monsters are enabled for live testing.`;
    if (rulesNotes[0]) rulesNotes[0].textContent = "Beta safety gate: uncertified 2014 monsters are hidden and cannot enter combat.";
    if (rulesNotes[1]) rulesNotes[1].textContent = "Hero side uses the currently integrated certified test pregens while dedicated 2014 pregen work continues.";
    const logNote = document.querySelector(".log-panel .rules-note");
    if (logNote) logNote.textContent = "D&D 5e 2014 · certified roster playtest · expandable rules audit";
  }

  async function buildMonsters() {
    const monsters = readyMonsterCards();
    if (!monsters.length) throw new Error("No certified 2014 monsters were exported for the playtest.");
    return monsters;
  }

  async function buildCatalog() {
    const heroes = buildHeroes(), monsters = await buildMonsters();
    mark2014Playtest(monsters.length);
    window.IRON_PIT_PLAYTEST = {
      ruleset: "2014",
      certified_monsters: monsters.length,
      hero_scope: "currently integrated certified test pregens, levels 1-10",
    };
    return { heroes, monsters, hero_count: heroes.length, monster_count: monsters.length };
  }

  window.IRON_PIT_BROWSER_CATALOG = { buildCatalog };
})();
