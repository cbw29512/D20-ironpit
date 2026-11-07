"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const State = window.IRON_PIT_BROWSER_STATE;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const Swallow = window.IRON_PIT_BROWSER_SWALLOW;
const heroBase = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(values) {
  try {
    const pending = [...values];
    return {
      roll(sides) {
        const result = pending.shift();
        if (!Number.isInteger(result) || result < 1 || result > sides)
          throw new Error("Unexpected d" + sides + " roll: " + result);
        return result;
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Failed to configure swallowed-hit dice.", error);
    throw error;
  }
}

function fight(name = "Renamed Bite", size = "medium") {
  try {
    const base = structuredClone(heroBase);
    Object.assign(base, {
      id: "synthetic-defender", name: "Defender", size, armor_class: 5,
      max_hp: 200, damage_resistances: [], damage_immunities: [],
      condition_immunities: [], traits: [], weapon_masteries: [],
    });
    const source = structuredClone(base);
    Object.assign(source, { id: "synthetic-source", name: "Burrower", size: "gargantuan" });
    const bite = {
      id: "attack-hit-bite", weaponId: "attack-hit-bite", name,
      kind: "melee", bonus: 9, diceCount: 3, diceSize: 8,
      damageBonus: 9, damageType: "piercing", reach: 10,
      animation: "strike", onHitDamage: [],
    };
    source.attacks = [bite];
    source.primary_attack_id = bite.id;
    source.swallowActions = [{
      sourceName: "Swallow", attackId: bite.id, deliveryMode: "attack_hit",
      requiresExistingGrapple: false, onHitSaveAbility: "dexterity",
      onHitSaveDc: 19, maxTargetSize: "large", damageDiceCount: 6,
      damageDiceSize: 6, damageType: "acid", maxSwallowed: null,
      exitMovementFt: 20, regurgitationDamageThreshold: 30,
      regurgitationSaveAbility: "constitution", regurgitationSaveDc: 21,
      regurgitationRangeFt: 10, regurgitationAllSwallowed: true,
    }];
    const attacker = {
      combatant_id: "source", side: "monsters", position_ft: 0,
      state: State.buildState(source),
    };
    const defender = {
      combatant_id: "target", side: "heroes", position_ft: 5,
      state: State.buildState(base),
    };
    return { attacker, defender, bite, setup: {
      heroes: [defender], monsters: [attacker], ruleset: "2014",
    }};
  } catch (error) {
    console.error("Generic Bite-hit Swallow test setup failed.", error);
    throw error;
  }
}

try {
  assert.ok(State && Attack && Swallow, "Universal Swallow runtime unavailable");
  {
    const { attacker, defender, bite, setup } = fight();
    window.IRON_PIT_DICE = dice([19, 5, 5, 5, 1]);
    const hit = Attack.resolveAttack(1, 1, attacker, defender, bite, 5, { setup });
    assert.equal(hit.hit, true);
    assert.equal(hit.save_ability, "dexterity");
    assert.equal(hit.save_dc, 19);
    assert.equal(hit.save_succeeded, false);
    assert.equal(defender.state.swallowed.source_id, "source");
    assert.ok(hit.applied_condition_ids.includes("blinded"));
    assert.ok(hit.applied_condition_ids.includes("restrained"));
    const hpBefore = defender.state.current_hp;
    window.IRON_PIT_DICE = dice([2, 2, 2, 2, 2, 2]);
    const tick = Swallow.sourceTurnDamage(2, 2, attacker, setup);
    assert.equal(tick.events.length, 1);
    assert.equal(defender.state.current_hp, hpBefore - 12);
    attacker.state.is_dead = true;
    attacker.state.is_alive = false;
    attacker.state.current_hp = 0;
    assert.ok(Swallow.cleanup(setup).includes("target"));
    assert.equal(defender.state.swallowed, null);
    assert.ok(defender.state.active_effect_ids.includes("prone"));
  }
  {
    const { attacker, defender, bite, setup } = fight("Another Bite");
    window.IRON_PIT_DICE = dice([19, 5, 5, 5, 20]);
    const saved = Attack.resolveAttack(1, 1, attacker, defender, bite, 5, { setup });
    assert.equal(saved.hit, true);
    assert.equal(saved.save_succeeded, true);
    assert.equal(defender.state.swallowed, null);
  }
  {
    const { attacker, defender, bite, setup } = fight("Massive Target Bite", "huge");
    window.IRON_PIT_DICE = dice([19, 5, 5, 5]);
    const hit = Attack.resolveAttack(1, 1, attacker, defender, bite, 5, { setup });
    assert.equal(hit.hit, true);
    assert.equal(hit.saving_throw_roll, null);
    assert.equal(defender.state.swallowed, null);
  }
  {
    const { attacker, defender, bite, setup } = fight("Missed Bite");
    window.IRON_PIT_DICE = dice([1]);
    const miss = Attack.resolveAttack(1, 1, attacker, defender, bite, 5, { setup });
    assert.equal(miss.hit, false);
    assert.equal(defender.state.swallowed, null);
  }
  console.log("Universal browser Bite-hit save Swallow and release passed");
} catch (error) {
  console.error("Bite-hit source-neutral Swallow browser fight failed.", error);
  process.exitCode = 1;
}
