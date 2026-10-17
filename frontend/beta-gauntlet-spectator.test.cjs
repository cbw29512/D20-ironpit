"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
class Element {
  constructor(tag = "div") {
    this.tagName = tag; this.children = []; this.textContent = ""; this.value = "0";
    this.scrollTop = 0; this.scrollHeight = 0; this.max = 0; this.className = "";
    this.classList = { toggle: (name, enabled) => { this[name] = enabled; } };
  }
  append(...nodes) { this.children.push(...nodes); this.scrollHeight = this.children.length; }
  replaceChildren(...nodes) { this.children = [...nodes]; this.scrollHeight = this.children.length; }
  get firstElementChild() { return this.children[0] || null; }
  remove() { this.removed = true; }
}
const elements = new Map();
global.document = {
  getElementById(id) { if (!elements.has(id)) elements.set(id, new Element()); return elements.get(id); },
  createElement(tag) { return new Element(tag); },
};
const root = __dirname;
const html = fs.readFileSync(path.join(root, "beta-gauntlet.html"), "utf8");
const runner = fs.readFileSync(path.join(root, "beta-gauntlet.js"), "utf8");
assert.match(html, /beta-gauntlet-spectator\.js/);
for (const id of ["arena-title", "arena-event", "arena-teams", "arena-log", "speed"]) {
  assert.match(html, new RegExp('id="' + id + '"'));
}
assert.match(runner, /IRON_PIT_BETA_SPECTATOR\.play/);
assert.doesNotMatch(runner, /IRON_PIT_BETA_BRIDGE/);

vm.runInThisContext(fs.readFileSync(path.join(root, "beta-gauntlet-spectator.js"), "utf8"),
  { filename: "beta-gauntlet-spectator.js" });
(async () => {
  const battle = { setup: { heroes: [
    { combatant_id: "h1", state: { template: { name: "Hero", max_hp: 10 }, current_hp: 10 } },
  ], monsters: [
    { combatant_id: "m1", state: { template: { name: "Monster", max_hp: 8 }, current_hp: 8 } },
  ] }, events: [
    { round_number: 1, event_type: "attack", description: "Hero hits Monster", target_id: "m1", hp_after: 5 },
  ] };
  await window.IRON_PIT_BETA_SPECTATOR.play(battle, { id: "test", ruleset: "2014" }, 17);
  assert.match(document.getElementById("arena-title").textContent, /2014.*17/);
  assert.equal(document.getElementById("arena-log").children.length, 1);
  assert.match(document.getElementById("arena-log").children[0].children[1].textContent, /Hero hits Monster/);
  assert.equal(document.getElementById("arena-teams").children.length, 2);
  assert.equal(document.getElementById("arena-teams").children[1].children[1].children[1].value, 5);
  console.log("Beta gauntlet spectator wiring and event playback passed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
