"use strict";

// Direct browser fight parity for a card-declared recurring-hit damage packet.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const State = window.IRON_PIT_BROWSER_STATE;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const EndTurn = window.IRON_PIT_BROWSER_END_TURN_RECURRING_DAMAGE;
const Timed = window.IRON_PIT_BROWSER_TIMED;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function setDice(rolls) {
  try {
    const queue = [...rolls];
    window.IRON_PIT_DICE = {
      roll(sides) {
        const v = queue.shift();
        if (!Number.isInteger(v) || v < 1 || v > sides) {
          throw new Error("Unexpected or invalid d" + sides + " roll: " + v);
        }
        return v;
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Invalid recurring-damage browser dice fixture.", error);
    throw error;
  }
}

function fighter(id, side, position) {
  try {
    const template = structuredClone(base);
    Object.assign(template, {
      id: "template-" + id, name: id, armor_class: 10, max_hp: 70,
      damage_resistances: [], condition_immunities: [], traits: [],
      weapon_masteries: [],
    });
    return { combatant_id: id, side, position_ft: position, state: State.buildState(template) };
  } catch (error) {
    console.error("Recurring-damage browser combatant fixture failed.", error);
    throw error;
  }
}

function fight() {
  try {
    const attacker = fighter("other-source", "monsters", 0);
    const target = fighter("other-target", "heroes", 5);
    const attack = {
      id: "custom-contact", weaponId: "custom-contact", name: "Touch",
      kind: "melee", bonus: 10, diceCount: 1, diceSize: 6,
      damageBonus: 0, damageType: "fire", reach: 5, animation: "strike",
      onHitDamage: [], onHitRecurringDamage: {
        effectId: "burning", diceCount: 1, diceSize: 6,
        damageType: "fire", tickTiming: "target_turn_end",
        stacking: "nonstacking", endsIfSourceDead: false,
      },
    };
    attacker.state.template.attacks = [attack];
    attacker.state.template.primary_attack_id = attack.id;
    return { attacker, target, attack, setup: { heroes: [target], monsters: [attacker] } };
  } catch (error) {
    console.error("Recurring-damage browser fight setup failed.", error);
    throw error;
  }
}

try {
  const { attacker, target, attack, setup } = fight();
  setDice([18, 2]);
  const hit = Attack.resolveAttack(1, 1, attacker, target, attack, 5, {
    spendAction: false, setup,
  });
  assert.equal(hit.hit, true);
  let effects = target.state.timed_effects.filter(e => e.effect_id === "burning");
  assert.equal(effects.length, 1);
  assert.equal(effects[0].source_name, "Touch");
  assert.equal(effects[0].end_of_turn_damage_type, "fire");

  // Re-hitting cannot stack the same nonstacking source-declared debuff.
  setDice([18, 2]);
  Attack.resolveAttack(2, 1, attacker, target, attack, 5, {
    spendAction: false, setup,
  });
  assert.equal(target.state.timed_effects.filter(e => e.effect_id === "burning").length, 1);

  const before = target.state.current_hp;
  setDice([4]);
  const tick = EndTurn.resolve(3, 1, target, setup);
  assert.equal(tick.events.length, 1);
  assert.equal(tick.sequence, 4);
  assert.equal(target.state.current_hp, before - 4);
  assert.match(tick.events[0].description, /Touch deals 4 fire damage/);

  target.state.template.damage_resistances = ["fire"];
  setDice([6]);
  const resisted = EndTurn.resolve(4, 2, target, setup);
  assert.equal(resisted.events.length, 1);
  assert.equal(target.state.current_hp, before - 7);

  // A dead source does not extinguish the target's fire.
  attacker.state.is_alive = false;
  attacker.state.is_dead = true;
  setDice([2]);
  EndTurn.resolve(5, 3, target, setup);
  assert.equal(target.state.current_hp, before - 8);
  Timed.removeEffect(target.state, effects[0]);
  assert.equal(target.state.timed_effects.filter(e => e.effect_id === "burning").length, 0);
  assert.equal(EndTurn.resolve(6, 4, target, setup).events.length, 0);

  const fresh = fight();
  setDice([1]);
  const missed = Attack.resolveAttack(
    1, 1, fresh.attacker, fresh.target, fresh.attack, 5,
    { spendAction: false, setup: fresh.setup },
  );
  assert.equal(missed.hit, false);
  assert.equal(fresh.target.state.timed_effects.length, 0);
} catch (error) {
  console.error("Browser end-turn recurring damage regression failed.", error);
  throw error;
}
console.log("Generic on-hit recurring and target-turn end damage passed.");
