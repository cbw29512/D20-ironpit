const assert = require("assert");
const fs = require("fs");
const vm = require("vm");

global.window = global;
let rolls = [6];
window.IRON_PIT_DICE = {
  roll(sides) {
    const value = rolls.shift();
    if (!Number.isInteger(value) || value < 1 || value > sides) throw new Error("invalid test die");
    return value;
  },
};
vm.runInThisContext(fs.readFileSync("frontend/browser-failed-d20-bonus-die.js", "utf8"));

function state() {
  return {
    resources: { "dark-ones-own-luck": 1 },
    template: {
      name: "Varek Ashenmark",
      failed_d20_bonus_die_grants: [{
        source_id: "dark-ones-own-luck",
        source_name: "Dark One's Own Luck",
        resource_id: "dark-ones-own-luck",
        resource_cost: 1,
        dice_size: 10,
        test_kinds: ["ability_check", "saving_throw"],
      }],
    },
  };
}

{
  rolls = [6];
  const actor = state();
  const original = {
    notation: "1d20+4", rolls: [5], modifier: 4, selected_roll: 5,
    total: 9, revisions: [],
  };
  const result = window.IRON_PIT_BROWSER_FAILED_D20_BONUS_DIE.apply(
    actor, original, 15, "saving_throw",
  );
  assert.equal(result.roll.total, 15);
  assert.equal(result.roll.revisions.at(-1).kind, "additive_die");
  assert.equal(result.roll.revisions.at(-1).source_effect_id, "dark-ones-own-luck");
  assert.equal(actor.resources["dark-ones-own-luck"], 0);
}

{
  rolls = [8];
  const actor = state();
  const original = {
    notation: "1d20+3", rolls: [4], modifier: 3, selected_roll: 4,
    total: 7, revisions: [],
  };
  const result = window.IRON_PIT_BROWSER_FAILED_D20_BONUS_DIE.apply(
    actor, original, 15, "ability_check",
  );
  assert.equal(result.roll.total, 15);
  assert.equal(actor.resources["dark-ones-own-luck"], 0);
}

{
  rolls = [];
  const actor = state();
  const original = {
    notation: "1d20+4", rolls: [18], modifier: 4, selected_roll: 18,
    total: 22, revisions: [],
  };
  const result = window.IRON_PIT_BROWSER_FAILED_D20_BONUS_DIE.apply(
    actor, original, 15, "saving_throw",
  );
  assert.equal(result.roll.total, 22);
  assert.equal(actor.resources["dark-ones-own-luck"], 1);
}

console.log("Browser generic failed-D20 bonus die passed.");
