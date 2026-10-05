"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const frontend = path.join(__dirname, "..", "frontend");
const window = globalThis;
global.window = window;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(frontend, name), "utf8"), { filename: name });

for (const file of [
  "browser-heroes.js",
  "browser-monsters-generated.js",
  "browser-monsters-2014.js",
  "figure-profiles.js",
  "figure-visuals.js",
  "figure-portraits.js",
]) load(file);

const SHAPES = new Set([
  "humanoid", "brute", "quadruped", "bear", "hoofed", "reptile", "theropod", "snake",
  "crab", "bird", "bat", "pterosaur", "aquatic-reptile", "spider", "winged-insect",
  "centipede", "insect", "plant", "frog", "primate", "unknown",
]);

function uniqueHeroes(ruleset) {
  const seen = new Map();
  for (const hero of Object.values(window.IRON_PIT_BROWSER_HEROES || {})) {
    if (hero.ruleset !== ruleset) continue;
    const key = `${hero.ruleset}:${hero.class_id}`;
    const current = seen.get(key);
    if (!current || hero.level < current.level) seen.set(key, hero);
  }
  return [...seen.values()].sort((a, b) => a.class_id.localeCompare(b.class_id));
}

function inaccuracy(name, form, detail, key) {
  const n = String(name).toLowerCase();
  if (key === "unknown") return `Fallback silhouette is a question-mark, not the printed ${name}.`;
  if (/pegasus/.test(n) && key === "hoofed") return "Hoofed horse outline omits the printed wings.";
  if (/manticore/.test(n) && key === "quadruped") return "Generic quadruped omits humanoid head, wings, and tail spikes.";
  if (/^grick$/.test(n) && key === "snake") return "Snake coil is the wrong anatomy for a tentacled worm-like aberration.";
  if (/^xorn$/.test(n) && key === "brute") return "Generic brute omits the printed radial three-arm, three-leg body.";
  if (/earth elemental/.test(n) && key === "brute") return "Generic brute omits the printed walking-stone anatomy.";
  if (/lemure/.test(n) && key === "brute") return "Generic brute omits the printed molten, bloated devil anatomy.";
  if (/sahuagin|merfolk/.test(n) && key === "humanoid") return "Humanoid-with-legs silhouette omits the printed aquatic anatomy.";
  if (/triceratops/.test(n) && key === "reptile") return "Generic reptile omits the printed frill and three horns.";
  if (/ankylosaurus/.test(n) && key === "reptile") return "Generic reptile omits the printed club tail and armor plates.";
  if (/chimera/.test(n)) return "Generic outline omits the printed lion, goat, and dragon heads.";
  if (/minotaur/.test(n) && !/skeleton/.test(n)) return "Generic outline omits the printed bull head.";
  if (/satyr/.test(n)) return "Generic humanoid outline omits goat legs and horns.";
  return null;
}

function monsterRows(registry, ruleset) {
  return Object.values(registry || {})
    .filter((monster) => !ruleset || monster.ruleset === ruleset)
    .map((monster) => {
      const info = window.IRON_PIT_FIGURE_VISUALS.profile(monster);
      const key = window.IRON_PIT_FIGURE_PORTRAITS.keyFor(monster, info);
      const reason = inaccuracy(monster.name, info.form, info.detail, key);
      return {
        id: monster.id,
        name: monster.name,
        type: monster.creature_type || monster.archetype,
        cr: monster.challenge_rating,
        size: monster.size,
        ruleset: monster.ruleset,
        form: info.form,
        detail: info.detail,
        silhouette_key: key,
        status: reason ? "inaccurate" : "missing",
        reason,
      };
    })
    .sort((a, b) => a.name.localeCompare(b.name));
}

const heroes2014 = uniqueHeroes("2014");
const heroes2024 = uniqueHeroes("2024");
const monsters2014 = monsterRows(window.IRON_PIT_BROWSER_MONSTERS_2014, "2014");
const monsters2024 = monsterRows(window.IRON_PIT_BROWSER_MONSTERS, "2024");
const catalog2024 = JSON.parse(fs.readFileSync(path.join(frontend, "data", "srd_5_2_1_monsters.json"), "utf8"));

const report = {
  heroes_2014: heroes2014.map((hero) => ({
    portrait_id: `hero-2014-${hero.class_id}`,
    name: hero.name,
    class_name: hero.archetype,
    class_id: hero.class_id,
    level_1_template: hero.id,
    status: "missing",
  })),
  heroes_2024: heroes2024.map((hero) => ({
    portrait_id: `hero-2024-${hero.class_id}`,
    name: hero.name,
    class_name: hero.archetype,
    class_id: hero.class_id,
    level_1_template: hero.id,
    status: "missing",
  })),
  monsters_2014_certified: monsters2014,
  monsters_2024_certified: monsters2024,
  monsters_2024_catalog_count: catalog2024.length,
  counts: {
    unique_pregens_2014: heroes2014.length,
    unique_pregens_2024: heroes2024.length,
    certified_monsters_2014: monsters2014.length,
    certified_monsters_2024: monsters2024.length,
    catalog_monsters_2024: catalog2024.length,
    inaccurate_2014: monsters2014.filter((row) => row.status === "inaccurate").length,
    inaccurate_2024: monsters2024.filter((row) => row.status === "inaccurate").length,
  },
};

process.stdout.write(JSON.stringify(report, null, 2));
