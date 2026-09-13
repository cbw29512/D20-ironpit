"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;
const load = (name) => vm.runInThisContext(fs.readFileSync(path.join(__dirname, name), "utf8"), { filename: name });
for (const file of ["browser-action-economy.js", "browser-state.js", "browser-zero-hp.js", "browser-ongoing-damage.js", "browser-attachments.js"]) load(file);

const capabilityRows = JSON.parse(fs.readFileSync(path.join(__dirname, "../backend/app/content/data/combatant_capabilities_riders_v1.json"), "utf8"));
const stirge = capabilityRows.find((row) => row.id === "srd-stirge");
const sourceEffect = stirge.attacks[0].effects.find((effect) => effect.kind === "attachment");
const attack = {
  id: stirge.attacks[0].id,
  attachmentOnHit: {
    periodicDamageCount: sourceEffect.periodic_damage_count,
    periodicDamageSize: sourceEffect.periodic_damage_size,
    periodicDamageBonus: sourceEffect.periodic_damage_bonus,
    periodicDamageType: sourceEffect.periodic_damage_type,
    forbidsSourceAttackIds: sourceEffect.forbids_source_attack_ids,
    detachableBySourceMovementFt: sourceEffect.detachable_by_source_movement_ft,
    detachableByTargetAction: sourceEffect.detachable_by_target_action,
    detachableByAdjacentAction: sourceEffect.detachable_by_adjacent_action,
  },
};

const template = (id, name, side, hp = 20) => ({ id, name, kind: side === "monsters" ? "monster" : "character", size: "medium", max_hp: hp, speed_ft: 30, damage_resistances: [], damage_vulnerabilities: [], damage_immunities: [], traits: [] });
const member = (id, name, side, position, hp) => ({ combatant_id: id, side, position_ft: position, state: window.IRON_PIT_BROWSER_STATE.buildState(template(id, name, side, hp)) });
const stirgeMember = member("stirge", "Stirge", "monsters", 5, 5);
const target = member("target", "Target", "heroes", 0, 30);
const ally = member("ally", "Ally", "heroes", 5, 30);
const enemy = member("enemy", "Enemy", "monsters", 0, 30);
const setup = { heroes: [target, ally], monsters: [stirgeMember, enemy] };

assert.equal(window.IRON_PIT_BROWSER_ATTACHMENTS.apply(stirgeMember.state, "stirge", "target", attack, 1), true);
assert.equal(window.IRON_PIT_BROWSER_ATTACHMENTS.attackAvailable(stirgeMember.state, attack), false);
assert.equal(stirgeMember.state.attachment.detachable_by_source_movement_ft, 5);

window.IRON_PIT_DICE = { roll: () => 4 };
const tick = window.IRON_PIT_BROWSER_ATTACHMENTS.startTurn(1, 2, stirgeMember, setup);
assert.equal(tick.events[0].damage_roll.total, 8);
assert.equal(target.state.current_hp, 22);

window.IRON_PIT_BROWSER_STATE.beginTurn(enemy.state);
assert.equal(window.IRON_PIT_BROWSER_ATTACHMENTS.detachAction(2, 2, enemy, setup), null, "AI must not spend an Action detaching an opponent's attachment");
window.IRON_PIT_BROWSER_STATE.beginTurn(ally.state);
const detached = window.IRON_PIT_BROWSER_ATTACHMENTS.detachAction(2, 2, ally, setup);
assert.ok(detached, "adjacent ally must be able to detach the Stirge");
assert.equal(ally.state.action_available, false);
assert.equal(stirgeMember.state.attachment, null);

window.IRON_PIT_BROWSER_ATTACHMENTS.apply(stirgeMember.state, "stirge", "target", attack, 3);
stirgeMember.state.movement_remaining_ft = 10;
const selfDetach = window.IRON_PIT_BROWSER_ATTACHMENTS.detachBySourceMovement(3, 3, stirgeMember);
assert.equal(selfDetach.movement_ft, 5);
assert.equal(stirgeMember.state.movement_remaining_ft, 5);
assert.equal(stirgeMember.state.attachment, null);

console.log("Browser universal attachment lifecycle regressions passed.");
