"use strict";

// Browser parity: source text -> generic Bonus Action save/death/healing +
// generic Invisible concentration and named-action exit.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

function setup() {
  try {
    const card = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-will-o-wisp"];
    assert.ok(card, "Wisp must be source-admitted in the generated browser roster");
    const source = {
      combatant_id: "wisp", side: "monsters", position_ft: 0,
      state: window.IRON_PIT_BROWSER_STATE.buildState(card),
    };
    const hero = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
    assert.ok(hero, "Expected certified 2014 Fighter reference");
    const victim = {
      combatant_id: "downed", side: "heroes", position_ft: 5,
      state: window.IRON_PIT_BROWSER_STATE.buildState(hero),
    };
    const scene = { heroes: [victim], monsters: [source] };
    const life = card.saving_throw_actions.find(a => a.id === "consume-life");
    const invis = card.timed_self_buff_actions.find(a => a.id === "invisibility");
    assert.ok(life && invis);
    assert.deepEqual(
      [life.actionCost, life.saveAbility, life.dc, life.range,
       life.requiresTargetSight, life.requiresTargetZeroHpAlive,
       life.instantDeathOnFailedSave, life.healSourceOnKillDiceCount,
       life.healSourceOnKillDiceSize],
      ["bonus_action", "constitution", 10, 5, true, true, true, 3, 6],
    );
    assert.deepEqual(invis.endsOnOwnerActionIds, ["consume-life"]);
    assert.equal(invis.endsOnOwnerAttack, true);
    assert.equal(invis.endsOnOwnerSpellCast, false);
    source.state.current_hp = 8;
    victim.state.current_hp = 0;
    victim.state.is_alive = true;
    victim.state.is_dead = false;
    victim.state.is_unconscious = true;
    return { source, victim, scene, life, invis };
  } catch (error) {
    console.error("Wisp browser scenario construction failed", error);
    throw error;
  }
}

function rolled(sequence) {
  const values = [...sequence];
  window.IRON_PIT_DICE = {
    roll: (sides) => {
      const value = values.shift() ?? 1;
      if (value < 1 || value > sides) throw Error("Invalid deterministic die " + value + "/d" + sides);
      return value;
    },
    rollMany: (count, sides) => Array.from({ length: count }, () => window.IRON_PIT_DICE.roll(sides)),
  };
}

try {
  {
    const { source, victim, scene, life, invis } = setup();
    rolled([1, 2, 3, 4]);
    window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, source, invis, {
      spendActionCost: false,
      affectedStates: [source.state, victim.state],
    });
    assert.ok(source.state.active_effect_ids.includes("invisible"));
    assert.ok(source.state.concentration);
    const selected = window.IRON_PIT_BROWSER_BONUS_SAVE_ACTIONS.choose(source, scene);
    assert.equal(selected?.action?.id, "consume-life");
    assert.equal(selected?.target?.combatant_id, victim.combatant_id);
    const result = window.IRON_PIT_BROWSER_SAVES.resolveAction(
      2, 1, source, victim, life, 5, { setup: scene },
    );
    assert.equal(result.save_succeeded, false);
    assert.equal(victim.state.is_dead, true);
    assert.equal(source.state.bonus_action_available, false);
    assert.equal(result.healing_roll?.total, 9);
    assert.equal(source.state.current_hp, 17);
    assert.equal(source.state.concentration, null);
    assert.ok(!source.state.active_effect_ids.includes("invisible"));
    assert.match(result.description, /Consume Life/);
  }
  {
    const { source, victim, scene, life, invis } = setup();
    rolled([20]);
    window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS.resolve(1, 1, source, invis, {
      spendActionCost: false,
      affectedStates: [source.state, victim.state],
    });
    const result = window.IRON_PIT_BROWSER_SAVES.resolveAction(
      2, 1, source, victim, life, 5, { setup: scene },
    );
    assert.equal(result.save_succeeded, true);
    assert.equal(victim.state.is_dead, false);
    assert.equal(source.state.current_hp, 8);
    assert.equal(result.healing_roll, null);
    assert.equal(source.state.concentration, null);
    assert.ok(!source.state.active_effect_ids.includes("invisible"));
  }
  {
    const { source, victim, scene, life } = setup();
    victim.state.current_hp = 2;
    assert.equal(window.IRON_PIT_BROWSER_BONUS_SAVE_ACTIONS.choose(source, scene), null);
    assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(life, victim, 5, source.combatant_id, source), false);
    victim.state.current_hp = 0;
    victim.state.is_dead = true;
    victim.state.is_alive = false;
    assert.equal(window.IRON_PIT_BROWSER_BONUS_SAVE_ACTIONS.choose(source, scene), null);
    victim.state.is_dead = false;
    victim.state.is_alive = true;
    assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(life, victim, 5, source.combatant_id, source), true);
    assert.equal(window.IRON_PIT_BROWSER_SAVES.legalAction(life, victim, 10, source.combatant_id, source), false);
  }
  {
    // A normal Action may reduce a character from 1 HP to 0 HP before this
    // checkpoint. The retained Bonus Action must then become selectable.
    const { source, victim, scene } = setup();
    victim.state.current_hp = 1;
    assert.equal(window.IRON_PIT_BROWSER_BONUS_SAVE_ACTIONS.choose(source, scene), null);
    source.state.action_available = false;
    victim.state.current_hp = 0;
    rolled([1, 2, 3, 4]);
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    const result = hooks.runPhase(hooks.PHASES.BONUS_ACTION_WINDOW, {
      sequence: 3, round: 1, member: source, setup: scene,
      turnKey: "1:wisp", bonusActionCheckpoint: "postAction", events: [],
    });
    assert.equal(result.events[0]?.feature_id, "consume-life");
    assert.equal(victim.state.is_dead, true);
    assert.equal(source.state.current_hp, 17);
    assert.equal(source.state.bonus_action_available, false);
  }
  console.log("2014 Will-o'-Wisp Consume Life and Invisibility browser parity passed.");
} catch (error) {
  console.error("2014 Wisp browser parity failed:", error);
  process.exitCode = 1;
}
