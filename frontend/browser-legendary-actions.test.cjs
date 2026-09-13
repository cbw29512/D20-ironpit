const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-legendary-actions.js");

function state() {
  const value = {
    template: {
      legendary_actions: {
        max_uses: 3,
        options: [
          { id: "pounce", cost: 1, once_until_owner_turn: false },
          { id: "gaze", cost: 1, once_until_owner_turn: true },
        ],
      },
    },
    is_dead: false,
    is_unconscious: false,
    active_effect_ids: [],
  };
  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.initialize(value);
  return value;
}

{
  const monster = state();
  assert.equal(monster.legendary_action_uses_remaining, 3);
  assert.equal(window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.canSpend(monster, "pounce", "monster-1", "monster-1"), false);
  assert.equal(window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.canSpend(monster, "pounce", "monster-1", "hero-1"), true);
}

{
  const monster = state();
  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.spend(monster, "gaze");
  assert.equal(monster.legendary_action_uses_remaining, 2);
  assert.deepEqual(monster.legendary_action_locked_option_ids, ["gaze"]);
  assert.equal(window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.canSpend(monster, "gaze", "monster-1", "hero-1"), false);
  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.refresh(monster);
  assert.equal(monster.legendary_action_uses_remaining, 3);
  assert.deepEqual(monster.legendary_action_locked_option_ids, []);
}

{
  const monster = state();
  for (let i = 0; i < 3; i += 1) window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.spend(monster, "pounce");
  assert.equal(window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.canSpend(monster, "pounce", "monster-1", "hero-1"), false);
  assert.throws(() => window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS.spend(monster, "pounce"), /Insufficient legendary action uses/);
}

console.log("browser legendary-action economy lifecycle passed");
