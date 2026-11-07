"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const Attack = window.IRON_PIT_BROWSER_ATTACK;
const Tick = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN;
const End = window.IRON_PIT_BROWSER_END_TURN_RECURRING_DAMAGE;
const Douse = window.IRON_PIT_BROWSER_DOUSE_BURNING;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function setDice(rolls) {
  try {
    const queue = [...rolls];
    window.IRON_PIT_DICE = {
      roll(sides) {
        const value = queue.shift();
        if (!Number.isInteger(value) || value < 1 || value > sides)
          throw new Error("Invalid or missing d" + sides + " result: " + value);
        return value;
      },
      rollMany(count, sides) {
        return Array.from({ length: count }, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Start-turn damage test dice initialization failed.", error);
    throw error;
  }
}

function scene(name = "Other Flame Attack") {
  try {
    const member = (id, side, place) => {
      const template = structuredClone(base);
      Object.assign(template, {
        id: "synthetic-" + id, name: id, armor_class: 10, max_hp: 70,
        damage_resistances: [], damage_immunities: [],
        condition_immunities: [], traits: [], weapon_masteries: [],
      });
      return {
        combatant_id: id, side, position_ft: place,
        state: S.buildState(template),
      };
    };
    const source = member("synthetic-attacker", "monsters", 0);
    const target = member("synthetic-victim", "heroes", 5);
    const attack = {
      id: "renamed-source-hit", weaponId: "renamed-source-hit", name,
      kind: "melee", bonus: 10, diceCount: 1, diceSize: 6,
      damageBonus: 0, damageType: "fire", reach: 5, animation: "strike",
      onHitDamage: [], onHitRecurringDamage: {
        effectId: "burning", diceCount: 1, diceSize: 10,
        damageType: "fire", tickTiming: "target_turn_start",
        stacking: "nonstacking", endsIfSourceDead: false,
        removalActionIds: ["douse-fire"],
      },
    };
    source.state.template.attacks = [attack];
    source.state.template.primary_attack_id = attack.id;
    return { source, target, attack, setup: { heroes: [target], monsters: [source] } };
  } catch (error) {
    console.error("Start-turn damage browser fixture failed.", error);
    throw error;
  }
}

try {
  assert.ok(S && Attack && Tick && End && Douse, "Shared combat modules must be loaded");
  const { source, target, attack, setup } = scene();
  setDice([18, 2]);
  const hit = Attack.resolveAttack(1, 1, source, target, attack, 5, {
    spendAction: false, setup,
  });
  assert.equal(hit.hit, true);
  const active = target.state.timed_effects.filter(e => e.effect_id === "burning");
  assert.equal(active.length, 1);
  assert.equal(active[0].source_name, "Other Flame Attack");
  assert.equal(active[0].start_of_turn_dice_count, 1);
  assert.equal(active[0].start_of_turn_dice_size, 10);
  assert.equal(active[0].start_of_turn_damage_type, "fire");
  assert.equal(active[0].end_of_turn_dice_count, 0);
  assert.ok(active[0].allowed_removal_action_ids.includes("douse-fire"));

  // The same nonstacking source should not add a second debuff.
  setDice([18, 2]);
  Attack.resolveAttack(2, 1, source, target, attack, 5, {
    spendAction: false, setup,
  });
  assert.equal(target.state.timed_effects.filter(e => e.effect_id === "burning").length, 1);

  const before = target.state.current_hp;
  setDice([9]);
  assert.deepEqual(End.resolve(3, 1, target, setup).events, []);
  assert.equal(target.state.current_hp, before, "Start-turn burn cannot tick at turn end");

  source.state.is_dead = true;
  source.state.is_alive = false;
  setDice([7]);
  const start = Tick.resolve(4, 2, target, setup);
  assert.equal(start.events.length, 1);
  assert.match(start.events[0].description, /deals 7 fire damage/);
  assert.equal(target.state.current_hp, before - 7);

  // Source authorizes self douse, not an invented helper range.
  assert.equal(Douse.choose(target, setup), target);
  assert.throws(() => Douse.resolve(5, 2, source, target), /Helper dousing/);
  const removal = Douse.resolve(6, 2, target, target);
  assert.equal(removal.feature_id, "douse-fire");
  assert.deepEqual(removal.removed_condition_ids, ["burning"]);
  assert.equal(target.state.action_available, false);
  setDice([8]);
  assert.equal(Tick.resolve(7, 3, target, setup).events.length, 0);
  assert.equal(target.state.current_hp, before - 7);

  // Typed Fire resistance halves the very same generic periodic packet.
  const resistant = scene("Renamed Contact");
  resistant.target.state.template.damage_resistances = ["fire"];
  setDice([18, 2]);
  Attack.resolveAttack(1, 1, resistant.source, resistant.target, resistant.attack, 5, {
    spendAction: false, setup: resistant.setup,
  });
  const rBefore = resistant.target.state.current_hp;
  setDice([7]);
  Tick.resolve(2, 2, resistant.target, resistant.setup);
  assert.equal(resistant.target.state.current_hp, rBefore - 3);

  const missed = scene("A Third Name");
  setDice([1]);
  const miss = Attack.resolveAttack(1, 1, missed.source, missed.target, missed.attack, 5, {
    spendAction: false, setup: missed.setup,
  });
  assert.equal(miss.hit, false);
  assert.equal(missed.target.state.timed_effects.length, 0);
  console.log("Universal browser start-turn on-hit Burning and Douse tests passed.");
} catch (error) {
  console.error("Browser start-turn recurring on-hit fight failed.", error);
  process.exitCode = 1;
}
