"use strict";

const assert = require("node:assert/strict");
const test = require("node:test");
require("./browser-test-runtime.cjs").loadWebsite();

function execute(kind, label) {
  const source = kind === "monster"
    ? window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]
    : window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"];
  const template = structuredClone(source);
  template.id = "synthetic-attacker";
  template.kind = kind;
  template.name = "Synthetic";
  template.attacks = [{
    id: "synthetic-claw", name: label, kind: "melee",
    bonus: 5, diceCount: 2, diceSize: 6, damageBonus: 2,
    damageType: "bludgeoning", reach: 5, animation: "slash",
  }];
  template.primary_attack_id = "synthetic-claw";
  template.weapon_masteries = [];
  template.traits = [];
  const targetTemplate = structuredClone(window.IRON_PIT_BROWSER_MONSTERS["srd-goblin-warrior"]);
  targetTemplate.id = "synthetic-target";
  targetTemplate.armor_class = 10;
  targetTemplate.max_hp = 100;
  const attacker = {combatant_id: "attacker", side: kind === "monster" ? "monsters" : "heroes",
    position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(template)};
  const target = {combatant_id: "target", side: "monsters", position_ft: 5,
    state: window.IRON_PIT_BROWSER_STATE.buildState(targetTemplate)};
  const rolls = [15, 4, 5];
  window.IRON_PIT_DICE = {
    roll(sides) { const v = rolls.shift(); assert.ok(v >= 1 && v <= sides); return v; },
    rollMany(count, sides) { return Array.from({length: count}, () => this.roll(sides)); },
  };
  const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
    1, 1, attacker, target, template.attacks[0], 5, {spendAction: false},
  );
  return {hit: event.hit, damage: event.damage_roll.total, hp: target.state.current_hp};
}

test("renamed monster and character attacks use identical browser combat rules", () => {
  assert.deepEqual(execute("monster", "Tail"), execute("character", "Imaginary Coil"));
});

const fs = require("node:fs");
const path = require("node:path");

test("actual compiled form browser rows match Python combat outcomes", () => {
  const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, "browser-form-runtime-parity-fixture.json"), "utf8"));
  for (const item of fixture.cases) {
    const actor = {
      combatant_id: "attacker", side: item.kind === "monster" ? "monsters" : "heroes",
      position_ft: 0, state: window.IRON_PIT_BROWSER_STATE.buildState(item.attacker),
    };
    const target = {
      combatant_id: "target", side: item.kind === "monster" ? "heroes" : "monsters",
      position_ft: 5, state: window.IRON_PIT_BROWSER_STATE.buildState(item.defender),
    };
    const rolls = [15, 4, 5];
    window.IRON_PIT_DICE = {
      roll(sides) { const v = rolls.shift(); assert.ok(v >= 1 && v <= sides); return v; },
      rollMany(count, sides) { return Array.from({length: count}, () => this.roll(sides)); },
    };
    const event = window.IRON_PIT_BROWSER_ATTACK.resolveAttack(
      1, 1, actor, target, actor.state.template.attacks[0], 5, {spendAction: false},
    );
    assert.deepEqual(
      {hit: event.hit, damage: event.damage_roll.total, hp: target.state.current_hp},
      item.expected, `Python/browser divergence for ${item.kind}`,
    );
  }
});

test("compiled custom monster completes a full browser encounter", () => {
  const fixture = JSON.parse(fs.readFileSync(path.join(__dirname, "browser-form-runtime-parity-fixture.json"), "utf8"));
  const monster = fixture.cases.find(item => item.kind === "monster").attacker;
  const hero = structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
  const monsterId = "form-custom-monster-full-fight";
  const heroId = "form-custom-hero-full-fight";
  const roster = window.IRON_PIT_BROWSER_MONSTERS_2014;
  assert.equal(monster.ruleset, "2014");
  assert.equal(hero.ruleset, "2014");
  try {
    roster[monsterId] = {...structuredClone(monster), id: monsterId};
    window.IRON_PIT_BROWSER_HEROES[heroId] = {...hero, id: heroId};
    window.IRON_PIT_DICE = {
      roll: sides => sides === 20 ? 15 : 3,
      rollMany: (count, sides) => Array.from({length: count}, () => sides === 20 ? 15 : 3),
    };
    const battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
      ruleset: "2014", hero_ids: [heroId], monster_ids: [monsterId],
    });
    assert.notEqual(battle.outcome, "active");
    assert.ok(battle.events.some(item => item.event_type === "attack"));
    assert.equal(battle.setup.monsters[0].state.template.id, monsterId);
  } finally {
    delete roster[monsterId];
    delete window.IRON_PIT_BROWSER_HEROES[heroId];
  }
});
