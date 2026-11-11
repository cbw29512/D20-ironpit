"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const D = window.IRON_PIT_BROWSER_DOUSE_BURNING;
const S = window.IRON_PIT_BROWSER_STATE;
const E = window.IRON_PIT_ACTION_ECONOMY;
const End = window.IRON_PIT_BROWSER_END_TURN_RECURRING_DAMAGE;
const P = window.IRON_PIT_BROWSER_SUPPORT;

function scene() {
  try {
    const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
    const mk = (id, side) => {
      const template = structuredClone(base);
      template.id = id;
      template.name = id;
      return { combatant_id: id, side, position_ft: 5, state: S.buildState(template) };
    };
    const victim = mk("burned", "heroes"), helper = mk("helper", "heroes");
    const enemy = mk("source", "monsters");
    victim.state.timed_effects.push({
      effect_id: "burning", source_id: enemy.combatant_id,
      source_effect_id: "custom-fire", source_name: "Custom Fire Strike",
      end_of_turn_dice_count: 1, end_of_turn_dice_size: 6,
      end_of_turn_damage_type: "fire", expires_at_start_of_source_turn: false,
      allowed_removal_action_ids: ["douse-fire"],
    });
    victim.state.active_effect_ids.push("burning");
    return { victim, helper, enemy, setup: { heroes: [victim, helper], monsters: [enemy] } };
  } catch (error) { console.error("Douse scene failed", error); throw error; }
}

try {
  assert.ok(D && P, "Production Douse and Support modules must be loaded");
  {
    const { victim, helper, setup } = scene();
    assert.equal(D.choose(victim, setup), null);
    const oldHp = victim.state.current_hp;
    const event = D.resolve(1, 1, victim, victim);
    assert.equal(event.feature_id, "douse-fire");
    assert.match(event.description, /Custom Fire Strike/);
    assert.equal(E.available(victim.state, "action"), false);
    assert.deepEqual(victim.state.timed_effects, []);
    assert.equal(victim.state.active_effect_ids.includes("burning"), false);
    assert.equal(End.resolve(2, 1, victim, setup).events.length, 0);
    assert.equal(victim.state.current_hp, oldHp);
    assert.throws(() => D.resolve(3, 1, helper, victim), /Helper dousing/);
  }
  {
    const { victim, setup } = scene();
    const hp = victim.state.current_hp;
    assert.equal(D.choose(victim, setup), null);
    const result = P.resolve(1, 1, victim, setup, "1:burned");
    assert.equal(result.events.some(event => event.feature_id === "douse-fire"), false);
    assert.equal(victim.state.timed_effects.length, 1);
    assert.equal(E.available(victim.state, "action"), true);
    const tick = End.resolve(2, 1, victim, setup);
    assert.ok(tick.events.length > 0, "Burning must still damage without dousing");
    assert.ok(victim.state.current_hp < hp);
    assert.equal(victim.state.timed_effects.length, 1);
  }
  {
    const { victim, helper, setup } = scene();
    victim.state.timed_effects[0].allowed_removal_action_ids = [];
    assert.equal(D.choose(helper, setup), null);
    assert.throws(() => D.resolve(1, 1, helper, victim), /Helper dousing/);
    assert.equal(E.available(helper.state, "action"), true);
    victim.state.timed_effects[0].allowed_removal_action_ids = ["douse-fire"];
    victim.state.action_available = false;
    assert.equal(D.choose(victim, setup), null);
    assert.throws(() => D.resolve(1, 1, victim, victim), /available Action/);
  }
  console.log("Universal browser douse action and support integration passed");
} catch (error) {
  console.error("Universal browser Douse combat regression failed", error);
  process.exitCode = 1;
}
