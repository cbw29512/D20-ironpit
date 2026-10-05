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
    setAttribute(name, value) { this.attributes = this.attributes || {}; this.attributes[name] = value; },
    showModal() { this.open = true; this.hidden = false; },
    close() { this.open = false; this.hidden = true; },
    querySelector() { return node(); },
    querySelectorAll() { return []; },
  };
}
const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const rootHtml = fs.readFileSync(path.join(__dirname, "..", "index.html"), "utf8");
for (const page of [html, rootHtml]) {
  const sections = [...page.matchAll(/<section\b[^>]*>/g)].map((match) => match[0]);
  const board = sections.findIndex((section) => /class="battlefield"/.test(section));
  assert.ok(board >= 0, "board must exist");
  assert.match(sections[board], /id="pit"/, "primary CTA must land on the live board");
  assert.match(sections[board + 1], /class="log-panel"/, "log must directly follow the board");
  assert.match(sections[board + 2], /class="preset-panel"/, "prebuilt fights must directly follow the log");
}
const elements = new Map([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => [match[1], node()]));
const el = (id) => { assert.ok(elements.has(id), `missing page element #${id}`); return elements.get(id); };
global.document = {
  getElementById: el, createElement: node, querySelector: () => null,
  querySelectorAll: (sel) => sel === "[data-preset]"
    ? el("combat-presets").children.filter((item) => item.dataset?.preset)
    : [],
};
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
  load("combat-preset-recipes.js"); load("combat-presets.js"); load("combat-review.js"); load("app.js");
  const presetButton = (id) => el("combat-presets").children.find((item) => item.dataset?.preset === id);
  for (let i = 0; i < 40 && !presetButton("goblins"); i += 1) await Promise.resolve();
  assert.ok(api, `production app must initialize: ${JSON.stringify(errors)}`);
  assert.equal(el("combat-presets").children.filter((item) => item.dataset?.preset).length, 25);
  await presetButton("goblins").listeners.click();
  assert.equal(api.state.heroSlots.filter(Boolean).length, 1);
  assert.equal(api.state.heroSlots[0].class_id, "barbarian");
  assert.equal(api.state.monsterSlots.filter(Boolean).length, 2);
  assert.ok(api.state.monsterSlots.filter(Boolean).every((card) => card.runnable_template_id === "2014-goblin"));
  assert.equal(api.state.session, null);
  assert.equal(window.IRON_PIT_COMBAT_PRESETS.selected().id, "goblins");
  assert.equal(el("load-combat-button").disabled, false);
  assert.match(el("status").textContent, /Rage/);
  const before = JSON.stringify(api.state.heroSlots);
  api.state.session = { complete: false };
  await presetButton("duel").listeners.click();
  assert.equal(JSON.stringify(api.state.heroSlots), before);
  api.state.session = null;
  await click("quick-test");
  const heroes = api.state.heroSlots.filter(Boolean), monsters = api.state.monsterSlots.filter(Boolean);
  assert.deepEqual(heroes.map((c) => c.runnable_template_id), ["karnok-stoneward-2014-l1", "seraphine-dawnshield-2014-l1"]);
  assert.deepEqual(monsters.map((c) => c.runnable_template_id), ["2014-skeleton", "2014-goblin"]);
  assert.ok(heroes.every((c) => c.kind === "character" && c.ruleset === "2014" && c.coverage_status === "raw_ready"));
  assert.ok(monsters.every((c) => c.kind === "monster" && c.ruleset === "2014" && c.coverage_status === "raw_ready"));
  assert.match(el("battle-log").children[0].textContent, /Karnok \+ Seraphine/);
  assert.equal(window.IRON_PIT_COMBAT_PRESETS.selected(), null);
  assert.equal(el("load-combat-button").disabled, true);
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
  const loadedCards = JSON.stringify([api.state.heroSlots, api.state.monsterSlots]);
  const resolvedBeforeReset = resolutions;
  await click("reset-fight");
  assert.equal(JSON.stringify([api.state.heroSlots, api.state.monsterSlots]), loadedCards);
  assert.equal(api.state.session, null); assert.equal(api.state.turboBatch, null); assert.equal(api.state.hasRun, false);
  assert.equal(el("result-panel").hidden, true); assert.equal(el("turbo-panel").hidden, true);
  assert.equal(el("rerun-button").disabled, true); assert.equal(el("fight-button").disabled, false);
  assert.equal(el("next-event-button").disabled, true); assert.equal(resolutions, resolvedBeforeReset);
  await click("step-fight-button"); await click("reset-fight");
  assert.equal(api.state.session, null, "Reset Fight discards a paused Step session");
  api.state.fighting = true; api.updateControls();
  assert.equal(el("reset-fight").disabled, true); assert.equal(el("reset-board").disabled, true);
  await click("reset-board");
  assert.equal(JSON.stringify([api.state.heroSlots, api.state.monsterSlots]), loadedCards);
  api.state.fighting = false; api.updateControls(); await click("reset-board");
  assert.ok([...api.state.heroSlots, ...api.state.monsterSlots].every((card) => card === null));
  assert.equal(api.state.heroSlots.length, 6); assert.equal(api.state.monsterSlots.length, 6);
  assert.equal(el("fight-button").disabled, true); assert.equal(el("step-fight-button").disabled, true); assert.equal(el("turbo-button").disabled, true);
  assert.match(el("status").textContent, /Board cleared/);
  await presetButton("goblins").listeners.click();
  assert.equal(api.state.heroSlots.filter(Boolean).length, 1); assert.equal(api.state.monsterSlots.filter(Boolean).length, 2);
  assert.equal(el("load-combat-button").disabled, false);
  const seeded = window.IRON_PIT_BROWSER_TURBO.runSeeded;
  let reviewSeeds = [];
  window.IRON_PIT_BROWSER_TURBO.runSeeded = (selection, seed) => {
    reviewSeeds.push(seed);
    return seeded(selection, seed);
  };
  await click("load-combat-button");
  window.IRON_PIT_BROWSER_TURBO.runSeeded = seeded;
  assert.deepEqual(reviewSeeds, [1701]);
  assert.equal(api.state.session.seed, 1701);
  assert.equal(api.state.session.complete, true);
  assert.equal(api.state.session.eventIndex, api.state.session.battle.events.length);
  assert.equal(el("combat-review").hidden, false);
  assert.equal(el("combat-review-log").children.length, api.state.session.battle.events.length);
  assert.equal(el("battle-log").children.length, api.state.session.battle.events.length);
  assert.match(el("combat-review-title").textContent, /Barbarian vs two Goblins/);
  assert.match(el("combat-review-meta").textContent, /recorded seed 1701/);
  assert.match(el("lab-summary").textContent, /Load Combat · recorded seed 1701/);
  await click("combat-review-close");
  assert.equal(el("combat-review").hidden, true);
  assert.equal(el("fight-button").disabled, false);
  assert.equal(el("step-fight-button").disabled, false);
  assert.equal(el("turbo-button").disabled, false);
  const liveBefore = resolutions;
  await click("fight-button");
  assert.equal(resolutions, liveBefore + 1);
  assert.equal(el("combat-review").hidden, true);
  assert.equal(api.state.session.complete, true);
  assert.equal(JSON.stringify(sample), original);
  await presetButton("2024-goblins").listeners.click();
  assert.equal(api.state.ruleset, "2024");
  assert.equal(api.state.heroSlots.filter(Boolean).length, 1);
  assert.equal(api.state.heroSlots[0].class_id, "barbarian");
  assert.equal(api.state.heroSlots[0].ruleset, "2024");
  assert.equal(api.state.monsterSlots.filter(Boolean).length, 2);
  assert.ok(api.state.monsterSlots.filter(Boolean).every((card) => card.runnable_template_id === "srd-goblin-warrior"));
  assert.match(el("status").textContent, /Rage/);
  assert.equal(errors.length, 0, JSON.stringify(errors));
  console.log("2014 sample + 2024 preset load + Load Combat review + actual UI log/result wiring: Fight, rerun, Step/Watch, Turbo and replay passed.");
})().catch((error) => { priorError(error); process.exitCode = 1; }).finally(() => { console.error = priorError; });
