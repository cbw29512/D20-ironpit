const fs = require("fs");
const vm = require("vm");
const assert = require("assert");

global.window = global;
vm.runInThisContext(fs.readFileSync("frontend/browser-forced-movement.js", "utf8"));
const member = (id, x, y) => ({
  combatant_id: id,
  state: {position: {x, y}, movement_remaining_ft: 30, current_hp: 17},
});
const source = member("source", 1, 1), target = member("target", 2, 1);
const setup = {heroes: [source], monsters: [target]};
const initial = JSON.parse(JSON.stringify(target.state));
assert.strictEqual(window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pushStraightAway(target, source, setup, 15), 0);
assert.strictEqual(window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pullStraightToward(target, source, setup, 10), 0);
assert.deepStrictEqual(target.state, initial, "Displacement must leave HP, position and movement intact.");
target.state.position = null;
assert.strictEqual(window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pushStraightAway(target, source, setup, 5), 0);
assert.strictEqual(window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pullStraightToward(target, source, setup, 5), 0);
assert.throws(() => window.IRON_PIT_BROWSER_FORCED_MOVEMENT.pushStraightAway(target, source, setup, -5));
console.log("browser forced displacement exclusion passed");
