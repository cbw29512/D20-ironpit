"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of [
  "browser-heroes.js", "browser-monsters.js", "browser-monsters-2014.js",
  "browser-unarmed-opportunity.js", "browser-condition-immunity.js", "browser-condition-rules.js",
  "browser-action-economy.js", "browser-grapple.js", "browser-debuff-counters.js",
  "browser-movement-mode-policy.js", "browser-modifiers.js", "browser-state.js", "browser-rage.js",
  "browser-rolls.js", "browser-timed-conditions.js", "browser-zero-hp.js", "browser-ability-hooks.js",
  "browser-attack-outcome.js", "browser-attack.js", "browser-reactions.js",
]) load(file);

const S = window.IRON_PIT_BROWSER_STATE;
const X = window.IRON_PIT_BROWSER_REACTIONS;
const P = window.IRON_PIT_BROWSER_MOVEMENT_MODE_POLICY;
const M = window.IRON_PIT_BROWSER_MODIFIERS;
const FLYBY_IDS = ["2014-flying-snake", "2014-giant-owl", "2014-owl", "2014-pteranodon"];
const PRINTED = {
  "2014-flying-snake": "The snake doesn't provoke opportunity attacks when it flies out of an enemy's reach.",
  "2014-giant-owl": "The owl doesn't provoke opportunity attacks when it flies out of an enemy's reach.",
  "2014-owl": "The owl doesn't provoke opportunity attacks when it flies out of an enemy's reach.",
  "2014-pteranodon": "The pteranodon doesn’t provoke an opportunity attack when it flies out of an enemy’s reach.",
};
const WALK_FT = { "2014-flying-snake": 30, "2014-giant-owl": 5, "2014-owl": 5, "2014-pteranodon": 10 };

const heroTemplate = () => structuredClone(window.IRON_PIT_BROWSER_HEROES["karnok-stoneward-l1"]);
const flyerTemplate = (id) => {
  const template = structuredClone(window.IRON_PIT_BROWSER_MONSTERS_2014[id]);
  template.opportunity_attack_exempt_movement_modes = P.exemptModesFromTraitText(PRINTED[id]);
  return template;
};
const member = (id, side, template, position) => ({
  combatant_id: id, side, position_ft: position, state: S.buildState(template),
});
const dice = () => {
  window.IRON_PIT_DICE = {
    roll: (sides) => (sides === 20 ? 19 : 1),
    rollMany: (count, sides) => Array.from({ length: count }, () => (sides === 20 ? 19 : 1)),
  };
};

function setupFlyer(monsterId, movementMode) {
  const hero = member("hero-1", "heroes", heroTemplate(), 5);
  const monster = member("monster-1", "monsters", flyerTemplate(monsterId), 0);
  S.beginTurn(monster.state);
  monster.state.active_movement_mode = movementMode;
  S.beginTurn(hero.state);
  return { hero, monster, fight: { heroes: [hero], monsters: [monster] } };
}

{
  assert.deepEqual(P.exemptModesFromTraitText("<p><em><strong>Flyby.</strong></em></p>"), []);
  assert.deepEqual(
    P.exemptModesFromTraitText("doesn't provoke opportunity attacks when it swims out of an enemy's reach."),
    ["swim"],
  );
  for (const id of FLYBY_IDS) {
    assert.deepEqual(P.exemptModesFromTraitText(PRINTED[id]), ["fly"]);
    const template = flyerTemplate(id);
    assert.deepEqual(template.opportunity_attack_exempt_movement_modes, ["fly"]);
    assert.equal(template.movement_modes.fly_ft, 60);
    assert.equal(template.source_trait_names.includes("Flyby"), true);
  }
}

{
  for (const id of FLYBY_IDS) {
    const state = S.buildState(flyerTemplate(id));
    S.beginTurn(state);
    assert.equal(state.active_movement_mode, "fly");
    assert.equal(M.effectiveSpeed(state), 60);
    assert.equal(state.movement_remaining_ft, 60);
    state.active_movement_mode = "walk";
    assert.equal(M.effectiveSpeed(state), WALK_FT[id]);
  }
}

{
  for (const id of FLYBY_IDS) {
    dice();
    const flying = setupFlyer(id, "fly");
    assert.equal(X.opportunityAttackWeapon(flying.hero, flying.monster, 5, 10, "speed"), null);
    assert.equal(flying.hero.state.reaction_available, true);
    dice();
    const walking = setupFlyer(id, "walk");
    const weapon = X.opportunityAttackWeapon(walking.hero, walking.monster, 5, 10, "speed");
    assert.ok(weapon);
    const event = X.resolveOpportunityAttack(1, 1, walking.hero, walking.monster, walking.fight, 5, 10, "speed");
    assert.ok(event);
    assert.equal(event.feature_id, "opportunity-attack");
    assert.equal(walking.hero.state.reaction_available, false);
  }
}
