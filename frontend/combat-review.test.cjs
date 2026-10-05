"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

function node() {
  return {
    children: [], listeners: {}, dataset: {}, style: {}, hidden: false, disabled: false, open: false,
    textContent: "",
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = [...items]; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    showModal() { this.open = true; this.hidden = false; },
    close() { this.open = false; this.hidden = true; },
  };
}

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const rootHtml = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
for (const page of [html, rootHtml]) {
  assert.match(page, />Load Combat</);
  assert.match(page, /id="load-combat-button"/);
  assert.match(page, /id="combat-review"/);
  assert.match(page, /combat-review\.js/);
  assert.doesNotMatch(page, /id="instant-mode"/);
}

const elements = new Map([
  "load-combat-button", "combat-review", "combat-review-title", "combat-review-meta",
  "combat-review-log", "combat-review-close", "status", "lab-summary", "battle-log",
].map((id) => [id, node()]));
global.window = globalThis;
global.document = { getElementById: (id) => elements.get(id), createElement: node };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "combat-review.js"), "utf8"), { filename: "combat-review.js" });

const recipe = {
  id: "goblins", title: "1v2 · Barbarian vs two Goblins", seed: 1701,
  purpose: "Barbarian Rage.", ruleset: "2014",
};
const events = [
  { round_number: 1, event_type: "initiative", description: "Karnok rolls initiative." },
  { round_number: 1, event_type: "feature", feature_id: "rage", description: "Karnok enters Rage." },
];
const battle = { outcome: "heroes_win", rounds: 2, events };
const session = { battle, rolls: [{ sides: 20, value: 17 }], slotMap: { heroes: [0], monsters: [0, 1] } };
const rows = [];
window.IRON_PIT_BATTLE_LOG = { format: (event) => event.description };
window.IRON_PIT_BATTLEFIELD_VIEW = {
  eventRow(event) { const row = node(); row.textContent = event.description; rows.push(row); return row; },
  writeLog() {},
  showResult() {},
};
const replayed = [];
window.IRON_PIT_EXECUTION = {
  resolveReplay(selection, seed, slotMap) {
    replayed.push({ selection, seed, slotMap });
    return {
      battle, rolls: session.rolls, slotMap, started: false, complete: false, eventIndex: 0,
    };
  },
};
window.IRON_PIT_BATTLEFIELD_REPLAY = { bindBattle() {}, syncFinal() {} };
window.IRON_PIT_COMBAT_PRESETS = {
  selected: () => recipe,
  resolve: () => ({ heroes: [{ id: "barbarian" }], monsters: [{ id: "goblin" }, { id: "goblin" }] }),
};
const api = {
  state: { fighting: false, session: null, hasRun: false, catalog: { ruleset: "2014" } },
  matchup: () => ({
    error: null,
    heroes: { indexes: [0] },
    monsters: { indexes: [0, 1] },
    selection: { ruleset: "2014", hero_ids: ["barbarian-2014-l3"], monster_ids: ["2014-goblin", "2014-goblin"] },
  }),
  render() {},
  updateControls() {},
  clearResult() {},
  load() {},
  ensureRuleset: async () => {},
};

window.IRON_PIT_COMBAT_REVIEW.install(api);
assert.equal(elements.get("combat-review").hidden, true);
assert.equal(typeof elements.get("load-combat-button").listeners.click, "function");

(async () => {
  await elements.get("load-combat-button").listeners.click();
  assert.deepEqual(replayed, [{
    selection: api.matchup().selection,
    seed: 1701,
    slotMap: { heroes: [0], monsters: [0, 1] },
  }]);
  assert.equal(api.state.session.complete, true);
  assert.equal(api.state.session.eventIndex, events.length);
  assert.equal(api.state.hasRun, true);
  assert.equal(elements.get("combat-review").hidden, false);
  assert.equal(elements.get("combat-review").open, true);
  assert.equal(elements.get("combat-review-log").children.length, 2);
  assert.match(elements.get("combat-review-title").textContent, /Barbarian vs two Goblins/);
  assert.match(elements.get("combat-review-meta").textContent, /HEROES WIN/);
  assert.match(elements.get("combat-review-meta").textContent, /recorded seed 1701/);
  assert.match(elements.get("lab-summary").textContent, /Load Combat · recorded seed 1701/);
  await elements.get("combat-review-close").listeners.click();
  assert.equal(elements.get("combat-review").hidden, true);
  console.log("Load Combat review presents the recorded seed log without a live step session.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
