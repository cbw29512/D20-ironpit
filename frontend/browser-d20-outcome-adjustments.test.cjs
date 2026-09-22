"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, name), "utf8"),
  { filename: name },
);
load("browser-condition-rules.js");
load("browser-state.js");
load("browser-d20-outcome-adjustments.js");

const fate = {
  source_id: "boon-of-fate", resource_id: "boon-of-fate",
  range_ft: 60, dice_count: 2, dice_size: 4,
};
const member = (id, side, position, withFate = false) => ({
  combatant_id: id,
  side,
  position_ft: position,
  state: {
    template: {
      name: id, size: "medium",
      d20_outcome_adjustment: withFate ? fate : null,
    },
    current_hp: 10,
    is_alive: true,
    is_dead: false,
    is_unconscious: false,
    active_effect_ids: [],
    resources: withFate ? { "boon-of-fate": 1 } : {},
    position: null,
  },
});
const roll = (total) => ({
  notation: "1d20+0", rolls: [total], modifier: 0,
  selected_roll: total, total, revisions: [],
});
const queued = (values) => {
  const queue = [...values];
  window.IRON_PIT_DICE = {
    roll: () => queue.shift(),
    rollMany: (count) => Array.from({ length: count }, () => queue.shift()),
  };
};

{
  const roller = member("roller", "heroes", 0);
  const source = member("source", "heroes", 10, true);
  const enemy = member("enemy", "monsters", 20);
  queued([2, 3]);
  const result = window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS.adjust(
    roll(8), false, 12, roller, { heroes: [roller, source], monsters: [enemy] },
  );
  assert.equal(result.succeeded, true);
  assert.equal(result.roll.total, 13);
  assert.deepEqual(result.roll.revisions[0].adjustment_rolls, [2, 3]);
  assert.equal(source.state.resources["boon-of-fate"], 0);
}

{
  const source = member("source", "heroes", 0, true);
  const enemy = member("enemy", "monsters", 10);
  queued([2, 3]);
  const result = window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS.adjust(
    roll(15), true, 12, enemy, { heroes: [source], monsters: [enemy] },
  );
  assert.equal(result.succeeded, false);
  assert.equal(result.roll.total, 10);
  assert.equal(result.roll.revisions[0].adjustment_sign, -1);
}

console.log("Browser generic D20 outcome adjustment regressions passed.");
