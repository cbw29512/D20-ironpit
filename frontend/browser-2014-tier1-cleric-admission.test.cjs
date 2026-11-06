"use strict";

const assert = require("node:assert/strict");
require("./browser-test-runtime.cjs").loadWebsite();
require("./browser-catalog.js");
require("./battle-lab.js");
require("./browser-turbo.js");

try {
  const caster = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-acolyte"];
  assert.ok(caster, "Source-complete low-level Cleric must enter the 2014 combat roster");
  assert.deepEqual((caster.spell_save_actions || []).map(a => a.id), ["sacred-flame"]);
  assert.deepEqual(
    (caster.defensive_spell_actions || []).map(a => a.id).sort(),
    ["bless", "sanctuary"],
  );
  assert.deepEqual((caster.healingActions || []).map(a => a.id), ["cure-wounds"]);
  assert.equal(caster.resources["spell-slot-1"], 3, "Slot counts must match the printed 2014 source");
  assert.ok(caster.attacks.some(a => a.name === "Club"));
  const hero = Object.values(window.IRON_PIT_BROWSER_HEROES).find(
    h => h.ruleset === "2014" && h.class_id === "fighter" && h.level === 5
  );
  assert.ok(hero, "A certified 2014 Fighter is required for real browser combat");

  // Independently prove the source-backed monster can select a real cantrip
  // with its generic spell engine after its three leveled slots are exhausted.
  const State = window.IRON_PIT_BROWSER_STATE;
  const Policy = window.IRON_PIT_BROWSER_SPELL_POLICY;
  assert.ok(State && Policy, "The universal state/spell policy must be loaded");
  const actor = {
    combatant_id: "source-cleric", side: "monsters", position_ft: 0,
    state: State.buildState(structuredClone(caster)),
  };
  const target = {
    combatant_id: "fighter", side: "heroes", position_ft: 5,
    state: State.buildState(structuredClone(hero)),
  };
  const scene = { heroes: [target], monsters: [actor] };
  State.beginTurn(actor.state);
  actor.state.resources["spell-slot-1"] = 0;
  const spell = Policy.choose(actor, scene, "1:source-cleric");
  assert.ok(spell, "The generic spell policy must find a legal spell Action");
  assert.equal(spell.action.id, "sacred-flame");
  assert.equal(spell.slotLevel, 0, "A cantrip must not spend a depleted spell slot");

  for (const count of [1, 3]) {
    const selection = {
      ruleset: "2014",
      hero_ids: Array(count).fill(hero.id),
      monster_ids: Array(count).fill("2014-acolyte"),
    };
    const snapshot = JSON.stringify(caster);
    const seeded = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261106 + count).battle;
    const repeat = window.IRON_PIT_BROWSER_TURBO.runSeeded(selection, 20261106 + count).battle;
    assert.deepEqual(repeat.events, seeded.events, "The same source and seed must replay");
    assert.equal(seeded.setup.monsters.length, count);
    assert.ok(seeded.events.length > 0, "Shared combatants must execute turns");
    assert.equal(JSON.stringify(caster), snapshot, "Printed source cannot mutate during a fight");
  }
  console.log("2014 Acolyte: shared four-spell profile and deterministic browser fights passed");
} catch (error) {
  console.error("2014 source-backed low-level Cleric regression failed", error);
  process.exitCode = 1;
}
