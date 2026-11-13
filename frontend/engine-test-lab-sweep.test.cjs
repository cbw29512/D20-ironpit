"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    const heroes = {h14a: {id: "h14a", ruleset: "2014"},
      h14b: {id: "h14b", ruleset: "2014"},
      h24: {id: "h24", ruleset: "2024"}};
    const monsters14 = {m14a: {id: "m14a", ruleset: "2014"},
      m14b: {id: "m14b", ruleset: "2014"}};
    const monsters24 = {m24: {id: "m24", ruleset: "2024"}};
    const recipes = [
      {id: "p14", title: "2014 preset", ruleset: "2014", seed: 77,
        hero_id: "h14b", monster_id: "m14a", aspects: [{kind: "attack"}]},
      {id: "p24", title: "2024 preset", ruleset: "2024", seed: 99,
        hero_id: "h24", monster_id: "m24", aspects: [{kind: "attack"}]},
    ];
    const context = {console, setTimeout};
    context.window = context;
    context.IRON_PIT_BROWSER_HEROES = heroes;
    context.IRON_PIT_BROWSER_MONSTERS_2014 = monsters14;
    context.IRON_PIT_BROWSER_MONSTERS = monsters24;
    context.IRON_PIT_BROWSER_CATALOG = {buildCatalog: async edition => ({
      heroes: [], monsters: edition === "2014" ?
        [{coverage_status: "raw_ready"}, {coverage_status: "blocked"}] :
        [{coverage_status: "raw_ready"}],
    })};
    context.IRON_PIT_COMBAT_PRESET_RECIPES = {recipes};
    context.IRON_PIT_COMBAT_PRESETS = {
      resolve: recipe => ({
        heroes: [{runnable_template_id: recipe.hero_id}],
        monsters: [{runnable_template_id: recipe.monster_id}],
      }),
      aspectFired: () => true,
    };
    context.IRON_PIT_BATTLE_LAB = {fingerprint: battle => JSON.stringify(battle)};
    context.IRON_PIT_BROWSER_TURBO = {
      deriveSeed: (seed, index) => (seed + index) >>> 0,
      runSeeded: (selection, seed) => {
        const hero = selection.hero_ids[0], monster = selection.monster_ids[0];
        if (hero === "h24") throw new Error("synthetic 2024 engine failure");
        const events = [{event_type: "attack", feature_id: "source-melee",
          damage_components: [{damage_type: "slashing"}]}];
        if (hero === "h14a" && monster === "m14b")
          events.push({event_type: "movement", movement_ft: 5});
        return {battle: {events, outcome: "heroes_win", rounds: 2},
          diagnostic_id: String(seed)};
      },
    };
    for (const file of ["engine-test-lab-sweep-plan.js",
      "engine-test-lab-sweep-runner.js"]) {
      vm.runInNewContext(fs.readFileSync(path.join(__dirname, file), "utf8"),
        context, {filename: file});
    }
    const plan = await context.IRON_PIT_TEST_ALL_PLAN.create("pairs");
    assert.equal(plan.duel_total, 5);
    assert.equal(plan.total, 7);
    assert.equal(plan.presets_count, 2);
    assert.equal(plan.unavailable["2014"], 1);
    assert.equal(plan.at(1).selection.hero_ids[0], "h14a");
    assert.equal(plan.at(1).selection.monster_ids[0], "m14b");
    assert.equal(plan.at(4).selection.ruleset, "2024");
    assert.equal(plan.at(5).kind, "preset");
    assert.equal(plan.at(5).seed, 77);

    const report = await context.IRON_PIT_TEST_ALL_RUNNER.run(
      plan, 123, {stopRequested: false}
    );
    assert.equal(report.completed, 7);
    assert.equal(report.failed, 3, "Movement and both 2024 failures remain visible.");
    assert.equal(report.passed, 4);
    assert.equal(report.skipped, 0);
    assert.ok(report.failures.some(row =>
      row.problems.includes("forbidden_tactical_movement")));
    assert.equal(report.by_edition["2024"].failed, 2);
    assert.ok(report.observed.feature_ids["source-melee"] >= 1);
    assert.equal(JSON.stringify(heroes.h14a), JSON.stringify({id:"h14a",ruleset:"2014"}));

    const presetsOnly = await context.IRON_PIT_TEST_ALL_PLAN.create("presets");
    assert.equal(presetsOnly.duel_total, 0);
    assert.equal(presetsOnly.total, 2);
    assert.equal(presetsOnly.at(0).selection.ruleset, "2014");
    assert.equal(presetsOnly.at(1).selection.ruleset, "2024");
    const presetResults = await context.IRON_PIT_TEST_ALL_RUNNER.run(
      presetsOnly, 123, {stopRequested: false}
    );
    assert.equal(presetResults.completed, 2);
    assert.equal(presetResults.passed, 1);
    assert.equal(presetResults.failed, 1);
    assert.ok(presetResults.failures[0].problems[0].startsWith("engine_error"));
    assert.equal(presetResults.failures[0].selection.ruleset, "2024");
    assert.equal(presetResults.failures[0].seed, 99);

    const quick = await context.IRON_PIT_TEST_ALL_PLAN.create("cards");
    assert.equal(quick.duel_total, 6);
    assert.equal(quick.total, 8);
    const stop = {stopRequested: false};
    const repeated = {mode:"cards", total:25,
      at: () => ({kind:"duel",label:"one duel",selection:{
        ruleset:"2014",hero_ids:["h14b"],monster_ids:["m14a"]}})};
    const partial = await context.IRON_PIT_TEST_ALL_RUNNER.run(
      repeated, 123, stop, status => {
        if (status.completed >= 20) stop.stopRequested = true;
      }
    );
    assert.equal(partial.completed, 20);
    assert.equal(partial.skipped, 5);
    assert.equal(partial.stopped, true);

    const html = fs.readFileSync(path.join(__dirname,"engine-test-lab.html"),"utf8");
    for (const id of ["sweep-run","sweep-stop","sweep-mode","sweep-status",
      "sweep-summary","sweep-download","sweep-evidence","sweep-failures"])
      assert.ok(html.includes(`id="${id}"`), `Missing sweep control: ${id}`);
    const scripts = [...html.matchAll(/<script defer src="([^"]+)"/g)]
      .map(match => match[1]);
    for (const file of ["engine-test-lab-sweep-plan.js",
      "engine-test-lab-sweep-runner.js","engine-test-lab-sweep-ui.js",
      "browser-wanted-2014.js","browser-wanted-posters.js"])
      assert.ok(scripts.includes(file), `Missing Test Lab dependency: ${file}`);
    assert.ok(scripts.indexOf("browser-wanted-2014.js") <
      scripts.indexOf("browser-wanted-posters.js"));
    assert.ok(scripts.indexOf("browser-wanted-posters.js") <
      scripts.indexOf("browser-catalog.js"));
    assert.ok(html.includes('value="presets" selected'),
      "Prebuilt fights must be the default scope, not an enormous roster matrix.");
    assert.ok(html.includes("Test All Fights"));
    for (const home of ["index.html"]) {
      const frontend = fs.readFileSync(path.join(__dirname, home), "utf8");
      const root = fs.readFileSync(path.join(__dirname, "..", home), "utf8");
      for (const page of [frontend, root]) {
        assert.match(page, /action="engine-test-lab\.html" method="get"/);
        assert.match(page, /name="run" value="presets"/);
      }
    }
    const controller = fs.readFileSync(path.join(__dirname,
      "engine-test-lab-sweep-ui.js"), "utf8");
    assert.ok(controller.includes('request.get("run") === "presets"'));
    assert.ok(scripts.indexOf("engine-test-lab-sweep-plan.js") <
      scripts.indexOf("engine-test-lab-sweep-ui.js"));
    console.log("Test All: both-edition complete matrix, presets, failures, stop and UI passed.");
  } catch (error) {
    console.error("Full roster test runner regression failed.", error);
    process.exitCode = 1;
  }
})();
