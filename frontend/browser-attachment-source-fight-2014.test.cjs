"use strict";
// Proof: immutable 2014 source attack -> Python compiler -> browser serializer ->
// production browser attack, turn scheduler, shared HP loss, detach and event stream.
// The synthetic durable body is NOT an admitted Stirge or a replacement source card.
const assert = require("node:assert/strict");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
require("./browser-test-runtime.cjs").loadWebsite();

let printedAttack;
try {
  const script = [
    "import json",
    "from app.content.monster_source_2014 import load_monster_source_2014",
    "from app.content.monster_definition_adapter_2014 import _attack",
    "from app.content.capability_attack_compiler import compile_attack",
    "from scripts.browser_template_serializer import attack_row",
    "source = next(row for row in load_monster_source_2014() if row.id == 'stirge')",
    "compiled = compile_attack(_attack(source, source.attacks[0]))",
    "print(json.dumps(attack_row(compiled, set())))",
  ].join("\n");
  const projectRoot = path.resolve(__dirname, "..");
  printedAttack = JSON.parse(execFileSync("python", ["-c", script], {
    cwd: projectRoot,
    encoding: "utf8",
    env: { ...process.env, PYTHONPATH: "backend:scripts" },
  }));
} catch (error) {
  console.error("Pinned 2014 attack failed to compile for browser fight", error);
  throw error;
}
assert.equal(printedAttack.name, "Blood Drain");
assert.equal(printedAttack.bonus, 5);
assert.deepEqual(
  [printedAttack.diceCount, printedAttack.diceSize, printedAttack.damageBonus],
  [1, 4, 3],
);
assert.equal(printedAttack.onHitAttachment.periodic_effect_kind, "direct_hp_loss");
assert.equal(printedAttack.onHitAttachment.auto_end_after_hp_loss, 10);

// The real source attack is installed on a durable generic monster shell
// solely so fight-length is sufficient to witness recurrent owner-turn events.
const shell = window.IRON_PIT_BROWSER_MONSTERS_2014["2014-commoner"];
assert.ok(shell, "Certified browser 2014 Commoner fixture is required.");
const template = structuredClone(shell);
template.id = "2014-attachment-live-fixture";
template.name = "Source-Linked Attachment Fixture";
template.max_hp = 100;
template.armor_class = 14;
template.attacks = [printedAttack];
template.primary_attack_id = printedAttack.id;
template.attack_action = null;
const original = structuredClone(template);
const dice = {
  roll(sides) { return Math.min(18, sides); },
  rollMany(count, sides) { return Array.from({ length: count }, () => this.roll(sides)); },
};
window.IRON_PIT_DICE = dice;
let battle;
try {
  battle = window.IRON_PIT_BROWSER_ENGINE.runEncounter({
    ruleset: "2014",
    hero_ids: ["karnok-stoneward-2014-l5"],
    monster_ids: [template.id],
    compiled_monsters: { [template.id]: template },
  });
} catch (error) {
  console.error("Complete browser source-linked attachment fight failed", error);
  throw error;
}
const changes = battle.events.flatMap(event => event.attachment_changes || []);
assert.ok(changes.some(row => row.operation === "attach"), "Source hit must create a real link.");
const ownerDrains = battle.events.filter(event =>
  event.feature_id === "Blood Drain" && /Hit Points \\(not damage\\)/.test(event.description));
if (!ownerDrains.length) {
  console.error("Attachment fight missing source-turn drain", {
    outcome: battle.outcome, rounds: battle.rounds,
    events: battle.events.filter(event => event.round_number > 0
      && ["attack", "feature", "movement", "dodge", "victory"].includes(event.event_type))
      .slice(0, 90).map(event => ({
        round: event.round_number, actor: event.actor_id, type: event.event_type,
        feature: event.feature_id, hit: event.hit, hp: event.hp_after,
        changes: event.attachment_changes, description: event.description?.slice(0, 125),
      })),
  });
}
assert.ok(ownerDrains.length, "Owner turn must drain HP through the production scheduler.");
assert.ok(changes.some(row => row.operation === "detach"), "Fight must include attachment expiry.");
assert.ok(battle.events.some(event => event.event_type === "victory" || event.event_type === "draw"));
assert.deepEqual(battle.setup.attachments, [], "No dead-source/target linked status survives fight.");
assert.deepEqual(template, original, "Immutable source-derived card must not mutate.");
console.log("Pinned 2014 source attack completed browser fight with linked status and detachment.");
