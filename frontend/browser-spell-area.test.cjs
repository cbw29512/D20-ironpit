"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-spell-area.js"), "utf8"));
const A = window.IRON_PIT_BROWSER_SPELL_AREA;

const member = (side, index, position) => ({
  combatant_id: `${side}-${index}`, side, position_ft: position,
  state: { is_alive: true, is_dead: false, current_hp: 10 },
});
const setup = (heroes, monsters) => ({ heroes, monsters });

assert.equal(A.areaSlotCount(5), 1);
assert.equal(A.areaSlotCount(10), 2);
assert.equal(A.areaSlotCount(20), 4);
assert.equal(A.areaSlotCount(30), 6);
assert.equal(A.areaSlotCount(60), 6);

{
  const heroes = [member("heroes", 0, 0)];
  const monsters = Array.from({ length: 6 }, (_, i) => member("monsters", i, 30));
  const result = A.bestPlacement(heroes[0], setup(heroes, monsters), 20, 150);
  assert.equal(result.enemyIds.length, 4);
  assert.equal(result.friendlyIds.length, 0);
}

{
  const heroes = [member("heroes", 0, 0)];
  const monsters = Array.from({ length: 6 }, (_, i) => member("monsters", i, 60));
  assert.equal(A.bestPlacement(heroes[0], setup(heroes, monsters), 30, 150).enemyIds.length, 6);
}

{
  const heroes = [member("heroes", 0, 0)];
  const monsters = Array.from({ length: 3 }, (_, i) => member("monsters", i, 5));
  const result = A.bestPlacement(heroes[0], setup(heroes, monsters), 20, 150);
  assert.equal(result.enemyIds.length, 3);
  assert.deepEqual(result.friendlyIds, ["heroes-0"]);
}

{
  const heroes = [member("heroes", 0, 0), member("heroes", 1, 0)];
  const monsters = [member("monsters", 0, 5), member("monsters", 1, 5)];
  assert.equal(A.bestPlacement(heroes[0], setup(heroes, monsters), 10, 150), null);
  const protectedResult = A.bestPlacement(
    heroes[0], setup(heroes, monsters), 10, 150, ["heroes-0", "heroes-1"],
  );
  assert.equal(protectedResult.enemyIds.length, 2);
  assert.equal(protectedResult.friendlyIds.length, 0);
  assert.deepEqual(protectedResult.protectedFriendlyIds, ["heroes-0", "heroes-1"]);
}

{
  const heroes = [member("heroes", 0, 0)];
  const monsters = Array.from({ length: 3 }, (_, i) => member("monsters", i, 30));
  monsters[1].state.current_hp = 0;
  monsters[1].state.is_alive = false;
  monsters[1].state.is_dead = true;
  assert.equal(A.bestPlacement(heroes[0], setup(heroes, monsters), 10, 150).enemyIds.length, 1);
}

console.log("Browser spell-area decision regressions passed.");
