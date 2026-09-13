const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-progression-recovery.js");

function state() {
  return { template: { peerless_aim: true }, feature_last_turn_keys: {} };
}

{
  const fighter = state();
  assert.deepEqual(window.IRON_PIT_BROWSER_PEERLESS_AIM.resolve(fighter, false), { hit: true, used: true });
  assert.deepEqual(window.IRON_PIT_BROWSER_PEERLESS_AIM.resolve(fighter, false), { hit: false, used: false });
  window.IRON_PIT_BROWSER_PEERLESS_AIM.refresh(fighter);
  assert.deepEqual(window.IRON_PIT_BROWSER_PEERLESS_AIM.resolve(fighter, false), { hit: true, used: true });
}

{
  const fighter = state();
  assert.deepEqual(window.IRON_PIT_BROWSER_PEERLESS_AIM.resolve(fighter, true), { hit: true, used: false });
  assert.deepEqual(window.IRON_PIT_BROWSER_PEERLESS_AIM.resolve(fighter, false), { hit: true, used: true });
}

console.log("browser Peerless Aim lifecycle passed");
