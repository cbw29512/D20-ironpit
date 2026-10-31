"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

global.window = globalThis;
vm.runInThisContext(fs.readFileSync(path.join(__dirname, "browser-attachments.js"), "utf8"),
  { filename: "browser-attachments.js" });
const A = window.IRON_PIT_BROWSER_ATTACHMENTS;

const sample = (source = "source-a", target = "target-a", effect = "feed") => ({
  source_id: source, target_id: target, effect_id: effect,
  damage_dice_count: 1, damage_dice_size: 4, damage_bonus: 3,
  damage_type: null, periodic_effect_kind: "direct_hp_loss",
  damage_timing: "source_turn_start", detach_after_hp_lost: 10,
});

{
  const initial = sample();
  const linked = A.attach([], initial);
  assert.equal(A.activeTarget(linked, "source-a", "feed"), "target-a");
  assert.equal(linked[0].damage_type, null);
  assert.equal(linked[0].damage_bonus, 3);
  assert.equal(linked[0].actual_hp_lost, 0);
  assert.equal(Object.prototype.hasOwnProperty.call(linked[0], "grappled"), false);
  assert.equal(Object.prototype.hasOwnProperty.call(linked[0], "speed_penalty"), false);
  const afterFour = A.recordHpLoss(linked, "source-a", "feed", 4);
  assert.equal(afterFour[0].actual_hp_lost, 4);
  assert.equal(linked[0].actual_hp_lost, 0, "fight state update cannot mutate prior snapshot");
  assert.deepEqual(A.recordHpLoss(afterFour, "source-a", "feed", 6), []);
  assert.deepEqual(A.recordHpLoss(linked, "source-a", "feed", 0), linked);
  assert.deepEqual(A.detachForCombatant(linked, "source-a"), []);
  assert.deepEqual(A.detachForCombatant(linked, "target-a"), []);
  assert.deepEqual(A.detach(linked, "source-a", "feed"), []);
  assert.deepEqual(A.linkedEffects(linked), [
    { owner_id: "target-a", counterpart_id: "source-a", effect_id: "attached", kind: "debuff" },
    { owner_id: "source-a", counterpart_id: "target-a", effect_id: "feed", kind: "buff" },
  ]);
}

{
  const typed = A.attach([], { ...sample("synthetic", "other", "effect"),
    damage_type: "necrotic", periodic_effect_kind: "typed_damage",
    detach_after_hp_lost: null });
  assert.equal(typed[0].periodic_effect_kind, "typed_damage");
  assert.equal(typed[0].damage_type, "necrotic");
  assert.deepEqual(A.recordHpLoss(typed, "synthetic", "effect", 4)[0].actual_hp_lost, 4);
  assert.equal(A.activeTarget(typed, "synthetic", "effect"), "other");
}

// Invalid source semantics must fail closed, rather than silently attach a grapple.
{
  const invalid = [
    { ...sample(), damage_type: "piercing" },
    { ...sample(), periodic_effect_kind: "unknown" },
    { ...sample(), detach_after_hp_lost: -1 },
    { ...sample(), damage_dice_count: 0 },
    { ...sample(), periodic_effect_kind: "typed_damage" },
    { ...sample(), source_id: "target-a" },
  ];
  const prior = console.error;
  console.error = () => {}; // Failure is intentionally asserted; avoid noisy expected-error logs.
  try {
    for (const invalidEntry of invalid) assert.throws(() => A.attach([], invalidEntry));
    assert.throws(() => A.attach(A.attach([], sample()), sample()));
    assert.throws(() => A.recordHpLoss(A.attach([], sample()), "source-a", "feed", -1));
  } finally { console.error = prior; }
}

// Homebrew/renamed source parameters must not alter the underlying engine behavior.
const renamed = A.attach([], sample("homebrew", "target-two", "custom-label"));
assert.deepEqual(A.recordHpLoss(renamed, "homebrew", "custom-label", 10), []);
console.log("Universal browser attachment state and lifecycle tests passed.");
