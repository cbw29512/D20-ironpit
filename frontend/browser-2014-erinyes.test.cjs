"use strict";

const assert = require("node:assert/strict");
const { loadWebsite } = require("./browser-test-runtime.cjs");
loadWebsite();
const S = window.IRON_PIT_BROWSER_STATE;
const source = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-erinyes"];
assert.ok(source, "the actual exported 2014 card must be admitted");
const original = JSON.stringify(source);

// Immutable card facts enter the production resolver; only fresh state changes.
function resolve(values, { renamed = false, resistance = false, immune = false } = {}) {
  try {
    const template = structuredClone(source);
    if (renamed) {
      template.id = "anonymous-character";
      template.name = "Other Archer";
      template.kind = "character";
      for (const attack of template.attacks) {
        attack.id = `other-${attack.id}`;
        attack.name = attack.kind === "ranged" ? "Venom Arrow" : "Other Blade";
      }
    }
    const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
    Object.assign(targetTemplate, {
      armor_class: 10, max_hp: 200, condition_immunities: immune ? ["poisoned"] : [],
      damage_resistances: resistance ? ["piercing"] : [],
      damage_immunities: immune ? ["poison"] : [], damage_vulnerabilities: [],
      saving_throw_bonuses: { ...targetTemplate.saving_throw_bonuses, constitution: 0 },
    });
    const actor = { combatant_id: "archer", side: "monsters", position_ft: 0, state: S.buildState(template) };
    const target = { combatant_id: "target", side: "heroes", position_ft: 60, state: S.buildState(targetTemplate) };
    const rolls = [...values];
    window.IRON_PIT_DICE = {
      roll(sides) {
        try {
          const value = rolls.shift();
          assert.ok(value >= 1 && value <= sides, `unexpected d${sides} roll: ${value}`);
          return value;
        } catch (error) { console.error("Erinyes regression die sequence failed.", error); throw error; }
      },
      rollMany(count, sides) {
        try { return Array.from({ length: count }, () => this.roll(sides)); }
        catch (error) { console.error("Erinyes regression damage dice failed.", error); throw error; }
      },
    };
    const bow = template.attacks.find(attack => attack.kind === "ranged");
    assert.deepEqual(bow.damageSourceQualifiers, ["magical"]);
    assert.equal(bow.onHitConditionSave.dc, 14);
    assert.equal(bow.onHitConditionSave.durationRounds, undefined);
    assert.equal(bow.onHitConditionSave.repeatSaveTiming, undefined);
    const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(1, 1, actor, target, bow, 60);
    assert.equal(rolls.length, 0, "a hit rolls once, four damage dice, then at most one save");
    return { event, target, actor };
  } catch (error) { console.error("Exported 2014 Erinyes combat regression failed.", error); throw error; }
}

const failed = resolve([15, 2, 2, 2, 2, 1]);
assert.equal(failed.event.hit, true);
assert.equal(failed.event.damage_roll.total, 11);
assert.deepEqual(failed.event.damage_components.map(part => part.damage_type), ["piercing", "poison"]);
assert.equal(failed.event.save_succeeded, false);
assert.ok(failed.target.state.active_effect_ids.includes("poisoned"));
assert.deepEqual(failed.target.state.timed_effects, [], "no invented expiry or repeat save");
window.IRON_PIT_BROWSER_CONDITION_REMOVAL.removeCondition(failed.target, "poisoned");
assert.ok(!failed.target.state.active_effect_ids.includes("poisoned"));
assert.ok(!S.buildState(failed.target.state.template).active_effect_ids.includes("poisoned"));

const success = resolve([15, 2, 2, 2, 2, 20]);
assert.equal(success.event.save_succeeded, true);
assert.equal(success.event.damage_roll.total, 11, "the save prevents Poisoned, not poison damage");
assert.ok(!success.target.state.active_effect_ids.includes("poisoned"));
const miss = resolve([2]);
assert.equal(miss.event.hit, false);
assert.equal(miss.target.state.current_hp, 200);
assert.ok(!miss.target.state.active_effect_ids.includes("poisoned"));

const defended = resolve([15, 2, 2, 2, 2], { resistance: true, immune: true });
assert.equal(defended.event.damage_roll.total, 2, "piercing resistance and poison immunity resolve separately");
assert.ok(!defended.target.state.active_effect_ids.includes("poisoned"));
const renamed = resolve([15, 2, 2, 2, 2, 1], { renamed: true });
assert.equal(renamed.event.damage_roll.total, 11);
assert.equal(renamed.event.save_succeeded, false);
assert.ok(renamed.target.state.active_effect_ids.includes("poisoned"));
assert.match(renamed.event.description, /Venom Arrow/);
assert.equal(JSON.stringify(source), original, "battles never mutate the source card");
console.log("2014 Erinyes exported card: shared hit/save/damage, removal, immunity, renaming and reset passed.");
