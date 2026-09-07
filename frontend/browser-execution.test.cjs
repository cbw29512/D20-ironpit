"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-execution.js");

const events = [
  { round_number: 1, event_type: "initiative", actor_id: "hero" },
  { round_number: 1, event_type: "attack", actor_id: "hero", target_id: "monster" },
  { round_number: 1, event_type: "victory", actor_id: "arena" },
];
const battle = { battle_id: "test", outcome: "heroes_win", rounds: 1, events };
const selection = { hero_ids: ["hero"], monster_ids: ["monster"] };
const slots = { heroes: [0], monsters: [0] };
let engineCalls = 0, seededCalls = 0, batchCalls = 0, bindCalls = 0, syncCalls = 0;
const applied = [];
const history = [];

window.IRON_PIT_DICE = {
  clearHistory: () => { history.length = 0; },
  getHistory: () => structuredClone(history),
  roll: (sides) => { const value = sides === 20 ? 17 : 4; history.push({ sides, value }); return value; },
};
window.IRON_PIT_BATTLE_LAB = { diagnosticId: (_heroes, _monsters, rolls) => `diag-${rolls.length}` };
window.IRON_PIT_BATTLEFIELD_REPLAY = {
  bindBattle: (current, slotMap) => { bindCalls += 1; assert.equal(current, battle); assert.deepEqual(slotMap, slots); },
  eventStep: async (event) => { applied.push(event); },
  syncFinal: (current) => { syncCalls += 1; assert.equal(current, battle); },
};
window.IRON_PIT_BROWSER_ENGINE = {
  runEncounter: (current) => {
    engineCalls += 1; assert.deepEqual(current, selection);
    window.IRON_PIT_DICE.roll(20); window.IRON_PIT_DICE.roll(6); return battle;
  },
};
window.IRON_PIT_BROWSER_TURBO = {
  runSeeded: (current, seed) => {
    seededCalls += 1; assert.deepEqual(current, selection);
    return { battle, seed, rolls: [{ sides: 20, value: 12 }], diagnostic_id: "seeded-diag" };
  },
  runBatch: async (current, fights, batchSeed, onProgress) => {
    batchCalls += 1; assert.deepEqual(current, selection); onProgress?.(fights, fights);
    return { requested_fights: fights, batch_seed: batchSeed ?? 1 };
  },
};

(async () => {
  const execution = window.IRON_PIT_EXECUTION;
  const session = execution.resolveLive(selection, slots);
  assert.equal(engineCalls, 1, "live execution must resolve the canonical engine once");
  assert.equal(session.rolls.length, 2);
  assert.equal(session.diagnosticId, "diag-2");
  assert.deepEqual(session.state(), { mode: "live", event_index: 0, event_count: 3, started: false, complete: false, seed: null });

  await session.begin();
  assert.equal(bindCalls, 1); assert.equal(engineCalls, 1);
  await session.step();
  assert.deepEqual(applied, [events[0]]); assert.equal(engineCalls, 1, "stepping must not rerun combat");
  assert.equal(session.state().event_index, 1); assert.equal(session.state().complete, false);

  await session.watch();
  assert.deepEqual(applied, events, "watch-rest must continue the same event stream");
  assert.equal(engineCalls, 1, "switching Step to Watch must never reroll or rerun combat");
  assert.equal(syncCalls, 1); assert.equal(session.state().complete, true);

  const replay = execution.resolveReplay(selection, 424242, slots);
  assert.equal(seededCalls, 1); assert.equal(replay.mode, "replay"); assert.equal(replay.seed, 424242);
  await replay.step(); assert.equal(engineCalls, 1, "replay must use its preserved seeded result, not live resolution");

  let progress = null;
  const batch = await execution.runTurbo(selection, 100, 77, (done, total) => { progress = [done, total]; });
  assert.equal(batchCalls, 1); assert.equal(batch.requested_fights, 100); assert.deepEqual(progress, [100, 100]);

  console.log("Universal Step/Watch/Replay/Turbo execution regressions passed.");
})().catch((error) => { console.error(error); process.exitCode = 1; });
