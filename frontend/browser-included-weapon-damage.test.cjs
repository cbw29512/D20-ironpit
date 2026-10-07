"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, "test-fixtures/included-weapon-damage.json"), "utf8"));
global.window = globalThis;
for (const file of [
  "browser-modifier-validation.js", "browser-modifiers.js", "browser-damage-defense-rules.js",
  "browser-grapple.js", "browser-timed-conditions.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-zero-hp.js", "browser-ability-hooks.js",
  "browser-attack-outcome.js", "browser-attack.js",
]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
const S = window.IRON_PIT_BROWSER_STATE;
for (const fixture of cases) {
  const before = JSON.stringify(fixture);
  const attacker = { combatant_id: "attacker", side: "heroes", position_ft: 0,
    state: S.buildState(structuredClone(fixture.attacker)) };
  const target = { combatant_id: "target", side: "monsters", position_ft: 5,
    state: S.buildState(structuredClone(fixture.target)) };
  const queue = [...fixture.rolls];
  const roll = (sides) => {
    assert.ok(queue.length, `${fixture.id}: extra damage roll would double-count included dice`);
    const value = queue.shift();
    assert.ok(value >= 1 && value <= sides);
    return value;
  };
  window.IRON_PIT_DICE = { roll, rollMany: (n, sides) => Array.from({ length: n }, () => roll(sides)) };
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, attacker, target, fixture.attack, 5);
  assert.equal(event.hit, true, fixture.id);
  assert.equal(event.critical, fixture.critical, fixture.id);
  assert.equal(event.damage_roll.total, fixture.total, fixture.id);
  assert.equal(target.state.current_hp, fixture.remainingHp, fixture.id);
  assert.deepEqual(event.damage_components.map((p) => ({
    type: p.damage_type, total: p.total, applied: p.applied_total, notation: p.notation,
  })), fixture.components, fixture.id);
  assert.equal(queue.length, 0, fixture.id);
  assert.equal(JSON.stringify(fixture), before, "source-derived card parameters remain immutable");
  assert.equal(S.buildState(structuredClone(fixture.target)).current_hp, 200, "new fight resets HP");
}
assert.equal(cases.length, 10);
console.log("Included weapon dice, magical qualifiers, criticals, typed defenses, reset, and Python/browser parity passed.");
