"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });

// A presentation-only DOM fixture: actual catalog, engine, actions and log renderer run below.
function node() {
  return {
    children: [], listeners: {}, dataset: {}, style: {}, hidden: false, disabled: false, value: "",
    textContent: "", classList: { add() {}, remove() {}, toggle() {} },
    append(...items) { this.children.push(...items); },
    replaceChildren(...items) { this.children = [...items]; },
    addEventListener(name, handler) { this.listeners[name] = handler; },
    querySelector() { return node(); },
    querySelectorAll() { return []; },
  };
}
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const elements = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => [match[1], node()]));
const el = (id) => { assert.ok(elements.has(id), `missing page element #${id}`); return elements.get(id); };
global.document = { getElementById: el, createElement: node, querySelector: () => null, querySelectorAll: () => [] };
global.requestAnimationFrame = (callback) => callback();
load("browser-catalog.js"); load("encounter-picker.js"); load("battle-log-format.js"); load("battle-lab.js"); load("browser-audit.js");
load("battlefield-view.js"); load("browser-turbo.js"); load("turbo-view.js"); load("browser-execution.js"); load("battle-actions.js");
const view = window.IRON_PIT_BATTLEFIELD_VIEW;
const actions = window.IRON_PIT_BATTLE_ACTIONS;
let api = null;
const install = actions.install;
actions.install = (current) => { api = current; install(current); };
// Animation is deliberately absent in this fixture; live DOM animation gets a separate browser check.
window.IRON_PIT_BATTLEFIELD_REPLAY = { bindBattle() {}, eventStep: async () => {}, syncFinal() {} };
window.IRON_PIT_RULESET_UI = { ensureBundle: async () => {}, install() {}, syncDisabled() {}, update() {} };
window.IRON_PIT_BATTLEFIELD_PICKER = { bind() {} };
const rendered = [];
view.render = (state) => { rendered.push(structuredClone({ heroes: state.heroSlots, monsters: state.monsterSlots })); };
const errors = [];
const priorError = console.error;
console.error = (...args) => errors.push(args.map((arg) => arg instanceof Error ? arg.stack : arg));
const click = async (id) => { await el(id).listeners.click(); };

(async () => {
  load("combat-presets.js"); load("app.js");
  for (let i = 0; i < 10 && !api; i += 1) await Promise.resolve();
  assert.ok(api, `production app must initialize: ${JSON.stringify(errors)}`);
  assert.equal(el("combat-presets").children.length, 12);
  await el("combat-presets").children[1].listeners.click();
  assert.equal(api.state.heroSlots.filter(Boolean).length, 1);
  assert.equal(api.state.heroSlots[0].class_id, "barbarian");
  assert.equal(api.state.monsterSlots.filter(Boolean).length, 2);
  assert.ok(api.state.monsterSlots.filter(Boolean).every((card) => card.runnable_template_id === "2014-goblin"));
  assert.equal(api.state.session, null);
  assert.match(el("status").textContent, /Rage/);
  const before = JSON.stringify(api.state.heroSlots);
  api.state.session = { complete: false };
  await el("combat-presets").children[0].listeners.click();
  assert.equal(JSON.stringify(api.state.heroSlots), before);
  api.state.session = null;
  await click("quick-test");
  const heroes = api.state.heroSlots.filter(Boolean), monsters = api.state.monsterSlots.filter(Boolean);
  assert.deepEqual(heroes.map((c) => c.runnable_template_id), ["karnok-stoneward-2014-l1", "seraphine-dawnshield-2014-l1"]);
  assert.deepEqual(monsters.map((c) => c.runnable_template_id), ["2014-skeleton", "2014-goblin"]);
  assert.ok(heroes.every((c) => c.kind === "character" && c.ruleset === "2014" && c.coverage_status === "raw_ready"));
  assert.ok(monsters.every((c) => c.kind === "monster" && c.ruleset === "2014" && c.coverage_status === "raw_ready"));
  assert.match(el("battle-log").children[0].textContent, /Karnok \+ Seraphine/);
  assert.equal(el("fight-button").disabled, false);
  assert.ok(rendered.length >= 2);

  const sample = api.matchup().selection;
  const original = JSON.stringify(sample);
  let resolutions = 0;
  const resolve = window.IRON_PIT_BROWSER_ENGINE.runEncounter;
  window.IRON_PIT_BROWSER_ENGINE.runEncounter = (...args) => { resolutions += 1; return resolve(...args); };
  await click("fight-button");
  assert.equal(resolutions, 1);
  assert.ok(api.state.hasRun, JSON.stringify(errors));
  assert.equal(el("result-panel").hidden, false);
  assert.match(el("status").textContent, /^(HEROES WIN|MONSTERS WIN|DRAW)$/);
  const battle = api.state.session.battle;
  assert.equal(el("battle-log").children.length, battle.events.length);
  assert.ok(el("battle-log").children.every((row) => row.children[0].textContent));
  assert.equal(el("initiative-list").children.length, 4);
  assert.equal(el("survivors").children.length, 4);
  assert.equal(el("rerun-button").disabled, false);

  // Replacing a partial/full log must never duplicate rows or mutate engine evidence.
  const evidence = JSON.stringify(battle.events);
  view.writeLog({ events: battle.events.slice(0, 2) });
  assert.equal(el("battle-log").children.length, 2);
  view.writeLog(battle); view.writeLog(battle);
  assert.equal(el("battle-log").children.length, battle.events.length);
  assert.equal(JSON.stringify(battle.events), evidence);
  await click("rerun-button"); assert.equal(resolutions, 2);
  await click("step-fight-button"); assert.equal(resolutions, 3);
  const session = api.state.session;
  await click("next-event-button");
  assert.equal(session.eventIndex, 1); assert.equal(el("battle-log").children.length, 1);
  await click("watch-rest-button");
  assert.equal(api.state.session, session); assert.equal(resolutions, 3);
  assert.equal(session.complete, true); assert.equal(el("result-panel").hidden, false);
  assert.equal(el("battle-log").children.length, session.battle.events.length);

  el("turbo-count").value = "5";
  await click("turbo-button");
  assert.equal(api.state.turboBatch.valid_fights, 5); assert.equal(api.state.turboBatch.engine_errors, 0);
  assert.equal(el("turbo-panel").hidden, false);
  await click("turbo-replay-step-button");
  const replay = api.state.session;
  await click("next-event-button"); await click("watch-rest-button");
  assert.equal(api.state.session, replay); assert.equal(replay.complete, true);
  assert.match(el("lab-summary").textContent, /Replay seed/);
  assert.equal(el("battle-log").children.length, replay.battle.events.length);
  assert.equal(JSON.stringify(sample), original);
  assert.equal(errors.length, 0, JSON.stringify(errors));
  console.log("2014 sample + actual UI log/result wiring: Fight, rerun, Step/Watch, Turbo and replay passed.");
})().catch((error) => { priorError(error); process.exitCode = 1; }).finally(() => { console.error = priorError; });
