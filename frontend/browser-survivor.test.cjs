const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
load("browser-progression-recovery.js");
load("browser-turn.js");

function state(hp = 0) {
  return {
    template: {
      name: "Champion",
      max_hp: 202,
      death_save_advantage: true,
      death_save_recovery_minimum: 18,
      bloodied_start_turn_healing: 10,
    },
    current_hp: hp, is_alive: true, is_dead: false, is_unconscious: hp === 0, is_stable: false,
    death_save_successes: 0, death_save_failures: 0,
  };
}

{
  const rolls = [7, 18];
  window.IRON_PIT_DICE = { roll: () => rolls.shift() };
  const member = { combatant_id: "fighter", state: state() };
  const event = window.IRON_PIT_BROWSER_TURN.deathSave(1, 1, member);
  assert.deepEqual(event.death_save_roll.rolls, [7, 18]);
  assert.equal(event.death_save_roll.mode, "advantage");
  assert.equal(member.state.current_hp, 1);
}

{
  const survivor = state(101);
  assert.equal(window.IRON_PIT_BROWSER_PROGRESSION_RECOVERY.startTurnHealing(survivor), 10);
  assert.equal(survivor.current_hp, 111);
  survivor.current_hp = 0;
  assert.equal(window.IRON_PIT_BROWSER_PROGRESSION_RECOVERY.startTurnHealing(survivor), 0);
}

console.log("browser Survivor parity passed");
