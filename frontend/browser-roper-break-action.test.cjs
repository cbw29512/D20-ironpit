"use strict";
// Synthetic renamed source: the ordinary Grapple-rescue Action breaks an object.
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const hero = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-2014-l5"];
  assert.ok(hero, "A source-certified Strength-check hero is required.");
  const State = window.IRON_PIT_BROWSER_STATE;
  const Grapple = window.IRON_PIT_BROWSER_GRAPPLE;
  const Rescue = window.IRON_PIT_BROWSER_GRAPPLE_HELPER_RESCUE;
  const make = (id, side, position_ft) => ({
    combatant_id: id, side, position_ft,
    state: State.buildState(structuredClone(hero)),
  });
  const owner = make("owner", "monsters", 0);
  const held = make("held", "heroes", 40);
  const ally = make("ally", "heroes", 45);
  const rule = {
    source_action_id: "synthetic-snare", source_name: "Renamed Snare",
    check_ability: "strength", check_dc: 15, helper_range_ft: 5,
    helper_range_anchor: "held_target", allow_held_target: true,
    requires_breakable_object: true, release_verb: "break",
    action_cost: "action",
  };
  owner.state.template.grapple_rescue_rules = [rule];
  const setup = { heroes: [held, ally], monsters: [owner] };
  const attach = () => Grapple.apply(held.state, owner.combatant_id, 15, 50,
    true, false, null, {
      effectId: "synthetic-snare",
      checkSaveDisadvantageAbilities: ["strength"],
      breakableObject: {
        armorClass: 20, hitPoints: 10, damageVulnerabilities: [],
        damageImmunities: ["poison", "psychic"],
      },
    });

  attach();
  assert.equal(held.state.grapple_sources[0].linked_effect_id, rule.source_action_id);
  assert.equal(Rescue.eligible(held, held, owner, rule), true);
  assert.equal(Rescue.eligible(ally, held, owner, rule), true);
  assert.deepEqual(Rescue.choose(ally, setup), {owner, target: held, rule});
  ally.position_ft = 55;
  assert.equal(Rescue.eligible(ally, held, owner, rule), false);
  ally.position_ft = 45;
  const originalRoll = window.IRON_PIT_DICE.roll;
  try {
    window.IRON_PIT_DICE.roll = (sides) => sides === 20 ? 20 : 1;
    const event = Rescue.resolve(1, 1, ally, held, owner, rule, setup);
    assert.equal(event.check_succeeded, true);
    assert.equal(event.check_dc, 15);
    assert.equal(event.feature_id, "synthetic-snare");
    assert.match(event.description, /break.*Renamed Snare/);
    assert.equal(ally.state.action_available, false);
    assert.deepEqual(held.state.grapple_sources, []);
    assert.ok(!held.state.active_effect_ids.includes("grappled"));
    assert.ok(!held.state.active_effect_ids.includes("restrained"));
    assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", rule.source_action_id), 1);
    attach();
    assert.equal(Rescue.eligible(held, held, owner, rule), true);
    const self = Rescue.resolve(2, 2, held, held, owner, rule, setup);
    assert.equal(self.check_succeeded, true);
    assert.equal(held.state.action_available, false);
    assert.deepEqual(held.state.grapple_sources, []);
    assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", rule.source_action_id), 2);
    State.beginTurn(owner.state);
    assert.equal(Grapple.sourceGrappleCapacityUsed(setup, "owner", rule.source_action_id), 0);
  } finally {
    window.IRON_PIT_DICE.roll = originalRoll;
  }
  console.log("Generic held/ally Grapple Break Action parity passed.");
} catch (error) {
  console.error("Generic held/ally Grapple Break Action failed.", error);
  throw error;
}
