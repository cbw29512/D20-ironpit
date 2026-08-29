(() => {
  "use strict";

  const CLASS_ORDER = [
    "barbarian", "bard", "cleric", "druid", "fighter", "monk",
    "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
  ];
  const LEVELS = Array.from({ length: 20 }, (_, index) => index + 1);

  function crNumber(value) {
    const text = String(value ?? "0").trim();
    if (!text.includes("/")) return Number(text) || 0;
    const [top, bottom] = text.split("/").map(Number);
    return bottom ? top / bottom : 0;
  }

  function classOptions(heroes) {
    const names = new Map(heroes.map((hero) => [hero.class_id, hero.class_name]));
    return CLASS_ORDER.map((id) => ({ id, name: names.get(id) || id }));
  }

  function heroBuilds(heroes, classId, level) {
    return heroes.filter((hero) => hero.class_id === classId && Number(hero.level) === Number(level));
  }

  function preferredHero(builds) {
    return builds.find((hero) => hero.coverage_status === "raw_ready" && hero.runnable_template_id) || builds[0] || null;
  }

  function sortedMonsters(monsters, crFilter = "all") {
    return monsters
      .filter((monster) => crFilter === "all" || String(monster.challenge_rating) === String(crFilter))
      .slice()
      .sort((a, b) => crNumber(a.challenge_rating) - crNumber(b.challenge_rating) || a.name.localeCompare(b.name));
  }

  function challengeRatings(monsters) {
    return [...new Set(monsters.map((monster) => String(monster.challenge_rating)))]
      .sort((a, b) => crNumber(a) - crNumber(b) || a.localeCompare(b));
  }

  function cardForSlot(heroes, slot) {
    return heroes.find((hero) => hero.id === slot.card_id) || null;
  }

  function normalizedSlot(heroes, slot = {}, patch = {}) {
    const classId = patch.class_id ?? slot.class_id ?? CLASS_ORDER[0];
    const level = Number(patch.level ?? slot.level ?? 1);
    const builds = heroBuilds(heroes, classId, level);
    const requestedId = patch.card_id ?? (slot.class_id === classId && Number(slot.level) === level ? slot.card_id : null);
    const chosen = builds.find((hero) => hero.id === requestedId) || preferredHero(builds);
    return { class_id: classId, level, card_id: chosen?.id || null };
  }

  window.IRON_PIT_ENCOUNTER_PICKER = {
    CLASS_ORDER, LEVELS, cardForSlot, challengeRatings, classOptions, crNumber,
    heroBuilds, normalizedSlot, preferredHero, sortedMonsters,
  };
})();
