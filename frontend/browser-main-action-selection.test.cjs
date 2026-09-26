"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-main-action-profiles.js"), "utf8"),
  { filename: "browser-main-action-profiles.js" },
);
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-main-action-selection.js"), "utf8"),
  { filename: "browser-main-action-selection.js" },
);

const S = window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
const member = (ruleset = "2024") => ({
  combatant_id: `hero-${ruleset}`,
  state: { template: { ruleset } },
});
const ctx = (ruleset = "2024", id = null) => ({ sequence: 3, round: 1, turnKey: "1:hero", member: id ? { combatant_id: id, state: { template: { ruleset } } } : member(ruleset) });
const provider = (id, category, rulesets, discover = () => ({ payload: { id } })) => ({
  id, category, rulesets, discover,
  resolve: ({ sequence }, candidate) => ({
    events: [{ event_type: "feature", feature_id: candidate.providerId }],
    sequence: sequence + 1,
  }),
});

assert.deepEqual(S.PROFILES.normalPreMove, ["replacement-form-setup", "spell-offense"]);
assert.deepEqual(S.PROFILES.actionSurgeAttack, ["attack-action", "standard-attack"]);
assert.throws(() => S.discoverCandidates("unknown", ctx()), /Unknown Main Action opportunity profile/);
assert.throws(
  () => S.discoverCandidates("normalPreMove", { sequence: 1, member: member() }),
  /requires a stable non-empty turnKey/,
);
assert.throws(() => S.registerProvider(provider("bad", "teleport", ["2024"])), /unknown category/);
assert.throws(() => S.registerProvider(provider("bad-rules", "dodge", ["2025"])), /invalid ruleset scope/);

S._resetForTests();
const discovered = [];
S.registerProvider(provider("dodge", "dodge", ["2014", "2024"], () => {
  discovered.push("dodge");
  return { payload: {} };
}));
S.registerProvider(provider("spell", "spell-offense", ["2024"], () => {
  discovered.push("spell");
  return { payload: { choice: "best-spell" } };
}));
const preMove = S.discoverCandidates("normalPreMove", ctx());
assert.deepEqual(discovered, ["spell"], "disallowed categories must not be discovered");
assert.deepEqual(preMove.map((item) => item.providerId), ["spell"]);
assert.equal(preMove[0].opportunityProfile, "normalPreMove");
assert.equal(preMove[0].combatantId, "hero-2024");
assert.equal(preMove[0].turnKey, "1:hero");
assert.equal(S.selectCandidate("normalPreMove", preMove).providerId, "spell");
assert.deepEqual(S.discoverCandidates("normalPreMove", ctx("2014")), [], "ruleset scope must isolate providers");

S._resetForTests();
S.registerProvider(provider("dodge-first", "dodge", ["2024"]));
S.registerProvider(provider("standard", "standard-attack", ["2024"]));
S.registerProvider(provider("spell-last", "spell-offense", ["2024"]));
const ordered = S.discoverCandidates("normalPostMove", ctx());
assert.equal(
  S.selectCandidate("normalPostMove", ordered).providerId,
  "spell-last",
  "Arena category policy must beat provider registration order",
);

S._resetForTests();
S.registerProvider(provider("spell", "spell-offense", ["2024"], () => {
  throw new Error("spell discovery should not run");
}));
S.registerProvider(provider("dodge", "dodge", ["2024"], () => {
  throw new Error("dodge discovery should not run");
}));
S.registerProvider(provider("attack", "attack-action", ["2024"]));
const surge = S.discoverCandidates("actionSurgeAttack", ctx());
assert.deepEqual(surge.map((item) => item.providerId), ["attack"]);
assert.equal(S.selectCandidate("actionSurgeAttack", surge).providerId, "attack");

const forgedSpell = {
  providerId: "spell", category: "spell-offense",
  opportunityProfile: "normalPreMove", payload: {},
};
assert.equal(S.selectCandidate("actionSurgeAttack", [forgedSpell]), null);

S._resetForTests();
S.registerProvider(provider("attack-a", "attack-action", ["2024"]));
S.registerProvider(provider("attack-b", "attack-action", ["2024"]));
assert.throws(
  () => S.selectCandidate("normalPostMove", S.discoverCandidates("normalPostMove", ctx())),
  /multiple candidates in category "attack-action"/,
);

S._resetForTests();
S.registerProvider(provider("standard", "standard-attack", ["2024"]));
const candidate = S.selectCandidate("normalPostMove", S.discoverCandidates("normalPostMove", ctx()));
const resolved = S.resolveCandidate("normalPostMove", candidate, ctx());
assert.equal(resolved.sequence, 4);
assert.deepEqual(resolved.events.map((event) => event.feature_id), ["standard"]);

assert.throws(
  () => S.resolveCandidate("normalPostMove", candidate, ctx("2024", "other-hero")),
  /does not match the current opportunity\/combatant\/turn/,
);
assert.throws(
  () => S.resolveCandidate("normalPostMove", candidate, { ...ctx(), turnKey: "2:hero" }),
  /does not match the current opportunity\/combatant\/turn/,
);

assert.throws(
  () => S.resolveCandidate("actionSurgeAttack", { ...candidate, opportunityProfile: "actionSurgeAttack", category: "dodge" }, ctx()),
  /does not match its opportunity profile\/provider\/ruleset/,
);
assert.equal(S.selectCandidate("normalPreMove", []), null);

S._resetForTests();
const originalError = console.error;
console.error = () => {};
S.registerProvider(provider("discover-fail", "spell-offense", ["2024"], () => {
  throw new Error("discovery boom");
}));
assert.throws(
  () => S.discoverCandidates("normalPreMove", ctx()),
  (error) => /failed during discover: discovery boom/.test(error.message) && error.cause?.message === "discovery boom",
);
S._resetForTests();
S.registerProvider({
  id: "resolve-fail", category: "dodge", rulesets: ["2024"],
  discover: () => ({ payload: {} }),
  resolve: () => { throw new Error("resolution boom"); },
});
const failing = S.selectCandidate("normalPostMove", S.discoverCandidates("normalPostMove", ctx()));
assert.throws(
  () => S.resolveCandidate("normalPostMove", failing, ctx()),
  (error) => /failed during resolve: resolution boom/.test(error.message) && error.cause?.message === "resolution boom",
);
console.error = originalError;

S._resetForTests();
S.registerProvider(provider("bad-payload", "dodge", ["2024"], () => ({ payload: [] })));
assert.throws(() => S.discoverCandidates("normalPostMove", ctx()), /candidate payload must be an object/);

console.log("Browser Main Action candidate-selection contract regressions passed.");
