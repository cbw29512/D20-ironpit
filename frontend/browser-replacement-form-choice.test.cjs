"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, "browser-replacement-form-choice.js"), "utf8"),
  { filename: "browser-replacement-form-choice.js" },
);
const choose = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_CHOICE.chooseProfitableChangeShape;
const projected = (id, outgoing, incoming, control = 0, legal = true) => ({
  formTemplateId: id, outgoingDamagePerRound: outgoing,
  incomingDamagePerRound: incoming, controlValuePerRound: control, legallyCompiled: legal,
});
const deva = projected("2014-deva", 30, 15);
const scorpion = projected("2014-giant-scorpion", 45, 20, 6);
const ape = projected("2014-giant-ape", 47, 18);
const rex = projected("2014-tyrannosaurus-rex", 44, 17, 9);

assert.equal(choose(deva, [ape], 1, 30), null, "Do not waste an Action for one turn of gain");
assert.equal(choose(deva, [ape], 4, 40), null, "Tie or loss must stay original");
assert.equal(choose(deva, [scorpion, ape, rex], 4, 30), "2014-tyrannosaurus-rex");
assert.equal(choose(deva, [projected("uncertified", 200, 0, 0, false), ape], 4, 30), "2014-giant-ape");
assert.equal(choose(deva, [projected("good", 99, 0)], 0, 30), null);
assert.throws(() => choose(deva, [ape, ape], 3, 30), /duplicate/);
assert.throws(() => choose(deva, [ape], -1, 30), /nonnegative integer/);
assert.throws(() => choose(deva, [projected("bad", NaN, 0)], 3, 30), /finite/);
{
  const baseline = { ...deva, incomingConditionCostPerRound: 12 };
  const trueCounter = {
    ...projected("2014-resistant-humanoid", 27, 11),
    incomingConditionCostPerRound: 0,
  };
  const brute = { ...projected("2014-strong-beast", 39, 18), incomingConditionCostPerRound: 12 };
  assert.equal(choose(baseline, [trueCounter, brute], 4, 20), "2014-resistant-humanoid");
  assert.equal(choose(
    baseline, [{ ...trueCounter, incomingConditionCostPerRound: 12 }], 3, 20
  ), null, "Do not invent an immunity that the printed form lacks");
}
console.log("Browser Change Shape tactical choice tests passed");

{
  const generic = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_CHOICE.chooseProfitableReplacementForm;
  const cases = [
    { edition: "2014", cost: 20, expected: null },
    { edition: "2024", cost: 5, expected: "2024-wolf" },
  ];
  for (const testCase of cases) {
    const actor = projected(testCase.edition + "-druid", 15, 10);
    const beast = projected(testCase.edition + "-wolf", 23, 10);
    assert.equal(
      generic(actor, [beast], 2, testCase.cost), testCase.expected,
      "Source-accurate Action versus Bonus Action opportunity costs",
    );
  }
  assert.equal(generic(
    projected("2014-druid", 15, 10),
    [projected("2014-uncertified", 100, 0, 0, false)],
    10, 5,
  ), null, "Never select an uncertified form");
}
