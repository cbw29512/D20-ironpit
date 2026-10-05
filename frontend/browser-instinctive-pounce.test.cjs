const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = global;
window.IRON_PIT_BROWSER_STATE = {
  distance: (a, b) => Math.abs(a.position_ft - b.position_ft),
};
window.IRON_PIT_BROWSER_MODIFIERS = { effectiveSpeed: () => 30 };
let speedZero = false;
window.IRON_PIT_BROWSER_GRAPPLE = { speedIsZero: () => speedZero };
let observedRemaining = null;
let observedOptions = null;
window.IRON_PIT_BROWSER_REACTION_MOVEMENT = {
  moveToward: (sequence, round, mover, _target, _setup, _desired, _source, options) => {
    observedRemaining = mover.state.movement_remaining_ft;
    observedOptions = options;
    return { events: [{ event_type: "movement", sequence, round_number: round }], sequence: sequence + 1 };
  },
};
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-activation-movement.js"), "utf8"));

const mover = {
  combatant_id: "hero",
  side: "heroes",
  position_ft: 0,
  state: {
    is_dead: false,
    is_unconscious: false,
    movement_remaining_ft: 40,
    template: { speed_ft: 40 },
  },
};
const target = {
  combatant_id: "monster",
  side: "monsters",
  position_ft: 30,
  state: { is_dead: false, is_unconscious: false },
};
const result = window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT.resolve(
  7, 2, mover, { heroes: [mover], monsters: [target] }, { speedFraction: 0.5, turnKey: "2:hero" },
);
assert.equal(observedRemaining, 15, "activation movement gets an isolated half-effective-Speed budget");
assert.equal(mover.state.movement_remaining_ft, 40, "activation movement must not consume or inflate normal turn movement");
assert.equal(result.sequence, 8);
assert.equal(result.events.length, 1);
assert.equal(observedOptions.disengaged, false);

window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT.resolve(
  9, 2, mover, { heroes: [mover], monsters: [target] },
  { speedFraction: 0.5, turnKey: "2:hero", provokesOpportunityAttacks: false },
);
assert.equal(observedOptions.disengaged, true, "OA-free granted movement must suppress reactions only for that movement");

assert.throws(
  () => window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT.resolve(1, 1, mover, { heroes: [mover], monsters: [target] }, { speedFraction: 1.5 }),
  /speedFraction/,
);

const rageSource = fs.readFileSync(path.join(__dirname, "browser-rage.js"), "utf8");
const turnSource = fs.readFileSync(path.join(__dirname, "browser-turn.js"), "utf8");
assert.match(rageSource, /instinctive_pounce_fraction/);
assert.match(rageSource, /IRON_PIT_BROWSER_ACTIVATION_MOVEMENT/);
assert.doesNotMatch(turnSource, /instinctive_pounce_fraction/, "turn engine must not own Rage rider sequencing");

for (const htmlPath of [path.join(__dirname, "index.html"), path.join(__dirname, "..", "index.html")]) {
  const html = fs.readFileSync(htmlPath, "utf8");
  assert.ok(html.indexOf("browser-activation-movement.js") >= 0, htmlPath + " must load activation movement");
  assert.ok(html.indexOf("browser-activation-movement.js") < html.indexOf("browser-ability-hook-installation.js"), htmlPath + " must load activation movement before hook installation");
  assert.ok(html.indexOf("browser-ability-hook-installation.js") < html.indexOf("browser-turn.js"), htmlPath + " must install hooks before turn resolver");
}

console.log("Browser Instinctive Pounce activation movement wiring is certified.");


speedZero = true;
observedRemaining = null;
const blocked = window.IRON_PIT_BROWSER_ACTIVATION_MOVEMENT.resolve(
  20, 3, mover, { heroes: [mover], monsters: [target] },
  { speedFraction: 0.5, turnKey: "3:hero", provokesOpportunityAttacks: false },
);
assert.equal(blocked.events.length, 0, "speed-zero must block all granted activation movement");
assert.equal(observedRemaining, null, "speed-zero must stop before movement resolution");
speedZero = false;
