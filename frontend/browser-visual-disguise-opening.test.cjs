"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
global.window = globalThis;
const load = name => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"));
window.IRON_PIT_BROWSER_PRECOMBAT_SPELLS = { choose: () => null };
window.IRON_PIT_BROWSER_TIMED_SELF_BUFFS = { active: () => false };
window.IRON_PIT_BROWSER_SELECTABLE_DAMAGE_RESISTANCE = {};
window.IRON_PIT_ACTION_ECONOMY = {
  available: (state, cost) => cost === "bonus_action"
    ? Boolean(state.bonus_action_available && !state.is_dead && !state.is_unconscious)
    : Boolean(state.action_available),
  spend: (state, cost) => {
    if (!window.IRON_PIT_ACTION_ECONOMY.available(state, cost)) throw Error("Unavailable");
    if (cost === "bonus_action") state.bonus_action_available = false;
    else state.action_available = false;
  },
};
load("browser-precombat-buffs.js");
const P = window.IRON_PIT_BROWSER_PRECOMBAT_BUFFS;
const action = {
  id: "visual-disguise", name: "Renamed Illusion",
  activationCost: "action", dismissalCost: "bonus_action",
  openingEligible: true, openingPriority: 20, concealsTrueForm: true,
  dismissOnFirstTurn: true, inspectionAbility: "intelligence", inspectionDc: 16,
  investigationRevealsTrueForm: false,
  magicalIllusion: true, endsIfOwnerDead: true, physicalInspectionInconsistent: true,
  inspectionCost: "action", inspectionSkill: "investigation",
};
const template = { name: "Renamed Monster", max_hp: 40, timed_self_buff_actions: [],
  visualDisguiseAction: action };
const fresh = () => ({
  combatant_id: "source", side: "monsters",
  state: { template, current_hp: 40, is_dead: false, is_unconscious: false,
    magical_visual_disguise_active: false, opening_buff_id: null,
    turns_started: 0, action_available: true, bonus_action_available: true },
});
const member = fresh(), setup = { heroes: [], monsters: [member] };
const selected = P.choose(member, setup);
assert.equal(selected.kind, "visual-disguise");
const opening = P.prepare(setup, 1);
assert.equal(opening.events.length, 1);
assert.equal(opening.events[0].round_number, 0);
assert.equal(member.state.magical_visual_disguise_active, true);
assert.equal(member.state.opening_buff_id, action.id);
assert.equal(member.state.bonus_action_available, true);
assert.equal(member.state.action_available, true);
assert.equal(P.prepare(setup, 2).events.length, 0, "Only one opening buff.");
member.state.turns_started = 1;
member.state.bonus_action_available = false;
assert.equal(P.dismissFirstTurn(member, 2, 1), null);
assert.equal(member.state.magical_visual_disguise_active, true);
member.state.bonus_action_available = true;
const reveal = P.dismissFirstTurn(member, 2, 1);
assert.equal(reveal.event_type, "feature");
assert.match(reveal.description, /Bonus Action/);
assert.equal(member.state.bonus_action_available, false);
assert.equal(member.state.action_available, true);
assert.equal(member.state.magical_visual_disguise_active, false);
assert.equal(P.dismissFirstTurn(member, 3, 1), null);
assert.equal(fresh().state.magical_visual_disguise_active, false);
assert.equal(template.visualDisguiseAction.inspectionDc, 16);
const pregenAction = { ...action, name: "Pregen Arcane Mask", dismissalCost: "action",
  inspectionDc: 19 };
const pregen = fresh();
pregen.combatant_id = "pregen";
pregen.state.template = { ...template, kind: "character", visualDisguiseAction: pregenAction };
P.resolve(10, pregen, { heroes: [pregen], monsters: [] }, { kind: "visual-disguise", value: pregenAction });
pregen.state.turns_started = 1;
const pregenResult = P.dismissFirstTurn(pregen, 11, 1);
assert.equal(pregenResult.feature_id, pregenAction.id);
assert.match(pregenResult.description, /using an Action/);
assert.equal(pregen.state.action_available, false);
assert.equal(pregen.state.bonus_action_available, true);
assert.equal(pregenAction.inspectionDc, 19);
assert.equal(action.inspectionDc, 16);
const second = fresh();
P.resolve(1, second, { heroes: [], monsters: [second] }, { kind: "visual-disguise", value: action });
second.state.turns_started = 1;
second.state.is_unconscious = true;
assert.equal(P.dismissFirstTurn(second, 2, 1), null);
assert.equal(second.state.magical_visual_disguise_active, true);
console.log("Source-neutral visual disguise opening, one buff, Bonus Action, and immutable form passed.");
