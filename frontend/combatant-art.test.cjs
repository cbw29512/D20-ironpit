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
const goblinWarriorSrc = "assets/portraits/monsters/goblin-warrior.webp";
assert.equal(A.assetFor({ id: "2014-goblin", kind: "monster", name: "Goblin" }).src, goblinSrc);
assert.equal(A.assetFor({ id: "srd-goblin-warrior", kind: "monster", name: "Goblin Warrior" }).src, goblinWarriorSrc);
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-goblin-warrior", kind: "monster" }).src, goblinWarriorSrc);
assert.equal(A.assetFor({ id: "catalog-2014-goblin", kind: "monster" }).src, goblinSrc);
assert.notEqual(goblinSrc, goblinWarriorSrc);
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
assert.equal(A.assetFor({ id: "srd-guard-captain", kind: "monster" }).src, "assets/portraits/monsters/guard-captain.webp");
assert.notEqual(A.assetFor({ id: "srd-guard-captain", kind: "monster" }).src, A.assetFor({ id: "srd-guard", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-giant-boar", kind: "monster" }).src, "assets/portraits/monsters/giant-boar.webp");
assert.notEqual(A.assetFor({ id: "srd-giant-boar", kind: "monster" }).src, A.assetFor({ id: "srd-boar", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "2014-winter-wolf", kind: "monster" }).src, "assets/portraits/monsters/winter-wolf.webp");
assert.equal(A.assetFor({ id: "srd-spider", kind: "monster" }).src, "assets/portraits/monsters/spider.webp");
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
assert.equal(A.assetFor({ id: "srd-eagle", kind: "monster" }).src, "assets/portraits/monsters/eagle.webp");
assert.notEqual(A.assetFor({ id: "srd-eagle", kind: "monster" }).src, A.assetFor({ id: "srd-giant-eagle", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-owl", kind: "monster" }).src, "assets/portraits/monsters/owl.webp");
assert.equal(A.assetFor({ id: "2014-owl", kind: "monster" }).src, "assets/portraits/monsters/owl.webp");
assert.notEqual(A.assetFor({ id: "srd-owl", kind: "monster" }).src, A.assetFor({ id: "srd-giant-owl", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-owl", kind: "monster" }).src, A.assetFor({ id: "srd-owlbear", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-frog", kind: "monster" }).src, "assets/portraits/monsters/frog.webp");
assert.notEqual(
  A.assetFor({ id: "srd-frog", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-giant-frog", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "srd-elk", kind: "monster" }).src, "assets/portraits/monsters/elk.webp");
assert.notEqual(A.assetFor({ id: "srd-elk", kind: "monster" }).src, A.assetFor({ id: "srd-giant-elk", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-giant-badger", kind: "monster" }).src, A.assetFor({ id: "srd-badger", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-giant-bat", kind: "monster" }).src, A.assetFor({ id: "srd-bat", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-druid", kind: "monster" }).src, "assets/portraits/monsters/druid.webp");
assert.notEqual(A.assetFor({ id: "srd-druid", kind: "monster" }).src, A.assetFor({ kind: "character", class_id: "druid", ruleset: "2024" }).src);
assert.equal(A.assetFor({ id: "2014-fire-giant", kind: "monster" }).src, "assets/portraits/monsters/fire-giant.webp");
assert.notEqual(A.assetFor({ id: "2014-fire-giant", kind: "monster" }).src, A.assetFor({ id: "2014-frost-giant", kind: "monster" }).src);
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
assert.equal(A.assetFor({ id: "srd-goat", kind: "monster" }).src, "assets/portraits/monsters/goat.webp");
assert.equal(A.assetFor({ id: "2014-goat", kind: "monster" }).src, "assets/portraits/monsters/goat.webp");
assert.notEqual(A.assetFor({ id: "srd-goat", kind: "monster" }).src, A.assetFor({ id: "srd-giant-goat", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-giant-venomous-snake", kind: "monster" }).src, "assets/portraits/monsters/giant-venomous-snake.webp");
assert.equal(A.assetFor({ id: "2014-giant-poisonous-snake", kind: "monster" }).src, "assets/portraits/monsters/giant-poisonous-snake.webp");
assert.notEqual(A.assetFor({ id: "srd-giant-venomous-snake", kind: "monster" }).src, A.assetFor({ id: "2014-giant-poisonous-snake", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-giant-venomous-snake", kind: "monster" }).src, A.assetFor({ id: "srd-constrictor-snake", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-giant-venomous-snake", kind: "monster" }).src, A.assetFor({ id: "srd-flying-snake", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-giant-venomous-snake", kind: "monster" }).src, A.assetFor({ id: "srd-giant-constrictor-snake", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "2014-giant-sea-horse", kind: "monster" }).src, "assets/portraits/monsters/giant-sea-horse.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-giant-seahorse", kind: "monster" }).src, "assets/portraits/monsters/giant-seahorse.webp");
assert.notEqual(A.assetFor({ id: "2014-giant-sea-horse", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-giant-seahorse", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-green-dragon-wyrmling", kind: "monster" }).src, "assets/portraits/monsters/green-dragon-wyrmling.webp");
assert.notEqual(
  A.assetFor({ id: "srd-green-dragon-wyrmling", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-green-dragon", kind: "monster" }).src,
);
assert.notEqual(
  A.assetFor({ id: "srd-5.2.1-2024-monster-gold-dragon-wyrmling", kind: "monster" }).src,
  A.assetFor({ id: "srd-5.2.1-2024-monster-adult-gold-dragon", kind: "monster" }).src,
);
assert.equal(A.assetFor({ id: "srd-grick", kind: "monster" }).src, "assets/portraits/monsters/grick.webp");
assert.equal(A.assetFor({ id: "srd-grimlock", kind: "monster" }).src, "assets/portraits/monsters/grimlock.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-gnoll-warrior", kind: "monster" }).src, "assets/portraits/monsters/gnoll-warrior.webp");
assert.equal(A.assetFor({ id: "srd-gnoll", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-hawk", kind: "monster" }).src, "assets/portraits/monsters/hawk.webp");
assert.equal(A.assetFor({ id: "2014-hawk", kind: "monster" }).src, "assets/portraits/monsters/hawk.webp");
assert.notEqual(A.assetFor({ id: "srd-hawk", kind: "monster" }).src, A.assetFor({ id: "srd-blood-hawk", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "2014-kobold", kind: "monster" }).src, "assets/portraits/monsters/kobold.webp");
assert.equal(A.assetFor({ id: "srd-kobold-warrior", kind: "monster" }).src, "assets/portraits/monsters/kobold-warrior.webp");
assert.notEqual(A.assetFor({ id: "2014-kobold", kind: "monster" }).src, A.assetFor({ id: "srd-kobold-warrior", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-merfolk-skirmisher", kind: "monster" }).src, "assets/portraits/monsters/merfolk-skirmisher.webp");
assert.equal(A.assetFor({ id: "2014-merfolk", kind: "monster" }).src, "assets/portraits/monsters/merfolk.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-merfolk-skirmisher", kind: "monster" }).src, "assets/portraits/monsters/merfolk-skirmisher.webp");
assert.notEqual(A.assetFor({ id: "srd-merfolk-skirmisher", kind: "monster" }).src, A.assetFor({ id: "2014-merfolk", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-merfolk-skirmisher", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-merrow", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-hobgoblin-captain", kind: "monster" }).src, A.assetFor({ id: "srd-hobgoblin-warrior", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-hyena", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-giant-hyena", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-lizard", kind: "monster" }).src, A.assetFor({ id: "srd-giant-lizard", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-octopus", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-giant-octopus", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-hunter-shark", kind: "monster" }).src, A.assetFor({ id: "srd-giant-shark", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-ice-mephit", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-magma-mephit", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-ice-mephit", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-dust-mephit", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-hill-giant", kind: "monster" }).src, A.assetFor({ id: "2014-fire-giant", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-iron-golem", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-clay-golem", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-night-hag", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-green-hag", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-lemure", kind: "monster" }).src, "assets/portraits/monsters/lemure.webp");
assert.equal(A.assetFor({ id: "2014-lion", kind: "monster" }).src, "assets/portraits/monsters/lion.webp");
assert.equal(A.assetFor({ id: "2014-mammoth", kind: "monster" }).src, "assets/portraits/monsters/mammoth.webp");
assert.equal(A.assetFor({ id: "srd-noble", kind: "monster" }).src, "assets/portraits/monsters/noble.webp");
assert.equal(A.assetFor({ id: "srd-mind-flayer", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "2014-mind-flayer", kind: "monster" }), null);
assert.equal(A.assetFor({ id: "srd-rat", kind: "monster" }).src, "assets/portraits/monsters/rat.webp");
assert.equal(A.assetFor({ id: "2014-chimera", kind: "monster" }).src, "assets/portraits/monsters/chimera.webp");
assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-hydra", kind: "monster" }).src, "assets/portraits/monsters/hydra.webp");
assert.match(A.markup({ id: "2014-wyvern", kind: "monster", name: "Wyvern" }), /portrait-image-monster/);
assert.doesNotMatch(A.markup({ id: "2014-wyvern", kind: "monster", name: "Wyvern" }), /portrait-image-hero/);

assert.equal(A.assetFor({ id: "srd-5.2.1-2024-monster-ice-devil", kind: "monster" }).src, "assets/portraits/monsters/ice-devil.webp");
assert.equal(A.assetFor({ id: "ice-devil", kind: "monster" }).src, "assets/portraits/monsters/ice-devil.webp");
assert.equal(A.assetFor({ id: "2014-poisonous-snake", kind: "monster" }).src, "assets/portraits/monsters/poisonous-snake.webp");
assert.equal(A.assetFor({ id: "srd-venomous-snake", kind: "monster" }).src, "assets/portraits/monsters/venomous-snake.webp");
assert.notEqual(A.assetFor({ id: "2014-poisonous-snake", kind: "monster" }).src, A.assetFor({ id: "srd-venomous-snake", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "2014-quipper", kind: "monster" }).src, "assets/portraits/monsters/quipper.webp");
assert.equal(A.assetFor({ id: "srd-piranha", kind: "monster" }).src, "assets/portraits/monsters/piranha.webp");
assert.notEqual(A.assetFor({ id: "2014-quipper", kind: "monster" }).src, A.assetFor({ id: "srd-piranha", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-rat", kind: "monster" }).src, A.assetFor({ id: "srd-giant-rat", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-spider", kind: "monster" }).src, A.assetFor({ id: "srd-giant-spider", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-crab", kind: "monster" }).src, A.assetFor({ id: "srd-giant-crab", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-scorpion", kind: "monster" }).src, A.assetFor({ id: "srd-giant-scorpion", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-vulture", kind: "monster" }).src, A.assetFor({ id: "srd-giant-vulture", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-weasel", kind: "monster" }).src, A.assetFor({ id: "srd-giant-weasel", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-warhorse", kind: "monster" }).src, A.assetFor({ id: "srd-warhorse-skeleton", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-riding-horse", kind: "monster" }).src, A.assetFor({ id: "srd-draft-horse", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-winter-wolf", kind: "monster" }).src, A.assetFor({ id: "srd-wolf", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-winter-wolf", kind: "monster" }).src, A.assetFor({ id: "srd-dire-wolf", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-5.2.1-2024-monster-white-dragon-wyrmling", kind: "monster" }).src, A.assetFor({ id: "srd-young-white-dragon", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-young-blue-dragon", kind: "monster" }).src, A.assetFor({ id: "srd-5.2.1-2024-monster-adult-blue-dragon", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-swarm-of-quippers", kind: "monster" }).src, A.assetFor({ id: "srd-swarm-of-piranhas", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-swarm-of-poisonous-snakes", kind: "monster" }).src, A.assetFor({ id: "srd-swarm-of-venomous-snakes", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "2014-tribal-warrior", kind: "monster" }).src, A.assetFor({ id: "srd-warrior-infantry", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-warrior-infantry", kind: "monster" }).src, A.assetFor({ id: "srd-warrior-veteran", kind: "monster" }).src);
assert.notEqual(A.assetFor({ id: "srd-goblin-warrior", kind: "monster" }).src, A.assetFor({ id: "srd-goblin-boss", kind: "monster" }).src);
assert.equal(A.assetFor({ id: "srd-xorn", kind: "monster" }).src, "assets/portraits/monsters/xorn.webp");
assert.equal(A.assetFor({ id: "srd-sahuagin-warrior", kind: "monster" }).src, "assets/portraits/monsters/sahuagin-warrior.webp");

const monsterFiles = [
  "aboleth", "adult-black-dragon", "adult-blue-dragon", "adult-brass-dragon", "adult-bronze-dragon",
  "adult-copper-dragon", "adult-gold-dragon", "adult-green-dragon", "adult-red-dragon", "adult-silver-dragon",
  "adult-white-dragon", "air-elemental", "allosaurus", "ancient-black-dragon", "ancient-blue-dragon",
  "ancient-brass-dragon", "ancient-bronze-dragon", "ancient-copper-dragon", "ancient-gold-dragon", "ancient-green-dragon",
  "ancient-red-dragon", "ancient-silver-dragon", "ancient-white-dragon", "animated-armor", "animated-flying-sword",
  "animated-rug-of-smothering", "ankheg", "ankylosaurus", "ape", "archelon",
  "archmage", "assassin", "awakened-shrub", "awakened-tree", "axe-beak",
  "azer", "baboon", "badger", "balor", "bandit",
  "bandit-captain", "barbed-devil", "basilisk", "bat", "bearded-devil",
  "behir", "berserker", "black-bear", "black-dragon-wyrmling", "black-pudding",
  "blink-dog", "blood-hawk", "blue-dragon-wyrmling", "boar", "bone-devil",
  "brass-dragon-wyrmling", "bronze-dragon-wyrmling", "brown-bear", "bugbear-stalker", "bugbear-warrior",
  "bulette", "camel", "cat", "centaur", "chain-devil",
  "chimera", "chuul", "clay-golem", "cloaker", "cloud-giant",
  "cockatrice", "commoner", "constrictor-snake", "copper-dragon-wyrmling", "couatl",
  "crab", "crocodile", "cultist", "cultist-fanatic", "darkmantle",
  "death-dog", "deer", "deva", "dire-wolf", "djinni",
  "doppelganger", "draft-horse", "dragon-turtle", "dretch", "drider",
  "druid", "dryad", "dust-mephit", "eagle", "earth-elemental",
  "efreeti", "elephant", "elk", "erinyes", "ettercap",
  "ettin", "fire-elemental", "fire-giant", "flesh-golem", "flying-snake",
  "frog", "frost-giant", "gargoyle", "gelatinous-cube", "ghast",
  "ghost", "ghoul", "giant-ape", "giant-badger", "giant-bat",
  "giant-boar", "giant-centipede", "giant-constrictor-snake", "giant-crab", "giant-crocodile",
  "giant-eagle", "giant-elk", "giant-fire-beetle", "giant-frog", "giant-goat",
  "giant-hyena", "giant-lizard", "giant-octopus", "giant-owl", "giant-poisonous-snake",
  "giant-rat", "giant-scorpion", "giant-sea-horse", "giant-seahorse", "giant-shark",
  "giant-spider", "giant-toad", "giant-venomous-snake", "giant-vulture", "giant-wasp",
  "giant-weasel", "giant-wolf-spider", "gibbering-mouther", "glabrezu", "gladiator",
  "gnoll-warrior", "goat", "goblin", "goblin-boss", "goblin-minion",
  "goblin-warrior", "gold-dragon-wyrmling", "gorgon", "gray-ooze", "green-dragon-wyrmling",
  "green-hag", "grick", "griffon", "grimlock", "guard",
  "guard-captain", "guardian-naga", "half-dragon", "harpy", "hawk",
  "hell-hound", "hezrou", "hill-giant", "hippogriff", "hippopotamus",
  "hobgoblin-captain", "hobgoblin-warrior", "homunculus", "horned-devil", "hunter-shark",
  "hydra", "hyena", "ice-devil", "ice-mephit", "imp",
  "incubus", "invisible-stalker", "iron-golem", "jackal", "killer-whale",
  "knight", "kobold", "kobold-warrior", "kraken", "lamia",
  "lemure", "lich", "lion", "lizard", "mage",
  "magma-mephit", "magmin", "mammoth", "manticore", "marilith",
  "mastiff", "medusa", "merfolk", "merfolk-skirmisher", "merrow",
  "mimic", "minotaur", "minotaur-of-baphomet", "minotaur-skeleton", "mule",
  "mummy", "nalfeshnee", "night-hag", "nightmare", "noble",
  "ochre-jelly", "octopus", "ogre", "ogre-zombie", "oni",
  "otyugh", "owl", "owlbear", "panther", "pegasus",
  "phase-spider", "piranha", "pit-fiend", "plesiosaurus", "poisonous-snake",
  "polar-bear", "pony", "priest", "pteranodon", "quasit",
  "quipper", "rat", "raven", "red-dragon-wyrmling", "reef-shark",
  "rhinoceros", "riding-horse", "roc", "saber-toothed-tiger", "sahuagin-warrior",
  "satyr", "scorpion", "scout", "skeleton", "specter",
  "spider", "spy", "stirge", "swarm-of-bats", "swarm-of-crawling-claws",
  "swarm-of-insects", "swarm-of-piranhas", "swarm-of-poisonous-snakes", "swarm-of-quippers", "swarm-of-rats",
  "swarm-of-ravens", "swarm-of-venomous-snakes", "thug", "tiger", "tough",
  "tribal-warrior", "triceratops", "troll", "twig-blight", "tyrannosaurus-rex",
  "unicorn", "vampire-spawn", "venomous-snake", "violet-fungus", "vulture",
  "warhorse", "warhorse-skeleton", "warrior-infantry", "warrior-veteran", "water-elemental",
  "weasel", "white-dragon-wyrmling", "wight", "winter-wolf", "wolf",
  "worg", "wyvern", "xorn", "young-black-dragon", "young-blue-dragon",
  "young-green-dragon", "young-red-dragon", "young-white-dragon", "zombie"
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
