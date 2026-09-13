const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

global.window = {};
vm.runInThisContext(fs.readFileSync(require.resolve("./browser-max-hp-reduction.js"), "utf8"), {
  filename: "browser-max-hp-reduction.js",
});

const H = window.IRON_PIT_BROWSER_MAX_HP_REDUCTION;

function state(maxHp = 20) {
  return { template: { name: "Target", max_hp: maxHp }, current_hp: maxHp, max_hp_bonus: 0, max_hp_reduction: 0 };
}

{
  const target = state();
  target.max_hp_bonus = 5;
  target.current_hp = 25;
  const result = H.apply(target, 7);
  assert.deepEqual(result, { before: 25, after: 18 });
  assert.equal(target.current_hp, 18);
  assert.equal(target.max_hp_reduction, 7);
  assert.equal(target.template.max_hp, 20);
}

{
  const target = state();
  H.apply(target, 3);
  H.apply(target, 100);
  assert.equal(H.effectiveMaxHp(target), 0);
  assert.equal(target.current_hp, 0);
}

{
  const target = state();
  assert.throws(() => H.apply(target, -1), /non-negative integer/);
}

console.log("browser max HP reduction tests passed");
