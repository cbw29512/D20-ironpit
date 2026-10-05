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

assert.throws(() => A.register([{ template_id: "broken", src: "x.webp" }]));
assert.throws(() => A.register([{
  template_id: "srd-test-art", src: "other.webp", license: "MIT", source: "test",
}]));

console.log("Combatant artwork registry regressions passed.");
