(() => {
  "use strict";
  // Snapshot of docs/UNIVERSAL_MECHANIC_INVENTORY.md; update when inventory changes.
  // A capability is covered only by a declared matching preset assertion observed in a fight.
  const inventory = Object.freeze([{"id":"action-economy","status":"supported"},{"id":"archery-style","status":"supported"},{"id":"area-target-placement","status":"supported"},{"id":"attack-roll-advantage-disadvantage","status":"supported"},{"id":"auras","status":"supported"},{"id":"battlefield-exile","status":"supported"},{"id":"blinded","status":"supported"},{"id":"cleave-mastery","status":"supported"},{"id":"complete-condition-semantics","status":"partial"},{"id":"concentration","status":"supported"},{"id":"concentration-repeat-save-action","status":"supported"},{"id":"condition-immunity","status":"supported"},{"id":"condition-removal","status":"supported"},{"id":"cover-line-of-sight-obscurement","status":"partial"},{"id":"defense-style","status":"supported"},{"id":"deferred-save-effect","status":"supported"},{"id":"delayed-resource-refill","status":"supported"},{"id":"forced-movement-push-pull-teleport","status":"partial"},{"id":"generic-buff-debuff-modifier-stack","status":"partial"},{"id":"generic-death-triggers","status":"partial"},{"id":"generic-limited-use-resources","status":"partial"},{"id":"generic-reaction-trigger-grammar","status":"partial"},{"id":"grappled-restrained-escape","status":"supported"},{"id":"graze-mastery","status":"supported"},{"id":"great-weapon-fighting","status":"supported"},{"id":"healing","status":"supported"},{"id":"hp-threshold-condition","status":"supported"},{"id":"hp-threshold-instant-death","status":"supported"},{"id":"indomitable","status":"supported"},{"id":"initiative-resource-refill","status":"supported"},{"id":"legendary-actions","status":"supported"},{"id":"legendary-resistance","status":"supported"},{"id":"melee-ranged-range-bands","status":"supported"},{"id":"movement-modes-closing","status":"supported"},{"id":"multiattack-extra-attack","status":"supported"},{"id":"multiple-persistent-riders-on-one-attack","status":"unsupported"},{"id":"natural-1-natural-20-critical","status":"supported"},{"id":"nick-mastery","status":"supported"},{"id":"non-concentration-precombat-defense","status":"supported"},{"id":"one-slot-spell-per-turn","status":"supported"},{"id":"ongoing-periodic-damage","status":"supported"},{"id":"opportunity-attacks","status":"supported"},{"id":"parry-redirect-reactions","status":"supported"},{"id":"poisoned","status":"supported"},{"id":"prone","status":"supported"},{"id":"recharge","status":"supported"},{"id":"regeneration","status":"supported"},{"id":"sap-mastery","status":"supported"},{"id":"saving-throws","status":"supported"},{"id":"shield-ac","status":"supported"},{"id":"simultaneous-effect-ordering","status":"partial"},{"id":"simultaneous-save-shared-damage-roll","status":"supported"},{"id":"slow-mastery","status":"supported"},{"id":"spell-attack-rolls","status":"supported"},{"id":"standard-tactical-actions-dash-dodge-disengage-ready-help","status":"partial"},{"id":"summons-transformations-splitting","status":"unsupported"},{"id":"tactical-master","status":"supported"},{"id":"temporary-hit-points","status":"supported"},{"id":"timed-condition-lifecycle-repeat-save","status":"supported"},{"id":"topple-mastery","status":"supported"},{"id":"two-weapon-fighting","status":"supported"},{"id":"typed-damage-resistance-immunity-vulnerability","status":"supported"},{"id":"unarmed-grapple-shove-options","status":"partial"},{"id":"undead-fortitude","status":"supported"},{"id":"vex-mastery","status":"supported"},{"id":"zero-hp-death-lifecycle","status":"supported"}]);
  const evidence = Object.freeze({
    "concentration": [{kind:"concentration",value:true}],
    "grappled-restrained-escape": [{kind:"condition",value:"grappled"},{kind:"condition",value:"restrained"},{kind:"feature",value:"escape-grapple"}],
    "healing": [{kind:"event",value:"healing"}],
    "legendary-actions": [{kind:"text",value:"Legendary Action"}],
    "multiattack-extra-attack": [{kind:"feature",value:"extra-attack"}],
    "poisoned": [{kind:"condition",value:"poisoned"}],
    "prone": [{kind:"condition",value:"prone"}],
    "undead-fortitude": [{kind:"text",value:"Undead Fortitude"}],
  });
  function coverage(recipes, tests) {
    const observed = new Set();
    for (const row of tests) {
      if (row.result !== "PASS" || row.index !== 0) continue;
      const recipe = recipes.find((item) => item.id === row.name && item.ruleset === row.edition);
      if (!recipe) continue;
      for (const [capability, specs] of Object.entries(evidence)) {
        if (specs.some((spec) => recipe.aspects.some((claimed) =>
          claimed.kind === spec.kind && claimed.value === spec.value))) observed.add(capability);
      }
    }
    return inventory.map((item) => ({ ...item,
      coverage: observed.has(item.id) ? "asserted in passing preset" : "no asserted preset evidence",
    }));
  }
  window.IRON_PIT_BETA_GAUNTLET_COVERAGE = { inventory, evidence, coverage };
})();
