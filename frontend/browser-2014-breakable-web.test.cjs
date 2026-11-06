"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

try {
  const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
  const State = window.IRON_PIT_BROWSER_STATE;
  const Attack = window.IRON_PIT_BROWSER_ATTACK;
  const Timed = window.IRON_PIT_BROWSER_TIMED;
  const Break = window.IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT;
  const hero = Object.values(window.IRON_PIT_BROWSER_HEROES).find(
    h => h.ruleset === "2014" && h.class_id === "fighter" && h.level === 5,
  );
  assert.ok(hero && State && Attack && Timed && Break);

  const fixture = {
    "2014-giant-spider": { bonus: 5, dc: 12, size: null },
    "2014-ettercap": { bonus: 4, dc: 11, size: "large" },
  };
  const originalDice = window.IRON_PIT_DICE;
  const dice = (number) => ({
    roll: (sides) => Math.min(number, sides),
    rollMany: (count, sides) => Array.from({ length: count }, () => Math.min(number, sides)),
  });
  for (const [id, expected] of Object.entries(fixture)) {
    const card = roster[id];
    assert.ok(card, id + " must be source-admitted");
    const web = card.attacks.find(a => a.name === "Web");
    assert.ok(web, id + " Web must be a real ranged attack");
    assert.equal(web.kind, "ranged");
    assert.equal(web.bonus, expected.bonus);
    assert.equal(web.normal, 30);
    assert.equal(web.long, 60);
    assert.equal(web.fixedDamage, 0);
    assert.equal(web.resourceId, "web");
    assert.equal(card.resources.web, 1);
    assert.ok(card.recharge_rules.some(r => r.resourceId === "web" && r.minimumRoll === 5));
    assert.equal(web.controlEffect.conditionId, "restrained");
    assert.equal(web.controlEffect.escapeCheckDc, expected.dc);
    assert.equal(web.controlEffect.maxTargetSize || null, expected.size);
    assert.equal(web.controlEffect.breakableObject.hitPoints, 5);

    const source = { combatant_id: "source", side: "monsters", position_ft: 0,
      state: State.buildState(structuredClone(card)) };
    const target = { combatant_id: "hero", side: "heroes", position_ft: 25,
      state: State.buildState(structuredClone(hero)) };
    const setup = { heroes: [target], monsters: [source], ruleset: "2014" };
    State.beginTurn(source.state);
    window.IRON_PIT_DICE = dice(1);
    const missed = Attack.resolveAttack(1, 1, source, target, web, 25, { setup });
    assert.equal(missed.hit, false, "natural 1 must miss");
    assert.equal(target.state.timed_effects.length, 0);
    assert.equal(source.state.resources.web, 0, "misses spend rechargeable shots");

    // Fresh fight must reset source template resources and all conditions.
    const attacker = { ...source, state: State.buildState(structuredClone(card)) };
    const victim = { ...target, state: State.buildState(structuredClone(hero)) };
    const battle = { heroes: [victim], monsters: [attacker], ruleset: "2014" };
    State.beginTurn(attacker.state);
    window.IRON_PIT_DICE = dice(18);
    const result = Attack.resolveAttack(2, 1, attacker, victim, web, 25, { setup: battle });
    assert.equal(result.hit, true);
    const object = victim.state.timed_effects.find(e => e.effect_id === "restrained");
    assert.ok(object, "successful ranged hit creates canonical Restrained");
    assert.equal(object.escape_check_dc, expected.dc);
    assert.equal(object.breakable_object.current_hp, 5);
    assert.equal(victim.state.current_hp, hero.max_hp, "Web has no damage type or damage");
    assert.equal(attacker.state.resources.web, 0);
    assert.deepEqual(Break.damage(victim.state, object, 9, 9, "fire"), {
      appliedDamage: 0, destroyed: false,
    });
    assert.deepEqual(Break.damage(victim.state, object, 20, 9, "poison"), {
      appliedDamage: 0, destroyed: false,
    });
    assert.deepEqual(Break.damage(victim.state, object, 20, 2, "fire"), {
      appliedDamage: 4, destroyed: false,
    });
    assert.deepEqual(Break.damage(victim.state, object, 20, 1, "piercing"), {
      appliedDamage: 1, destroyed: true,
    });
    assert.ok(!victim.state.active_effect_ids.includes("restrained"));
    assert.ok(!victim.state.timed_effects.some(e => e.effect_id === "restrained"));
    assert.equal(card.resources.web, 1, "source card remains immutable");
  }
  window.IRON_PIT_DICE = originalDice;
  console.log("2014 Giant Spider / Ettercap universal breakable ranged Web passed");
} catch (error) {
  console.error("2014 shared Web attack regression failed.", error);
  process.exitCode = 1;
}