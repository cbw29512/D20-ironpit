"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (file) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file },
);

function element() {
  try {
    return {
      hidden: false, children: [], attributes: {}, textContent: "",
      setAttribute(name, value) { this.attributes[name] = value; },
      append(...items) { this.children.push(...items); },
      replaceChildren(...items) { this.children = [...items]; },
    };
  } catch (error) {
    console.error("Fake Wanted poster DOM construction failed.", error);
    throw error;
  }
}

const nodes = {
  "wanted-board": element(),
  "wanted-grid": element(),
  "wanted-count": element(),
};
global.document = {
  createElement: () => element(),
  getElementById: (id) => nodes[id] || null,
};

load("browser-heroes.js");
load("browser-monsters-2014.js");
load("browser-wanted-2014.js");
load("browser-wanted-posters.js");
load("browser-catalog.js");

(async () => {
  try {
    const catalog = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
    const blocked = catalog.monsters.filter((card) => card.coverage_status === "blocked");
    assert.equal(catalog.monsters.length, 327);
    assert.ok(blocked.length);
    assert.equal(blocked.length + catalog.monster_ready_count, 327);
    assert.ok(blocked.every((card) => card.runnable_template_id === null));
    window.IRON_PIT_WANTED_POSTERS.render(catalog);
    assert.equal(nodes["wanted-board"].hidden, false);
    assert.equal(nodes["wanted-grid"].children.length, blocked.length);
    assert.match(nodes["wanted-count"].textContent, new RegExp(`^${blocked.length} still wanted`));
    assert.ok(nodes["wanted-grid"].children.every((poster) =>
      poster.attributes["aria-label"].includes("not playable")));
    window.IRON_PIT_WANTED_POSTERS.render({ ruleset: "2024" });
    assert.equal(nodes["wanted-board"].hidden, true);

    // Simulate a later generator run where one formerly blocked source was admitted.
    const former = window.IRON_PIT_BROWSER_WANTED_2014[0];
    const sample = Object.values(window.IRON_PIT_BROWSER_MONSTERS_2014)[0];
    const oldWanted = window.IRON_PIT_BROWSER_WANTED_2014;
    assert.ok(former && sample);
    assert.ok(!window.IRON_PIT_BROWSER_MONSTERS_2014[former.id]);
    try {
      window.IRON_PIT_BROWSER_WANTED_2014 = oldWanted.filter((row) => row.id !== former.id);
      window.IRON_PIT_BROWSER_MONSTERS_2014[former.id] =
        { ...sample, id: former.id, name: former.name };
      const promoted = await window.IRON_PIT_BROWSER_CATALOG.buildCatalog("2014");
      const card = promoted.monsters.find((item) => item.id === `catalog-${former.id}`);
      assert.equal(card.coverage_status, "raw_ready");
      assert.equal(card.runnable_template_id, former.id);
      assert.equal(promoted.monster_ready_count, catalog.monster_ready_count + 1);
      window.IRON_PIT_WANTED_POSTERS.render(promoted);
      assert.equal(nodes["wanted-grid"].children.length, blocked.length - 1);
      assert.ok(nodes["wanted-grid"].children.every((poster) =>
        !poster.attributes["aria-label"].startsWith(`${former.name}:`)));
    } finally {
      delete window.IRON_PIT_BROWSER_MONSTERS_2014[former.id];
      window.IRON_PIT_BROWSER_WANTED_2014 = oldWanted;
    }
    console.log("2014 Wanted posters auto-retire when source admission advances.");
  } catch (error) {
    console.error("2014 Wanted board regression failed.", error);
    process.exitCode = 1;
  }
})();
