"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
let supportCalls = 0, surgeCalls = 0;
window.IRON_PIT_BROWSER_STATE = { beginTurn: () => {}, distance: () => 5, nearestTarget: () => null };
window.IRON_PIT_BROWSER_GRAPPLE = { cleanup: () => {}, shouldEscape: () => false, speedIsZero: () => false };
window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL = {
  forcedRetreatActive: () => true,
  event: (sequence, round, member) => ({
    sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
    actor_name: member.state.template.name, target_id: member.combatant_id,
    target_name: member.state.template.name, feature_id: "forced-retreat", animation: "forced-retreat",
  }),
};
window.IRON_PIT_BROWSER_SUPPORT = { resolve: () => { supportCalls += 1; return null; } };
window.IRON_PIT_BROWSER_ACTION_SURGE = { resolveAttack: () => { surgeCalls += 1; return null; } };
window.IRON_PIT_BROWSER_RAGE = { finalize: (sequence) => ({ event: null, sequence }) };
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8"), { filename: "browser-turn.js" });

const member = {
  combatant_id: "fighter", side: "heroes", position_ft: 5,
  state: { template: { name: "Fighter", attacks: [] }, timed_effects: [{ turn_behavior: "forced_retreat" }] },
};
const enemy = { combatant_id: "goblin", side: "monsters", position_ft: 10, state: { template: { name: "Goblin" } } };
const setup = { heroes: [member], monsters: [enemy] };
const before = member.position_ft;
const result = window.IRON_PIT_BROWSER_TURN.resolveTurn(1, 1, member, setup);

assert.equal(member.position_ft, before);
assert.equal(supportCalls, 0);
assert.equal(surgeCalls, 0);
assert.equal(result.events.length, 1);
assert.equal(result.events[0].feature_id, "forced-retreat");
assert.equal(result.events.some((event) => event.event_type === "movement" || event.event_type === "attack"), false);
console.log("Browser forced-retreat live turn regression passed.");
