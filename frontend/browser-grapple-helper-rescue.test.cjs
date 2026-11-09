"use strict";

// A synthetic source card defines the same generic parameter shape that
// 2014 Whelm now exports. Neither selection nor resolver dispatches by name.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const State = window.IRON_PIT_BROWSER_STATE;
  const Hero = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
  assert.ok(Hero);
  const make = (id, side, position) => ({
    combatant_id: id, side, position_ft: position,
    state: State.buildState(structuredClone(Hero)),
  });
  const rule = {
    source_action_id: "synthetic-undertow", source_name: "Undertow",
    check_ability: "strength", check_dc: 14, helper_range_ft: 5,
    action_cost: "action",
  };
  const helper = make("helper", "heroes", 5);
  const held = make("held", "heroes", 0);
  const owner = make("owner", "monsters", 0);
  owner.state.template.grapple_rescue_rules = [rule];
  const setup = {heroes: [helper, held], monsters: [owner]};
  const G = window.IRON_PIT_BROWSER_GRAPPLE;
  const Rescue = window.IRON_PIT_BROWSER_GRAPPLE_HELPER_RESCUE;
  assert.ok(Rescue);

  const attach = () => G.apply(held.state, owner.combatant_id, 14, 0, true,
    false, null, {effectId: "synthetic-undertow"});
  attach();
  assert.deepEqual(Rescue.choose(helper, setup), {owner, target: held, rule});
  held.state.grapple_sources[0].linked_effect_id = "different-action";
  assert.equal(Rescue.choose(helper, setup), null);
  held.state.grapple_sources[0].linked_effect_id = "synthetic-undertow";
  assert.deepEqual(Rescue.choose(helper, setup), {owner, target: held, rule});
  const dice = window.IRON_PIT_DICE, originalRoll = dice.roll;
  try {
    dice.roll = (sides) => sides === 20 ? 1 : 2;
    const failed = Rescue.resolve(1, 1, helper, held, owner, rule, setup);
    assert.equal(failed.check_succeeded, false);
    assert.equal(failed.check_dc, 14);
    assert.equal(helper.state.action_available, false);
    assert.ok(held.state.grapple_sources.length);
    helper.state.action_available = true;
    dice.roll = (sides) => sides === 20 ? 20 : 2;
    const success = Rescue.resolve(2, 2, helper, held, owner, rule, setup);
    assert.equal(success.check_succeeded, true);
    assert.equal(success.feature_id, "synthetic-undertow");
    assert.match(success.description, /Undertow/);
    assert.deepEqual(held.state.grapple_sources, []);
    assert.ok(!held.state.active_effect_ids.includes("grappled"));
    assert.ok(!held.state.active_effect_ids.includes("restrained"));
    helper.state.action_available = true;
    attach();
    helper.position_ft = 15;
    assert.equal(Rescue.choose(helper, setup), null);
    assert.throws(() => Rescue.resolve(3, 3, helper, held, owner, rule, setup),
      /illegal/i);
  } finally {
    dice.roll = originalRoll;
  }
  console.log("Universal source-owned third-party Grapple rescue passed.");
} catch (error) {
  console.error("Universal helper rescue regression failed", error);
  process.exitCode = 1;
}
