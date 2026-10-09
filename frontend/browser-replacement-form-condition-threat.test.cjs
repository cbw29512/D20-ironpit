"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
global.window = globalThis;
const load = (filename) => vm.runInThisContext(
  fs.readFileSync(path.join(__dirname, filename), "utf8"), { filename },
);
const stats = {
  strength: 12, dexterity: 12, constitution: 12,
  intelligence: 12, wisdom: 12, charisma: 12,
};
const source = {
  id: "test-shape", name: "Protective Beast", kind: "monster",
  ability_scores: stats, saving_throw_bonuses: { wisdom: 3 },
  skill_bonuses: {}, condition_immunities: ["stunned", "paralyzed"],
  resources: {}, source: "certified test form", max_hp: 12,
};
const defender = {
  combatant_id: "caster", side: "heroes", position_ft: 0,
  state: {
    is_alive: true, is_dead: false, current_hp: 8,
    template: {
      id: "caster", kind: "character", ruleset: "2024", max_hp: 30,
      archetype: "druid", ability_scores: stats,
      saving_throw_bonuses: { wisdom: 2 }, skill_bonuses: {},
      resources: {}, condition_immunities: [], source: "test",
    },
  },
};
const rider = { effectId: "stunned" };
const action = {
  id: "stun", actionCost: "action", maxTargets: 1,
  saveAbility: "wisdom", dc: 30, range: 60,
  failedSaveTimedEffect: rider,
};
const enemy = {
  combatant_id: "enemy", side: "monsters", position_ft: 10,
  state: {
    is_alive: true, is_dead: false, current_hp: 23,
    resources: { "spell-slot-3": 1 },
    template: { saving_throw_actions: [action], spell_save_actions: [] },
  },
};
const setup = { heroes: [defender], monsters: [enemy] };
const form = {
  id: "shape", aiUsePolicy: "emergency_only", formTemplateId: "test-shape",
  hpMode: "retain_owner",
};
window.IRON_PIT_BROWSER_STATE = {
  distance: (left, right) => Math.abs(left.position_ft - right.position_ft),
};
window.IRON_PIT_BROWSER_MONSTERS = { "test-shape": source };
window.IRON_PIT_BROWSER_CONDITION_RULES = {
  incapacitated: () => false, canSee: () => true,
};
window.IRON_PIT_BROWSER_SAVES = { legalAction: () => true };
window.IRON_PIT_BROWSER_RESOURCES = {
  available: (state, id, cost = 1) => (state.resources[id] || 0) >= cost,
};
window.IRON_PIT_BROWSER_OFFENSE_VALUE = {
  saveSuccess: (target) => target.state.template.saving_throw_bonuses.wisdom >= 15 ? 0.9 : 0.1,
};
window.IRON_PIT_BROWSER_CONDITION_IMMUNITY = {
  immune: (state, condition) => (state.template.condition_immunities || []).includes(condition),
};
window.IRON_PIT_BROWSER_SPELLCASTING = {
  legalSlotLevels: (state, _turn, level) => (
    level === 0 || (state.resources["spell-slot-" + level] || 0) > 0 ? [level] : []
  ),
};
window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
  legalSingleTargets: () => [defender],
};
load("browser-replacement-form-compiler.js");
load("browser-spell-area.js");
load("browser-replacement-form-condition-threat.js");
const policy = window.IRON_PIT_BROWSER_REPLACEMENT_FORM_CONDITION_THREAT;
assert.equal(policy.formMitigates(defender, setup, form), true);
assert.equal(enemy.state.current_hp, 23, "No combat state changes during forecast");
source.condition_immunities = [];
assert.equal(policy.formMitigates(defender, setup, form), false, "HP alone cannot stop Stunned");
source.saving_throw_bonuses.wisdom = 15;
assert.equal(policy.formMitigates(defender, setup, form), true, "A materially improved save is protection");
source.saving_throw_bonuses.wisdom = 3;
rider.effectId = "frightened";
assert.equal(policy.formMitigates(defender, setup, form), false, "Do not treat every condition as Incapacitated");
rider.effectId = "stunned";
source.condition_immunities = ["stunned", "paralyzed"];
enemy.position_ft = 200;
assert.equal(policy.formMitigates(defender, setup, form), false, "Out of range is not a threat");
enemy.position_ft = 10;
enemy.state.template.saving_throw_actions = [];
enemy.state.template.spell_save_actions = [{
  ...action, id: "hold", level: 3, targetCount: 1,
  failedSaveTimedEffect: { effectId: "paralyzed" },
}];
assert.equal(policy.formMitigates(defender, setup, form), true, "Legal single-target spells are forecast");
enemy.state.resources["spell-slot-3"] = 0;
assert.equal(policy.formMitigates(defender, setup, form), false, "No resource, no spell threat");
enemy.state.resources["spell-slot-3"] = 1;
setup.heroes.push({
  combatant_id: "ally", side: "heroes", position_ft: 0,
  state: { is_alive: true, is_dead: false, current_hp: 10 },
});
assert.equal(policy.formMitigates(defender, setup, form), false, "Do not invent enemy focus fire");
console.log("Universal protective-form disabling-save forecast passed.");

{
  // Area-control threat can be predicted in a group, but must use the
  // resolver's legal/selected placement, not arbitrary possible coverage.
  source.condition_immunities = ["paralyzed", "stunned"];
  enemy.state.is_dead = false;
  enemy.position_ft = 30;
  enemy.state.resources["spell-slot-3"] = 1;
  const group = setup.heroes;
  assert.equal(group.length, 2);
  const area = {
    id: "area-paralysis", name: "Area paralysis", level: 3,
    actionCost: "action", range: 60, targetCount: 1,
    saveAbility: "wisdom", dc: 30,
    area: { origin: "point", shape: "radius", radiusFt: 5 },
    failedSaveTimedEffect: { effectId: "paralyzed" },
  };
  let selected = [{ enemyIds: [defender.combatant_id, group[1].combatant_id], friendlyIds: [] }];
  window.IRON_PIT_BROWSER_SPELL_POLICY_SUPPORT = {
    legalSingleTargets: () => [defender],
    effectiveRange: (_state, distance) => distance,
    protectedUniversalPlacements: () => selected,
    areaSpellProtection: () => ({ ids: new Set(), limit: 0 }),
  };
  enemy.state.template.spell_save_actions = [area];
  assert.equal(policy.formMitigates(defender, setup, form), true,
    "Use the actually chosen area containing the defender");
  selected = [{ enemyIds: [group[1].combatant_id], friendlyIds: [] }];
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "No condition threat if the chosen area misses the defender");
  selected = [];
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "No legal area placement means no threat");
  enemy.state.template.spell_save_actions = [{
    ...area, area: undefined, areaRadius: 10,
    failedSaveTimedEffect: { effectId: "stunned" },
  }];
  assert.equal(policy.formMitigates(defender, setup, form), true,
    "Legacy radius uses the shared ally-safe area placement");
  enemy.position_ft = 200;
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "Legacy area must also be in casting range");
  enemy.position_ft = 30;
  enemy.state.resources["spell-slot-3"] = 0;
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "Unavailable spell slots still prohibit a disabling area threat");
}
console.log("Area disabling-save threat parity passed.");

{
  // An actual printed, non-spell area Action uses the shared selector,
  // including its resource gate and filtered target list.
  const group = setup.heroes;
  enemy.state.resources["spell-slot-3"] = 1;
  source.condition_immunities = ["stunned"];
  enemy.position_ft = 10;
  enemy.state.is_dead = false;
  const action = {
    id: "printed-area-stun", name: "Stun cloud", actionCost: "action",
    saveAbility: "wisdom", dc: 30, range: 60,
    resourceId: "spell-slot-3", resourceCost: 1,
    area: { origin: "point", shape: "radius", radiusFt: 5 },
    failedSaveTimedEffect: { effectId: "stunned" },
  };
  let chosen = [{ targetIds: [defender.combatant_id, group[1].combatant_id],
    friendlyIds: [], enemyIds: [defender.combatant_id, group[1].combatant_id] }];
  window.IRON_PIT_BROWSER_AREA_TARGETING = { legalPlacements: () => chosen };
  load("browser-area-save-actions.js");
  enemy.state.template.spell_save_actions = [];
  enemy.state.template.saving_throw_actions = [action];
  assert.equal(policy.formMitigates(defender, setup, form), true,
    "The chosen printed Action area can stun this grouped defender");
  chosen = [{ targetIds: [group[1].combatant_id],
    friendlyIds: [], enemyIds: [group[1].combatant_id] }];
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "A selected area that omits the defender is not a threat");
  chosen = [];
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "No legal placement cannot disable the defender");
  chosen = [{ targetIds: [defender.combatant_id],
    friendlyIds: [], enemyIds: [defender.combatant_id] }];
  enemy.state.resources["spell-slot-3"] = 0;
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "Spent source resources prohibit the printed area Action");
  enemy.state.resources["spell-slot-3"] = 1;
  action.failedSaveTimedEffect = null;
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "Printed area without a severe rider must not gain condition threat value");
  action.failedSaveTimedEffect = { effectId: "stunned" };
  assert.equal(policy.formMitigates(defender, setup, form), true);
  action.requiresTargetHearing = true;
  defender.state.active_effect_ids = ["deafened"];
  window.IRON_PIT_BROWSER_SAVES.legalAction = (source, target) =>
    !source.requiresTargetHearing || !target.state.active_effect_ids?.includes("deafened");
  assert.equal(policy.formMitigates(defender, setup, form), false,
    "Printed area must respect target hearing legality");
  defender.state.active_effect_ids = [];
  delete action.requiresTargetHearing;
  window.IRON_PIT_BROWSER_SAVES.legalAction = () => true;
  assert.equal(enemy.state.resources["spell-slot-3"], 1,
    "A lookahead may not consume the source's resource");
}
console.log("Printed non-spell area disabling-save parity passed.");
