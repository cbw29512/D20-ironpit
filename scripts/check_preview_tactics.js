"use strict";

const tactics = require("../frontend/preview-tactics.js");

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

try {
  const state = { distance: 5 };
  const goblin = {
    template: {
      id: "srd-goblin-warrior",
      name: "Goblin Warrior",
      speed_ft: 30,
      bonus_action_features: ["nimble-escape"],
    },
  };
  const events = [];
  const used = tactics.prepareNimbleRetreat(state, goblin, events);

  assert(used === true, "Nimble Escape should trigger in melee range.");
  assert(events.length === 2, "Nimble Escape retreat should emit two events.");
  assert(events[0].event_type === "disengage", "First event should be Disengage.");
  assert(events[0].feature_id === "nimble-escape", "Disengage should identify Nimble Escape.");
  assert(events[1].event_type === "movement", "Second event should be retreat movement.");
  assert(events[1].animation === "retreat", "Retreat should use retreat animation.");
  assert(state.distance === 35, "Goblin should retreat 30 feet from 5 to 35 feet.");

  const rangedState = { distance: 35 };
  const rangedEvents = [];
  assert(
    tactics.prepareNimbleRetreat(rangedState, goblin, rangedEvents) === false,
    "Nimble Escape retreat should not fire outside melee range.",
  );
  assert(rangedEvents.length === 0, "No retreat events should be emitted at range.");

  console.log("Preview Nimble Escape checks passed.");
} catch (error) {
  console.error("Preview Nimble Escape checks failed", error);
  process.exitCode = 1;
}
