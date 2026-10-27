"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-monsters-2014.js"), "utf8"),
  { filename: "browser-monsters-2014.js" },
);

const catalog = JSON.parse(fs.readFileSync(
  path.join(__dirname, "..", "backend", "app", "content", "data", "srd_5_1_monsters_catalog.json"),
  "utf8",
));
const source = catalog.find((card) => card.id === "deep-gnome-svirfneblin");
assert.ok(source);
const nondetection = source.innate_spellcasting.spells.find((spell) => spell.id === "nondetection");
assert.deepEqual(nondetection, {
  id: "nondetection", name: "nondetection", usage: "at_will",
  uses_per_day: null, shared_pool: false, qualifier: "self only",
});

const template = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-deep-gnome-svirfneblin"];
assert.ok(template, "Deep Gnome must be admitted once all printed innate spells are classified");
assert.equal(template.timed_self_buff_actions.some((action) => action.id === "nondetection"), false);
assert.equal(template.spell_save_actions.some((action) => action.id === "nondetection"), false);
assert.equal(Object.hasOwn(template.resources, "nondetection"), false);

console.log("2014 innate Nondetection source preservation and arena-neutral browser parity passed.");
