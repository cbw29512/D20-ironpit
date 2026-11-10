"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-hit-point-pool.js"), "utf8"),
  { filename: "browser-hit-point-pool.js" },
);
const allocate = window.IRON_PIT_BROWSER_HIT_POINT_POOL.allocateHitPointPool;
const cases = JSON.parse(
  fs.readFileSync(path.join(__dirname, "test-fixtures", "hit-point-pool.json"), "utf8"),
).cases;

for (const example of cases) {
  const original = structuredClone(example.candidates);
  assert.deepEqual(
    allocate(example.pool, example.candidates),
    { affected: example.affected, remaining: example.remaining },
    example.name,
  );
  assert.deepEqual(example.candidates, original, "Allocation must not mutate source data");
}
for (const invalid of [-1, true, 1.2, Number.MAX_SAFE_INTEGER + 1]) {
  assert.throws(() => allocate(invalid, []));
}
assert.throws(() => allocate(5, [{ combatantId: "same", currentHp: 1 },
  { combatantId: "same", currentHp: 2 }]));
assert.throws(() => allocate(5, [{ combatantId: "a", currentHp: -1 }]));
assert.throws(() => allocate(5, [{ combatantId: "a", currentHp: 1, eligible: "yes" }]));
assert.throws(() => allocate(5, null));

console.log("Browser generic HP-pool allocation: parity cases and fail-closed checks passed.");
