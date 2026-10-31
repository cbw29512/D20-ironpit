"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

global.window = globalThis;
global.document = {
  createElement() {
    return {
      dataset: {}, className: "", textContent: "", title: "",
      setAttribute(name, value) { this[name] = value; },
      remove() {
        if (this.parent) this.parent.children = this.parent.children.filter((row) => row !== this);
      },
    };
  },
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battlefield-attachment-status.js"), "utf8"),
  { filename: "battlefield-attachment-status.js" });
const B = window.IRON_PIT_BATTLEFIELD_ATTACHMENT_STATUS;
const receipt = {
  operation: "attach", source_id: "monster:a", target_id: "hero:a",
  effect_id: "blood", source_name: "Blood Drain",
};
const rack = () => ({
  children: [],
  appendChild(child) { child.parent = this; this.children.push(child); },
});
const node = () => {
  const buffs = rack(), debuffs = rack(), concentration = { hidden: true };
  return {
    buffs, debuffs, flags: {},
    querySelector(selector) {
      return ({ ".card-buffs": buffs, ".card-debuffs": debuffs,
        ".card-concentration": concentration })[selector] || null;
    },
    classList: { toggle(name, value) { this[name] = value; } },
  };
};
const monster = node(), hero = node();
const nodes = new Map([["monster:a", monster], ["hero:a", hero]]);
let links = B.applyChanges(new Map(), [receipt]);
assert.equal(links.size, 1);
assert.deepEqual(B.labelsFor(links, "hero:a").debuffs.map((row) => row.text), ["ATTACHED"]);
assert.deepEqual(B.labelsFor(links, "monster:a").buffs.map((row) => row.text), ["FEEDING"]);
B.sync(nodes, links);
assert.equal(hero.debuffs.children[0].textContent, "ATTACHED");
assert.equal(monster.buffs.children[0].textContent, "FEEDING");
assert.match(hero.debuffs.children[0].title, /Blood Drain/);
assert.equal(hero.classList["has-debuff"], true);
assert.equal(monster.classList["has-buff"], true);
links = B.applyChanges(links, [{ ...receipt, operation: "detach" }]);
B.sync(nodes, links);
assert.equal(links.size, 0);
assert.equal(hero.debuffs.children.length, 0);
assert.equal(monster.buffs.children.length, 0);
assert.equal(hero.classList["has-debuff"], false);
// Source death also removes both projections without creating a Grappled effect.
links = B.applyChanges(new Map(), [receipt]);
assert.equal(B.removeCombatant(links, "monster:a").size, 0);
assert.equal(B.removeCombatant(links, "hero:a").size, 0);
assert.equal(B.fromSetup({ attachments: [receipt] }).size, 1);
assert.deepEqual(B.labelsFor(B.fromSetup({ attachments: [] }), "hero:a").debuffs, []);
console.log("Generic linked attachment battlefield badge tests passed.");
