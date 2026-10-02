"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const template = structuredClone(window.IRON_PIT_BROWSER_HEROES["kael-stillwater-l17"]);
const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
assert.ok(template, "generated 2024 Monk 17 card must exist");
assert.ok(targetTemplate, "generated target card must exist");

assert.equal(template.level, 17);
assert.equal(template.max_hp, 139);
assert.equal(template.speed_ft, 55);
assert.equal(template.initiative_bonus, 11);
assert.equal(template.resources["focus-points"], 17);
assert.equal(template.attacks.find((item) => item.weaponId === "unarmed-strike").diceSize, 12);
assert.deepEqual(template.saving_throw_bonuses, {
  strength: 7,
  dexterity: 11,
  constitution: 9,
  intelligence: 6,
  wisdom: 8,
  charisma: 6,
});
assert.equal(template.resource_backed_on_hit_save_rider.save_dc, 16);
assert.equal(template.healingActions[0].diceSize, 12);
assert.equal(template.attackDamageReductionReaction.zeroDamageRedirect.saveDc, 16);
assert.equal(template.attackDamageReductionReaction.zeroDamageRedirect.damageDiceSize, 12);

const rule = template.deferred_save_effect;
assert.equal(rule.source_id, "quivering-palm");
assert.equal(rule.source_name, "Quivering Palm");
assert.deepEqual(rule.trigger_weapon_ids, ["unarmed-strike"]);
assert.equal(rule.resource_id, "focus-points");
assert.equal(rule.resource_cost, 4);
assert.equal(rule.save_ability, "constitution");
assert.equal(rule.save_dc, 16);
assert.equal(rule.failure_damage_dice_count, 10);
assert.equal(rule.failure_damage_dice_size, 12);
assert.equal(rule.failure_damage_type, "force");
assert.equal(rule.success_damage_from_failure, "half");
assert.equal(rule.allow_attack_slot_activation, true);
assert.equal(rule.allow_harmless_end_on_rearm, true);
assert.equal(rule.max_active_targets, 1);

const S = window.IRON_PIT_BROWSER_STATE;
const DE = window.IRON_PIT_BROWSER_DEFERRED_SAVE_EFFECT;
const SLOT = window.IRON_PIT_BROWSER_DEFERRED_ATTACK_SLOT;
const unarmed = template.attacks.find((item) => item.weaponId === "unarmed-strike");

function fixture() {
  const hero = {
    combatant_id: "hero-kael-17",
    side: "heroes",
    position_ft: 5,
    state: S.buildState(structuredClone(template)),
  };
  const makeTarget = (id) => {
    const card = structuredClone(targetTemplate);
    card.max_hp = 300;
    return {
      combatant_id: id,
      side: "monsters",
      position_ft: 10,
      state: S.buildState(card),
    };
  };
  const first = makeTarget("monster-first");
  const second = makeTarget("monster-second");
  return { hero, first, second, setup: { heroes: [hero], monsters: [first, second] } };
}

{
  const { hero, first, setup } = fixture();
  const armed = DE.arm(hero.state, first.state, first.combatant_id, unarmed, 1);
  assert.ok(armed);
  assert.equal(armed.resourceRemaining, 13);
  hero.state.action_available = false;

  window.IRON_PIT_DICE = {
    values: [1, ...Array(10).fill(12)],
    roll() { return this.values.shift(); },
    rollMany(count) { return Array.from({ length: count }, () => this.roll()); },
  };
  const event = SLOT.resolve(1, 1, hero, setup);
  assert.ok(event);
  assert.equal(event.save_succeeded, false);
  assert.equal(event.damage_roll.total, 120);
  assert.equal(event.damage_components[0].damage_type, "force");
  assert.equal(first.state.current_hp, 180);
  assert.equal(hero.state.action_available, false);
  assert.deepEqual(hero.state.deferred_effects, []);
}

{
  const { hero, first, setup } = fixture();
  DE.arm(hero.state, first.state, first.combatant_id, unarmed, 1);
  hero.state.action_available = false;
  window.IRON_PIT_DICE = {
    values: [20, ...Array(10).fill(12)],
    roll() { return this.values.shift(); },
    rollMany(count) { return Array.from({ length: count }, () => this.roll()); },
  };
  const event = SLOT.resolve(1, 1, hero, setup);
  assert.ok(event);
  assert.equal(event.save_succeeded, true);
  assert.equal(event.damage_roll.total, 60);
  assert.equal(first.state.current_hp, 240);
}

{
  const { hero, first, second } = fixture();
  const firstArm = DE.arm(hero.state, first.state, first.combatant_id, unarmed, 1);
  assert.equal(firstArm.resourceRemaining, 13);

  const duplicate = DE.arm(hero.state, first.state, first.combatant_id, unarmed, 1);
  assert.equal(duplicate, null);
  assert.equal(hero.state.resources["focus-points"], 13);

  const replacement = DE.arm(hero.state, second.state, second.combatant_id, unarmed, 1);
  assert.ok(replacement);
  assert.equal(replacement.resourceRemaining, 9);
  assert.deepEqual(hero.state.deferred_effects, [
    { source_id: "quivering-palm", target_id: second.combatant_id, armed_round: 1 },
  ]);
}

console.log("2024 Monk 17 Quivering Palm browser parity passed.");
