"use strict";
const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();

const S = window.IRON_PIT_BROWSER_STATE;
const M = window.IRON_PIT_BROWSER_MULTIATTACK;
const C = window.IRON_PIT_BROWSER_SWALLOW;
const G = window.IRON_PIT_BROWSER_GRAPPLE;
const A = window.IRON_PIT_BROWSER_SWALLOW_ACTION;
const base = window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];

function dice(rolls) {
  try {
    const pending = [...rolls];
    return {
      roll(sides) {
        const value = pending.shift();
        if (!Number.isInteger(value) || value < 1 || value > sides)
          throw new Error(`Unexpected d${sides} roll: ${value}`);
        return value;
      },
      rollMany(count, sides) {
        return Array.from({length: count}, () => this.roll(sides));
      },
    };
  } catch (error) {
    console.error("Containment deterministic dice failed.", error);
    throw error;
  }
}

function scene(size = "medium", name = "Cavern Hold") {
  try {
    const hero = structuredClone(base);
    Object.assign(hero, {id: "test-victim", name: "Victim", size, max_hp: 200,
      armor_class: 5, damage_resistances: [], damage_immunities: [],
      condition_immunities: [], traits: [], weapon_masteries: []});
    const monster = structuredClone(hero);
    Object.assign(monster, {id: "test-source", name: "Attacker", size: "large"});
    const slam = {id: "slam", weaponId: "slam", name: "Slam", kind: "melee",
      bonus: 15, diceCount: 2, diceSize: 8, damageBonus: 4,
      damageType: "bludgeoning", reach: 5, onHitDamage: [], animation: "strike"};
    monster.attacks = [slam];
    monster.primary_attack_id = slam.id;
    monster.attack_action = {id: "shared-two-hit", name: "Multiattack",
      slots: [{attackIds: ["slam"]}, {attackIds: ["slam"]}], variants: []};
    monster.swallowActions = [{sourceName: name, attackId: "slam",
      deliveryMode: "attack_sequence", requiresExistingGrapple: true,
      requiredSequenceHits: 2, sequenceGrappleDc: 14, maxTargetSize: "medium",
      damageDiceCount: 2, damageDiceSize: 8, damageBonus: 4,
      damageType: "bludgeoning", startTurnSaveAbility: "constitution",
      startTurnSaveDc: 14, maxSwallowed: 1, exitMovementFt: 0,
      exitProne: false, cannotBreathe: true, movesWithSource: true}];
    const source = {combatant_id: "source", side: "monsters", position_ft: 0,
      state: S.buildState(monster)};
    const victim = {combatant_id: "victim", side: "heroes", position_ft: 5,
      state: S.buildState(hero)};
    return {source, victim, setup: {heroes: [victim], monsters: [source], ruleset: "2014"}};
  } catch (error) {
    console.error("Containment browser fight setup failed.", error);
    throw error;
  }
}

try {
  assert.ok(S && M && C && G && A, "Universal combat runtimes required");
  {
    const {source, victim, setup} = scene();
    window.IRON_PIT_DICE = dice([16, 2, 2, 16, 2, 2]);
    const result = M.resolveAttackAction(1, 1, source, setup);
    assert.equal(result.events.filter(e => e.event_type === "attack" && e.hit).length, 2);
    const applied = result.events.find(e => e.feature_id === "Cavern Hold");
    assert.ok(applied && applied.description.includes("Cavern Hold"));
    assert.equal(victim.state.swallowed.source_name, "Cavern Hold");
    assert.equal(victim.state.swallowed.damage_bonus, 4);
    assert.equal(victim.state.swallowed.cannot_breathe, true);
    assert.equal(victim.state.swallowed.moves_with_source, true);
    assert.equal(victim.state.action_available, true);
    assert.equal(source.state.action_available, false);
    const hp = victim.state.current_hp;
    window.IRON_PIT_DICE = dice([20]);
    const saved = C.sourceTurnDamage(4, 2, source, setup);
    assert.equal(saved.events.length, 1);
    assert.equal(saved.events[0].save_succeeded, true);
    assert.equal(victim.state.current_hp, hp);
    window.IRON_PIT_DICE = dice([2, 2, 2]);
    const failed = C.sourceTurnDamage(5, 3, source, setup);
    assert.equal(failed.events[0].save_succeeded, false);
    assert.equal(failed.events[0].damage_components[0].total, 8);
    assert.equal(victim.state.current_hp, hp - 8);
    source.state.is_alive = false; source.state.is_dead = true; source.state.current_hp = 0;
    assert.deepEqual(C.cleanup(setup), ["victim"]);
    assert.equal(victim.state.swallowed, null);
    assert.equal(victim.state.active_effect_ids.includes("prone"), false);
  }
  {
    const {source, victim, setup} = scene("medium", "Different Label");
    window.IRON_PIT_DICE = dice([16, 2, 2, 1]);
    M.resolveAttackAction(1, 1, source, setup);
    assert.equal(victim.state.swallowed, null, "A miss cannot complete two-hit containment");
  }
  {
    const {source, victim, setup} = scene("large");
    window.IRON_PIT_DICE = dice([16, 2, 2, 16, 2, 2]);
    M.resolveAttackAction(1, 1, source, setup);
    assert.equal(victim.state.swallowed, null, "Oversize targets cannot be engulfed");
  }
  {
    const {source, victim, setup} = scene();
    G.apply(victim.state, "source", 14, 5);
    const selected = A.choose(source, setup);
    assert.ok(selected && selected.action.deliveryMode === "attack_sequence");
    window.IRON_PIT_DICE = dice([]);
    const result = A.resolve(1, 1, source, setup, "1:source", "victim", "slam");
    assert.equal(result.events.length, 1);
    assert.equal(result.events[0].event_type, "feature");
    assert.equal(victim.state.swallowed.source_name, "Cavern Hold");
    assert.equal(source.state.action_available, false);
  }
  console.log("Shared browser two-hit containment / source-turn saves / held action passed.");
} catch (error) {
  console.error("Universal browser two-hit containment failed.", error);
  process.exitCode = 1;
}