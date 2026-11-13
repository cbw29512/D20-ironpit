"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    const context = {console, setTimeout};
    context.window = context;
    Object.assign(context, {
      IRON_PIT_BROWSER_FORMATION_ENGAGEMENT: {weaponTargetAllowed: () => true},
      IRON_PIT_BROWSER_FORMATION_AREA_TARGETING: {coneFrontlineTargets: () => []},
      IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH: {resolvePending: () => ({})},
      IRON_PIT_BROWSER_BREAKABLE_CONDITION_OBJECT: {preferFreshLimitedControl: () => true},
      IRON_PIT_BROWSER_TARGET_CHOSEN_SAVE: {choose: () => "dex"},
    });
    context.IRON_PIT_BROWSER_HEROES = {
      h24: {id:"h24",ruleset:"2024",kind:"character"},
    };
    context.IRON_PIT_BROWSER_MONSTERS = {
      m24: {id:"m24",ruleset:"2024",kind:"monster"},
    };
    context.IRON_PIT_BROWSER_TURBO = {
      deriveSeed: (seed, index) => (seed + index) >>> 0,
      runSeeded: () => {throw new Error("synthetic runtime outage");},
    };
    context.IRON_PIT_BATTLE_LAB = {
      fingerprint: battle => JSON.stringify(battle),
    };
    for (const file of [
      "engine-test-lab-sweep-report.js",
      "engine-test-lab-sweep-runner.js",
    ]) {
      vm.runInNewContext(fs.readFileSync(path.join(__dirname, file), "utf8"),
        context, {filename:file});
    }
    const plan = {mode:"pairs",total:300,
      editions:[{edition:"2024",hero_ids:["h24"],monster_ids:["m24"]}],
      at: () => ({kind:"duel",label:"fixture duel",
        selection:{ruleset:"2024",hero_ids:["h24"],monster_ids:["m24"]}}),
    };
    const run = context.IRON_PIT_TEST_ALL_RUNNER.run;
    const cached = context.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT;
    delete context.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT;
    await assert.rejects(run(plan, 123, {stopRequested:false}),
      /missing shared browser runtimes: formation attack/);
    context.IRON_PIT_BROWSER_FORMATION_ENGAGEMENT = cached;
    const large = await run(plan, 123, {stopRequested:false});
    assert.equal(large.failed, 300);
    assert.equal(large.passed, 0);
    assert.equal(large.failures.length, 100);
    assert.equal(large.failure_cases.length, 300);
    assert.equal(large.failure_codebook.length, 1);
    assert.equal(large.error_counts[large.failure_codebook[0]], 300);
    assert.ok(large.failure_cases.every(row => row.length === 2));
    assert.equal(large.source_rosters[0].hero_ids[0],"h24");
    assert.equal(large.processed,300);
    const resumed = await run(plan, 123, {startIndex:290,stopRequested:false});
    assert.equal(resumed.start_case,291);
    assert.equal(resumed.completed,300);
    assert.equal(resumed.processed,10);
    assert.equal(resumed.skipped,290);
    assert.equal(resumed.failure_cases[0][0],291);
    assert.equal(resumed.failure_cases.at(-1)[0],300);
    console.log("Bounded Test All 300-failure evidence and resumption passed.");
  } catch (error) {
    console.error("Bounded Test All report regression failed",error);
    process.exitCode=1;
  }
})();
