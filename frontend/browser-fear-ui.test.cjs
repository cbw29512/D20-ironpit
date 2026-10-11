"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
global.document = { getElementById: () => null };
global.matchMedia = () => ({ matches: true });
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8"), { filename: "battlefield-replay.js" });

const replay = window.IRON_PIT_BATTLEFIELD_REPLAY;
assert.equal(replay.conditionLabel("frightened"), "😱 FEAR");
assert.equal(replay.conditionLabel("poisoned"), "POISONED");
assert.equal(replay.concentrationLabel("bless"), "✨ CONCENTRATING · BLESS");
assert.equal(replay.concentrationLabel(null), "");

const lanes = replay.classifyStatusLanes({
  active_buff_effect_ids: ["bless"],
  active_effect_ids: ["rage", "poisoned"],
  timed_effects: [{ effect_id: "weapon-mastery-sap" }],
  active_modifiers: [
    { source_effect_id: "weapon-mastery-vex", kind: "next-attack-against-advantage", flat_bonus: 0 },
    { source_effect_id: "guiding-bolt", kind: "attacks-against-advantage", flat_bonus: 0 },
  ],
  concentration: { effect_id: "shield-of-faith" },
});
assert.deepEqual(lanes.buffs, ["bless", "rage", "weapon-mastery-vex"]);
assert.deepEqual(lanes.debuffs, ["guiding-bolt", "poisoned", "weapon-mastery-sap"]);

// Both editions project source-owned permanent passives from current combat state.
const passiveMember = {
  combatant_id: "passive-test",
  state: {
    template: {
      ruleset: "2024", source_trait_names: [],
      passive_modifier_grants: [{ source_id: "ward", source_name: "Warding", kind: "condition-immunity",
        condition_id: "frightened", required_visible_active_ally_within_ft: 30 }],
    },
    active_effect_ids: ["rage"],
    active_modifiers: [{
      source_effect_id: "ward", kind: "condition-immunity", condition_id: "frightened",
      required_active_effect_ids: ["rage"], required_visible_active_ally_within_ft: 30,
    }],
  },
};
let allyWithinRange = true;
window.IRON_PIT_BROWSER_STATE = { hasVisibleActiveAllyWithin: (member, setup, distanceFt) =>
  member === passiveMember && Boolean(setup) && distanceFt === 30 && allyWithinRange };
assert.deepEqual(replay.permanentPassiveStates(passiveMember, {}), [{
  id: "Warding", active: true, explanation: "Source-owned permanent combat modifier.",
}]);
assert.deepEqual(replay.classifyStatusLanes(passiveMember.state).buffs, ["rage"], "Permanent ward must not duplicate in transient badges; Rage remains a separate active buff.");
passiveMember.state.active_effect_ids = [];
assert.equal(replay.permanentPassiveStates(passiveMember, {})[0].active, false, "Unavailable passive remains visible but grey.");
passiveMember.state.template.ruleset = "2014";
assert.equal(replay.permanentPassiveStates(passiveMember, {})[0].active, false, "Edition does not change passive display semantics.");

for (const name of ["browser-defensive-modifier-rules.js", "browser-condition-immunity.js", "browser-timed-conditions.js"]) {
  vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
}
const applied = window.IRON_PIT_BROWSER_TIMED;
passiveMember.state.template.condition_immunities = [];
passiveMember.state.timed_effects = [];
for (const edition of ["2014", "2024"]) {
  passiveMember.state.template.ruleset = edition;
  passiveMember.state.active_effect_ids = ["rage"];
  allyWithinRange = true;
  assert.equal(replay.permanentPassiveStates(passiveMember, {})[0].active, true);
  assert.equal(applied.apply(passiveMember.state, "frightened", "source", {
    targetActor: passiveMember, setup: {}, useDefaultPoisonRecovery: false,
  }), null, "Visible ally prevents Frightened rather than merely hiding the badge.");
  assert.deepEqual(passiveMember.state.timed_effects, []);
  allyWithinRange = false;
  assert.equal(replay.permanentPassiveStates(passiveMember, {})[0].active, false);
  assert.equal(applied.apply(passiveMember.state, "frightened", "source", {
    targetActor: passiveMember, setup: {}, useDefaultPoisonRecovery: false,
  }), "frightened", "Missing ally allows Frightened through the same effect pipeline.");
  passiveMember.state.active_effect_ids = ["rage"];
  passiveMember.state.timed_effects = [];
}


const view = fs.readFileSync(path.join(__dirname, "battlefield-view.js"), "utf8");
const buffLane = view.indexOf("card-status-buffs");
const debuffLane = view.indexOf("card-status-debuffs");
assert.ok(buffLane >= 0 && debuffLane > buffLane, "Buff lane must render to the left of the debuff lane.");
assert.match(view, />BUFFS</);
assert.match(view, />DEBUFFS</);

const css = fs.readFileSync(path.join(__dirname, "condition-badges.css"), "utf8");
assert.match(css, /\.card-buffs\{justify-content:flex-start\}/);
assert.match(css, /\.card-debuffs\{justify-content:flex-end\}/);
assert.match(css, /\.card-status-buffs\{text-align:left/);
assert.match(css, /\.card-status-debuffs\{text-align:right/);
assert.match(css, /\.condition-frightened/);
assert.match(css, /condition-pulse/);


assert.match(css, /@keyframes status-enter/, "New statuses need a one-time appearance animation.");
assert.match(css, /\.passive-badge\.is-inactive/, "Inactive permanent passive must remain visible and grey.");
assert.match(css, /prefers-reduced-motion:reduce/, "Status animation must respect reduced motion.");
assert.match(fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8"), /existing = new Map/, "Retain badges while effects remain active.");

const runtime = fs.readFileSync(path.join(__dirname, "browser-state.js"), "utf8");
const replaySource = fs.readFileSync(path.join(__dirname, "battlefield-replay.js"), "utf8");
assert.match(runtime, /hasVisibleActiveAllyWithin/, "The visible ally check must be shared by the browser engine.");
assert.match(replaySource, /permanentPassiveStates\(member, battle\.setup\)/, "Cards must read encounter state, not a presentation flag.");
assert.match(replaySource, /passive\.active \? "" : " is-inactive"/, "Permanent passives must remain visible while inactive.");

console.log("Battle card buff-left/debuff-right and fear UI regressions passed.");
