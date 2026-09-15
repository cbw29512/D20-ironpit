"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

global.window = globalThis;

const load = (name) => {
  try {
    vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"),
      { filename: name },
    );
  } catch (error) {
    console.error(`Failed to load ${name} for Death Dog browser parity.`, error);
    throw error;
  }
};

try {
  const certificationManifest = JSON.parse(fs.readFileSync(
    path.join(__dirname, "..", "data", "monster_certification_manifest.json"),
    "utf8",
  ));

  const deathDogCertification = certificationManifest.monsters.find(
    (monster) => monster.runtime_template_id === "srd-death-dog",
  );
  assert.ok(deathDogCertification, "Death Dog must exist in the canonical certification manifest");
  assert.equal(deathDogCertification.public_ready_status, "ready");
  assert.deepEqual(deathDogCertification.blockers, []);

  load("browser-monsters-generated.js");
  const deathDog = window.IRON_PIT_BROWSER_MONSTERS["srd-death-dog"];
  assert.ok(deathDog, "Certified Death Dog must be present in the generated browser roster");

  const bite = deathDog.attacks.find((attack) => attack.name === "Bite");
  assert.ok(bite, "Death Dog Bite must be present in the generated browser template");
  assert.deepEqual(bite.onHitSavingThrow, {
    saveAbility: "constitution",
    dc: 12,
    magicalEffect: false,
    targetFilter: {
      excludedCreatureTypes: [],
      excludedTags: [],
    },
    failureEffects: [
      {
        kind: "condition",
        condition: "poisoned",
      },
    ],
  });

  console.log("Death Dog browser parity preserves DC 12 Constitution -> Poisoned and omits out-of-match 24-hour lifecycle.");
} catch (error) {
  console.error("Death Dog browser parity regression failed.", error);
  process.exitCode = 1;
}
