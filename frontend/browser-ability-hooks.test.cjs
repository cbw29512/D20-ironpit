"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-ability-hooks.js"), "utf8"), { filename: "browser-ability-hooks.js" });
const H = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
const member = (ruleset = "2024") => ({ combatant_id: `test-${ruleset}`, state: { template: { ruleset } } });
const event = (id, sequence) => ({ event_type: "feature", feature_id: id, sequence });
const result = (id, sequence, claimed = false) => ({ events: [event(id, sequence)], sequence: sequence + 1, claimed });

assert.deepEqual(H.knownPhases(), ["turnStart", "bonusActionWindow", "mainAction", "turnFinalize", "turnEndLifecycle", "beforeAttackRoll", "onHit", "onMiss"]);
assert.throws(() => H.registerAbility("onHti", { id: "typo", rulesets: ["2024"], resolve: () => null }), /Unknown ability-hook phase/);
assert.throws(() => H.registerAbility(H.PHASES.ON_HIT, { id: "missing-ruleset", resolve: () => null }), /must declare one or more rulesets/);
assert.throws(() => H.registerAbility(H.PHASES.ON_HIT, { id: "bad-ruleset", rulesets: ["2025"], resolve: () => null }), /unsupported ruleset/);
assert.throws(() => H.registerAbility(H.PHASES.ON_HIT, { id: "bad-priority", priority: NaN, rulesets: ["2024"], resolve: () => null }), /finite number/);

H._resetForTests();
const order = [];
for (const [id, priority] of [["late", 20], ["first-tie", 10], ["second-tie", 10]]) {
  H.registerAbility(H.PHASES.ON_HIT, { id, priority, rulesets: ["2024"], resolve: ({ sequence }) => { order.push(id); return result(id, sequence); } });
}
const ordered = H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member(), events: [] });
assert.deepEqual(order, ["first-tie", "second-tie", "late"]);
assert.equal(ordered.sequence, 4);
assert.deepEqual(ordered.events.map((item) => item.feature_id), ["first-tie", "second-tie", "late"]);
assert.equal(ordered.claimed, false);

H._resetForTests();
H.registerAbility(H.PHASES.ON_HIT, { id: "edition-2014", rulesets: ["2014"], resolve: ({ sequence }) => result("2014", sequence) });
H.registerAbility(H.PHASES.ON_HIT, { id: "edition-2024", rulesets: ["2024"], resolve: ({ sequence }) => result("2024", sequence) });
assert.deepEqual(H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member("2014") }).events.map((item) => item.feature_id), ["2014"]);
assert.deepEqual(H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member("2024") }).events.map((item) => item.feature_id), ["2024"]);

H._resetForTests();
const exclusiveOrder = [];
H.registerAbility(H.PHASES.BONUS_ACTION_WINDOW, { id: "observer", priority: 1, rulesets: ["2024"], resolve: ({ sequence }) => { exclusiveOrder.push("observer"); return result("observer", sequence, false); } });
H.registerAbility(H.PHASES.BONUS_ACTION_WINDOW, { id: "declines", priority: 2, rulesets: ["2024"], resolve: () => { exclusiveOrder.push("declines"); return { events: [], sequence: 2, claimed: false }; } });
H.registerAbility(H.PHASES.BONUS_ACTION_WINDOW, { id: "winner", priority: 3, rulesets: ["2024"], resolve: ({ sequence }) => { exclusiveOrder.push("winner"); return result("winner", sequence, true); } });
H.registerAbility(H.PHASES.BONUS_ACTION_WINDOW, { id: "must-not-run", priority: 4, rulesets: ["2024"], resolve: ({ sequence }) => { exclusiveOrder.push("must-not-run"); return result("bad", sequence, true); } });
const exclusive = H.runPhase(H.PHASES.BONUS_ACTION_WINDOW, { sequence: 1, member: member(), events: [] });
assert.deepEqual(exclusiveOrder, ["observer", "declines", "winner"], "only the hook that actually claims the exclusive phase may stop later hooks");
assert.equal(exclusive.claimed, true);
assert.deepEqual(exclusive.events.map((item) => item.feature_id), ["observer", "winner"]);

H._resetForTests();
let gated = 0;
H.registerAbility(H.PHASES.ON_MISS, { id: "gated", rulesets: ["2014", "2024"], appliesTo: () => false, resolve: () => { gated += 1; return null; } });
H.runPhase(H.PHASES.ON_MISS, { sequence: 1, member: member(), events: [] });
assert.equal(gated, 0);

H._resetForTests();
H.registerAbility(H.PHASES.ON_HIT, { id: "duplicate", rulesets: ["2024"], resolve: () => null });
assert.throws(() => H.registerAbility(H.PHASES.ON_HIT, { id: "duplicate", rulesets: ["2024"], resolve: () => null }), /already registered/);
assert.throws(() => H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: { state: { template: {} } } }), /requires a member with ruleset/);

H._resetForTests();
H.registerAbility(H.PHASES.ON_HIT, { id: "bad-result", rulesets: ["2024"], resolve: () => ({ event: event("legacy", 1), handled: true }) });
assert.throws(() => H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member() }), /result.events must be an array/);

H._resetForTests();
H.registerAbility(H.PHASES.ON_HIT, { id: "illegal-claim", rulesets: ["2024"], resolve: ({ sequence }) => result("claim", sequence, true) });
assert.throws(() => H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member() }), /cannot claim non-exclusive phase/);

H._resetForTests();
const originalError = console.error;
console.error = () => {};
H.registerAbility(H.PHASES.ON_HIT, { id: "applies-error", rulesets: ["2024"], appliesTo: () => { throw new Error("boom"); }, resolve: () => null });
assert.throws(() => H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member() }), /failed during appliesTo/);
H._resetForTests();
H.registerAbility(H.PHASES.ON_HIT, { id: "resolve-error", rulesets: ["2024"], resolve: () => { throw new Error("boom"); } });
assert.throws(() => H.runPhase(H.PHASES.ON_HIT, { sequence: 1, member: member() }), /failed during resolve/);
console.error = originalError;

H._resetForTests();
const seedEvents = [event("seed", 1)];
H.registerAbility(H.PHASES.ON_HIT, { id: "copy-check", rulesets: ["2024"], resolve: ({ events, sequence }) => { events.push(event("local-only", sequence)); return { events: [event("returned", sequence)], sequence: sequence + 1, claimed: false }; } });
const copied = H.runPhase(H.PHASES.ON_HIT, { sequence: 2, member: member(), events: seedEvents });
assert.deepEqual(seedEvents.map((item) => item.feature_id), ["seed"], "dispatcher must not mutate the caller's event array");
assert.deepEqual(copied.events.map((item) => item.feature_id), ["seed", "returned"]);

console.log("Browser ability-hook dispatcher regressions passed.");
