"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "combatant-art.js"), "utf8"), { filename: "combatant-art.js" });

const A = window.IRON_PIT_COMBATANT_ART;
const unknown = { id: "srd-unknown", name: "Unknown" };
assert.equal(A.assetFor(unknown), null);
assert.equal(A.markup(unknown), null);

A.register([{
  template_id: "srd-test-art",
  src: "assets/monsters/test.webp",
  alt: "Test monster",
  license: "CC-BY-4.0",
  source: "https://example.invalid/source",
}]);

const registered = { id: "srd-test-art", name: "Test Monster" };
assert.equal(A.assetFor(registered).src, "assets/monsters/test.webp");
assert.deepEqual(A.provenance(registered), {
  license: "CC-BY-4.0",
  source: "https://example.invalid/source",
});
assert.match(A.markup(registered), /class="portrait-image portrait-image-monster"/);
assert.match(A.markup(registered), /sizes="/);
assert.match(A.markup(registered), /onerror=/);

const level1 = { id: "karnok-stoneward-2014-l1", kind: "character", class_id: "fighter", ruleset: "2014", name: "Karnok Stoneward" };
const level20 = { id: "karnok-stoneward-2014-l20", kind: "character", class_id: "fighter", ruleset: "2014", name: "Karnok Stoneward" };
const karnok2024 = { id: "karnok-stoneward-l1", kind: "character", class_id: "fighter", ruleset: "2024", name: "Karnok Stoneward" };
assert.equal(A.portraitId(level1), "hero-2014-fighter");
assert.equal(A.portraitId(level20), "hero-2014-fighter");
assert.equal(A.assetFor(level1).src, A.assetFor(level20).src);
assert.equal(A.assetFor(level1).src, "assets/portraits/heroes/hero-2014-fighter.webp");
assert.equal(A.assetFor(karnok2024).src, "assets/portraits/heroes/hero-2024-fighter.webp");
assert.notEqual(A.assetFor(level1).src, A.assetFor(karnok2024).src);
assert.match(A.markup(level1), /portrait-image-hero/);
assert.doesNotMatch(A.markup(level1), /portrait-image-monster/);
assert.match(A.markup(level1), /art-broken/, "Broken portraits must reveal the fallback glyph.");
const classes = ["barbarian","bard","cleric","druid","fighter","monk","paladin","ranger","rogue","sorcerer","warlock","wizard"];
for (const ruleset of ["2014", "2024"]) {
  for (const classId of classes) {
    const src = `assets/portraits/heroes/hero-${ruleset}-${classId}.webp`;
    const hero = { kind: "character", class_id: classId, ruleset, name: classId };
    assert.equal(A.assetFor(hero).src, src);
    assert.ok(fs.existsSync(path.join(__dirname, src.replace(/^assets/, "assets"))));
  }
}
const css = fs.readFileSync(path.join(__dirname, "figure-portraits.css"), "utf8");
assert.match(css, /\.fighter-portrait\.has-art[^{]*\.portrait-svg/, "Legacy SVG layer must hide when a portrait asset exists.");
assert.match(css, /\.picker-portrait-frame\{position:relative\}|\.picker-portrait-frame\{[^}]*position:relative/, "Picker portrait images must stay inside the frame.");
assert.match(css, /\.portrait-image-monster\{[^}]*object-fit:cover/, "Monster rasters must fill the shadow-box without stretching.");

const goblinSrc = "assets/portraits/monsters/goblin.webp";
assert.equal(A.assetFor({ id: "2014-goblin", kind: "monster", name: "Goblin" }).src, goblinSrc);
assert.equal(A.assetFor({ id: "srd-goblin-warrior", kind: "monster", name: "Goblin Warrior" }).src, goblinSrc);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-goblin-warrior", kind: "monster" }).src, goblinSrc);
assert.equal(A.assetFor({ id: "catalog-2014-goblin", kind: "monster" }).src, goblinSrc);
assert.equal(A.assetFor({ id: "srd-brown-bear", kind: "monster" }).src, A.assetFor({ id: "2014-brown-bear" }).src);
assert.equal(A.assetFor({ id: "srd-manticore", kind: "monster" }).src, "assets/portraits/monsters/manticore.webp");
assert.equal(A.assetFor({ id: "srd-hippopotamus", kind: "monster" }).src, "assets/portraits/monsters/hippopotamus.webp");
assert.equal(A.assetFor({ id: "2014-minotaur", kind: "monster" }).src, "assets/portraits/monsters/minotaur.webp");
assert.equal(A.assetFor({ id: "srd-minotaur-skeleton", kind: "monster" }).src, "assets/portraits/monsters/minotaur-skeleton.webp");
assert.equal(A.assetFor({ id: "2014-minotaur-skeleton", kind: "monster" }).src, "assets/portraits/monsters/minotaur-skeleton.webp");
assert.equal(A.assetFor({ id: "srd-goblin-minion", kind: "monster" }).src, "assets/portraits/monsters/goblin-minion.webp");
assert.equal(A.assetFor({ id: "srd-goblin-boss", kind: "monster" }).src, "assets/portraits/monsters/goblin-boss.webp");
assert.equal(A.assetFor({ id: "srd-hobgoblin-warrior", kind: "monster" }).src, "assets/portraits/monsters/hobgoblin-warrior.webp");
assert.equal(A.assetFor({ id: "srd-ogre-zombie", kind: "monster" }).src, "assets/portraits/monsters/ogre-zombie.webp");
assert.equal(A.assetFor({ id: "srd-giant-crocodile", kind: "monster" }).src, "assets/portraits/monsters/giant-crocodile.webp");
assert.equal(A.assetFor({ id: "2014-wolf", kind: "monster" }).src, "assets/portraits/monsters/wolf.webp");
assert.equal(A.assetFor({ id: "srd-wolf", kind: "monster" }).src, "assets/portraits/monsters/wolf.webp");
assert.equal(A.assetFor({ id: "2014-troll", kind: "monster" }).src, "assets/portraits/monsters/troll.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-harpy", kind: "monster" }).src, "assets/portraits/monsters/harpy.webp");
assert.notEqual(A.assetFor({ id: "srd-goblin-minion", kind: "monster" }).src, goblinSrc);
assert.notEqual(A.assetFor({ id: "srd-goblin-boss", kind: "monster" }).src, goblinSrc);
assert.notEqual(A.assetFor({ id: "srd-minotaur-skeleton", kind: "monster" }).src, "assets/portraits/monsters/minotaur.webp");
assert.notEqual(A.assetFor({ id: "srd-minotaur-of-baphomet", kind: "monster" }).src, "assets/portraits/monsters/minotaur.webp");
assert.notEqual(A.assetFor({ id: "srd-giant-crocodile", kind: "monster" }).src, "assets/portraits/monsters/crocodile.webp");
assert.notEqual(A.assetFor({ id: "srd-ogre-zombie", kind: "monster" }).src, "assets/portraits/monsters/ogre.webp");
assert.notEqual(A.assetFor({ id: "srd-wolf", kind: "monster" }).src, "assets/portraits/monsters/dire-wolf.webp");
assert.equal(A.assetFor({ id: "srd-orc", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-orc", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-beholder", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-beholder", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-beholder", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-animated-armor", kind: "monster" }).src, "assets/portraits/monsters/animated-armor.webp");
assert.equal(A.assetFor({ id: "srd-earth-elemental", kind: "monster" }).src, "assets/portraits/monsters/earth-elemental.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-azer-sentinel", kind: "monster" }).src, "assets/portraits/monsters/azer.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-centaur-trooper", kind: "monster" }).src, "assets/portraits/monsters/centaur.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-adult-red-dragon", kind: "monster" }).src, "assets/portraits/monsters/adult-red-dragon.webp");
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-red-dragon", kind: "monster" }).src,
  A.assetFor({ id: "srd-young-red-dragon", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-red-dragon", kind: "monster" }).src,
  A.assetFor({ id: "srd-red-dragon-wyrmling", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-black-dragon", kind: "monster" }).src,
  A.assetFor({ id: "srd-young-black-dragon", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-ancient-red-dragon", kind: "monster" }).src, "assets/portraits/monsters/ancient-red-dragon.webp");
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-ancient-red-dragon", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-red-dragon", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-air-elemental", kind: "monster" }).src,
  A.assetFor({ id: "srd-earth-elemental", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-fire-elemental", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-water-elemental", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "srd-guard-captain", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-giant-boar", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-winter-wolf", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-spider", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-ape", kind: "monster" }).src, "assets/portraits/monsters/ape.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-ape", kind: "monster" }).src, "assets/portraits/monsters/ape.webp");
assert.equal(A.assetFor({ id: "2014-giant-ape", kind: "monster" }).src, "assets/portraits/monsters/giant-ape.webp");
assert.notEqual(A.assetFor({ id: "2014-ape", kind: "monster" }).src, A.assetFor({ id: "2014-giant-ape", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-constrictor-snake", kind: "monster" }).src, "assets/portraits/monsters/constrictor-snake.webp");
assert.notEqual(A.assetFor({ id: "srd-constrictor-snake", kind: "monster" }).src, A.assetFor({ id: "srd-giant-constrictor-snake", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-flying-snake", kind: "monster" }).src, "assets/portraits/monsters/flying-snake.webp");
assert.notEqual(A.assetFor({ id: "srd-flying-snake", kind: "monster" }).src, A.assetFor({ id: "srd-constrictor-snake", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "2014-allosaurus", kind: "monster" }).src, "assets/portraits/monsters/allosaurus.webp");
assert.equal(A.assetFor({ id: "srd-allosaurus", kind: "monster" }).src, "assets/portraits/monsters/allosaurus.webp");
assert.equal(A.assetFor({ id: "2014-ankylosaurus", kind: "monster" }).src, "assets/portraits/monsters/ankylosaurus.webp");
assert.equal(A.assetFor({ id: "srd-gargoyle", kind: "monster" }).src, "assets/portraits/monsters/gargoyle.webp");
assert.equal(A.assetFor({ id: "srd-giant-eagle", kind: "monster" }).src, "assets/portraits/monsters/giant-eagle.webp");
assert.equal(A.assetFor({ id: "srd-giant-owl", kind: "monster" }).src, "assets/portraits/monsters/giant-owl.webp");
assert.equal(A.assetFor({ id: "srd-eagle", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-owl", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-drow", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-duergar", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-displacer-beast", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-flumph", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-froghemoth", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-galeb-duhr", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-giant-wolf-spider", kind: "monster" }).src, "assets/portraits/monsters/giant-wolf-spider.webp");
assert.notEqual(A.assetFor({ id: "srd-giant-wolf-spider", kind: "monster" }).src, A.assetFor({ id: "srd-giant-spider", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-bandit", kind: "monster" }).src, "assets/portraits/monsters/bandit.webp");
assert.equal(A.assetFor({ id: "srd-bandit-captain", kind: "monster" }).src, "assets/portraits/monsters/bandit-captain.webp");
assert.notEqual(A.assetFor({ id: "srd-bandit", kind: "monster" }).src, A.assetFor({ id: "srd-bandit-captain", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-cultist", kind: "monster" }).src, "assets/portraits/monsters/cultist.webp");
assert.equal(A.assetFor({ id: "srd-cultist-fanatic", kind: "monster" }).src, "assets/portraits/monsters/cultist-fanatic.webp");
assert.notEqual(A.assetFor({ id: "srd-cultist", kind: "monster" }).src, A.assetFor({ id: "srd-cultist-fanatic", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-animated-flying-sword", kind: "monster" }).src, "assets/portraits/monsters/animated-flying-sword.webp");
assert.notEqual(A.assetFor({ id: "srd-animated-armor", kind: "monster" }).src, A.assetFor({ id: "srd-animated-flying-sword", kind: "monster" }).src);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-animated-rug-of-smothering", kind: "monster" }).src,
  A.assetFor({ id: "srd-animated-armor", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-bugbear-stalker", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-bugbear-warrior", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "2014-black-dragon-wyrmling", kind: "monster" }).src, "assets/portraits/monsters/black-dragon-wyrmling.webp");
assert.notEqual(
  A.assetFor({ id: "srd-black-dragon-wyrmling", kind: "monster" }).src,
  A.assetFor({ id: "srd-young-black-dragon", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-ancient-brass-dragon", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-brass-dragon", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-brass-dragon-wyrmling", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-ancient-brass-dragon", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-priest", kind: "monster" }).src, "assets/portraits/monsters/priest.webp");
assert.equal(A.assetFor({ id: "srd-priest-acolyte", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-mage", kind: "monster" }).src, "assets/portraits/monsters/mage.webp");
assert.equal(A.assetFor({ id: "srd-archmage", kind: "monster" }).src, "assets/portraits/monsters/archmage.webp");
assert.notEqual(A.assetFor({ id: "srd-archmage", kind: "monster" }).src, A.assetFor({ id: "srd-mage", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-vampire-spawn", kind: "monster" }).src, "assets/portraits/monsters/vampire-spawn.webp");
assert.equal(A.assetFor({ id: "srd-vampire", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-pegasus", kind: "monster" }).src, "assets/portraits/monsters/pegasus.webp");
assert.notEqual(A.assetFor({ id: "srd-pegasus", kind: "monster" }).src, A.assetFor({ id: "2014-unicorn", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-medusa", kind: "monster" }).src, "assets/portraits/monsters/medusa.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-gorgon", kind: "monster" }).src, "assets/portraits/monsters/gorgon.webp");
assert.notEqual(A.assetFor({ id: "srd-medusa", kind: "monster" }).src, A.assetFor({ id: "srd-gorgon", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-hawk", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-rat", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-chimera", kind: "monster" }).src, "assets/portraits/monsters/chimera.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-hydra", kind: "monster" }).src, "assets/portraits/monsters/hydra.webp");
assert.match(A.markup({ id: "2014-wyvern", kind: "monster", name: "Wyvern" }), /portrait-image-monster/);
assert.doesNotMatch(A.markup({ id: "2014-wyvern", kind: "monster", name: "Wyvern" }), /portrait-image-hero/);

const monsterFiles = [
  "aboleth", "adult-black-dragon", "adult-blue-dragon", "adult-brass-dragon",
  "adult-bronze-dragon", "adult-copper-dragon", "adult-gold-dragon",
  "adult-green-dragon", "adult-red-dragon", "adult-silver-dragon",
  "adult-white-dragon", "air-elemental", "allosaurus", "ancient-black-dragon",
  "ancient-blue-dragon", "ancient-brass-dragon", "ancient-bronze-dragon",
  "ancient-copper-dragon", "ancient-gold-dragon", "ancient-green-dragon",
  "ancient-red-dragon", "ancient-silver-dragon", "ancient-white-dragon",
  "animated-armor", "animated-flying-sword", "animated-rug-of-smothering",
  "ankheg", "ankylosaurus", "ape", "archelon", "archmage", "assassin",
  "awakened-shrub", "awakened-tree", "axe-beak", "azer", "baboon", "badger",
  "balor", "bandit", "bandit-captain", "barbed-devil", "basilisk", "bat",
  "bearded-devil", "behir", "berserker", "black-bear", "black-dragon-wyrmling",
  "black-pudding", "blink-dog", "blood-hawk", "blue-dragon-wyrmling", "boar",
  "bone-devil", "brass-dragon-wyrmling", "bronze-dragon-wyrmling", "brown-bear",
  "bugbear-stalker", "bugbear-warrior", "bulette", "camel", "cat", "centaur",
  "chain-devil", "chimera", "chuul", "clay-golem", "cloaker", "cloud-giant",
  "cockatrice", "commoner", "constrictor-snake", "copper-dragon-wyrmling",
  "couatl", "crocodile", "cultist", "cultist-fanatic", "darkmantle",
  "death-dog", "deer", "deva", "dire-wolf", "dragon-turtle", "dryad",
  "earth-elemental", "elephant", "ettin", "fire-elemental", "flying-snake",
  "gargoyle", "gelatinous-cube", "ghost", "ghoul", "giant-ape",
  "giant-constrictor-snake", "giant-crocodile", "giant-eagle", "giant-owl",
  "giant-rat", "giant-scorpion", "giant-spider", "giant-wolf-spider", "goblin",
  "goblin-boss", "goblin-minion", "gorgon", "griffon", "guard", "harpy",
  "hell-hound", "hippogriff", "hippopotamus", "hobgoblin-warrior", "hydra",
  "imp", "knight", "mage", "manticore", "medusa", "minotaur",
  "minotaur-of-baphomet", "minotaur-skeleton", "ogre", "ogre-zombie",
  "owlbear", "pegasus", "pit-fiend", "priest", "quasit",
  "red-dragon-wyrmling", "roc", "skeleton", "specter", "stirge", "triceratops",
  "troll", "tyrannosaurus-rex", "unicorn", "vampire-spawn",
  "warhorse-skeleton", "water-elemental", "wight", "wolf", "worg", "wyvern",
  "young-black-dragon", "young-red-dragon", "zombie",
];
for (const fileId of monsterFiles) {
  const rel = `assets/portraits/monsters/${fileId}.webp`;
  const abs = path.join(__dirname, rel);
  assert.ok(fs.existsSync(abs), rel);
  assert.ok(fs.statSync(abs).size <= 100000, `${rel} must stay at or under 100KB`);
  assert.equal(A.assetFor({ id: fileId, kind: "monster" }).src, rel);
}

assert.throws(() => A.register([{ template_id: "broken", src: "x.webp" }]));
assert.throws(() => A.register([{
  template_id: "srd-test-art", src: "other.webp", license: "MIT", source: "test",
}]));

console.log("Combatant artwork registry regressions passed.");
