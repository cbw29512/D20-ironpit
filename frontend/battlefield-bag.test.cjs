"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();

(async () => {
  try {
    for (const file of [
      "custom-monster-runtime.js", "battle-lab.js", "browser-turbo.js",
      "browser-audit.js", "browser-execution.js",
      "engine-test-lab-punching-bag.js", "engine-test-lab-bag-coverage.js",
      "battlefield-bag-report.js", "battlefield-bag-runner.js",
      "figure-portraits.js",
    ]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"),
      {filename: file});

    const heroes = window.IRON_PIT_BROWSER_HEROES;
    const before = JSON.stringify(heroes);
    const fighters = Object.fromEntries(["2014", "2024"].map(edition => {
      const runtime = Object.values(heroes).find(hero =>
        hero.ruleset === edition && hero.class_id === "fighter" && hero.level === 1);
      assert.ok(runtime, "Missing canonical fighter " + edition);
      return [edition, {
        name: runtime.name, ruleset: edition, kind: "character",
        level: 1, coverage_status: "raw_ready",
        runnable_template_id: runtime.id,
      }];
    }));
    const reportApi = window.IRON_PIT_BATTLEFIELD_BAG_REPORT;
    const runner = window.IRON_PIT_BATTLEFIELD_BAG_RUNNER;
    const bag = runner.bagCard("2014");
    assert.equal(bag.coverage_status, "custom_ready");
    assert.equal(bag.compiled_template.max_hp, 10000);
    assert.equal(bag.compiled_template.armor_class, 10);
    // Both entrypoints compile the same full-stat Punching Bag template.
    for (const edition of ["2014", "2024"]) {
      const template = runner.bagCard(edition).compiled_template;
      for (const ability of ["strength", "dexterity", "constitution",
        "intelligence", "wisdom", "charisma"]) {
        assert.equal(template.ability_scores[ability], 10);
        assert.equal(template.saving_throw_bonuses[ability], 1);
      }
      assert.equal(template.skill_bonuses.athletics, 0);
      assert.equal(template.skill_bonuses.acrobatics, 0);
    }
    assert.equal(bag.compiled_template.attacks[0].fixedDamage, 0);
    assert.equal(window.IRON_PIT_FIGURE_PORTRAITS.keyFor(bag.compiled_template, {}),
      "heavy_bag", "The real card renderer must use the bag silhouette.");

    const page = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
    const root = fs.readFileSync(path.join(__dirname, "../index.html"), "utf8");
    for (const html of [page, root]) {
      assert.match(html, /id="bag-all-button"/);
      assert.match(html, /id="bag-all-progress"/);
      assert.match(html, /id="bag-stop-button"/);
      assert.match(html, /id="bag-download-button"/);
      assert.doesNotMatch(html, /name="run" value="bag"/);
      const order = ["custom-monster-runtime.js", "engine-test-lab-punching-bag.js",
        "engine-test-lab-bag-coverage.js", "battlefield-bag-report.js",
        "battlefield-bag-runner.js", "battlefield-bag-controls.js", "app.js"];
      let index = -1;
      for (const filename of order) {
        const position = html.indexOf('src="' + filename + '"');
        assert.ok(position > index, filename + " must load in dependency order.");
        index = position;
      }
    }

    let loaded = null, plays = 0, writes = 0, results = 0;
    global.document = {getElementById: () => ({textContent: ""})};
    window.requestAnimationFrame = callback => setImmediate(callback);
    window.IRON_PIT_BATTLEFIELD_REPLAY = {
      play: async (battle, slots, options) => {
        assert.equal(options.instant, true);
        assert.deepEqual(slots, {heroes: [0], monsters: [0]});
        assert.ok(battle.events.length);
        plays += 1;
      },
    };
    window.IRON_PIT_BATTLEFIELD_VIEW = {
      writeLog(battle) { assert.ok(battle.events.length); writes += 1; },
      showResult(battle) { assert.ok(battle.outcome); results += 1; },
    };
    const state = {ruleset: "2014", catalog: null, fighting: false, session: null,
      hasRun: false};
    const api = {
      state, updateControls() {},
      async ensureRuleset(edition) {
        state.ruleset = edition;
        state.catalog = {ruleset: edition, heroes: [fighters[edition]]};
      },
      load(heroCards, monsterCards) {
        assert.equal(heroCards.length, 1);
        assert.equal(monsterCards.length, 1);
        loaded = {heroCards, monsterCards};
      },
      matchup() {
        const hero = loaded.heroCards[0], monster = loaded.monsterCards[0];
        return {
          heroes: {cards: [hero], indexes: [0]},
          monsters: {cards: [monster], indexes: [0]},
          error: null,
          selection: {
            ruleset: hero.ruleset, hero_ids: [hero.runnable_template_id],
            monster_ids: [monster.runnable_template_id],
            compiled_monsters: {[monster.runnable_template_id]: monster.compiled_template},
          },
        };
      },
    };
    const control = {running: false, stopRequested: false};
    const report = await runner.run(api, control);
    assert.equal(report.total, 2);
    assert.equal(report.completed, 2);
    assert.equal(report.cases.length, 2);
    assert.equal(plays, 2);
    assert.equal(writes, 2);
    assert.equal(results, 2);
    assert.equal(report.skipped, 0);
    assert.equal(report.stopped, false);
    assert.ok(report.cases.every(row => row.event_count > 0));
    assert.ok(report.cases.every(row => Array.isArray(row.events)));
    // User-provided 480-fight report found 2,038 forbidden movement events.
    // The actual player-facing Test All runner must never produce those
    // events in either 2014 or 2024 standard Pit combat.
    assert.equal(report.failed, 0, "Both formation gauntlet fights must pass.");
    assert.ok(report.cases.every(row => row.events.every(
      event => event.event_type !== "movement")),
    "Formation-only gauntlet must not move combatants between grid cells.");
    assert.equal(JSON.stringify(heroes), before);
    assert.equal(state.fighting, false);

    plays = 0;
    const stop = {running: false, stopRequested: false};
    const partial = await runner.run(api, stop, progress => {
      if (progress.completed === 1) stop.stopRequested = true;
    });
    assert.equal(partial.completed, 1);
    assert.equal(partial.skipped, 1);
    assert.equal(partial.stopped, true);
    assert.equal(plays, 1);

    const failure = reportApi.create(1, 12345);
    const entry = fighters["2014"];
    const attempted = window.IRON_PIT_EXECUTION.resolveReplay({
      ruleset: "2014", hero_ids: [entry.runnable_template_id],
      monster_ids: [bag.runnable_template_id],
      compiled_monsters: {[bag.runnable_template_id]: bag.compiled_template},
    }, 9841, {heroes: [0], monsters: [0]});
    reportApi.failure(failure, entry, 9841, new Error("render failed"), attempted);
    assert.ok(failure.cases[0].event_count > 0,
      "UI failures must still preserve the full real combat event log.");
    console.log("Player battlefield 1v1 Punching Bag suite, reports, stop and art passed.");
  } catch (error) {
    console.error("Player-facing pregen vs Punching Bag regression failed", error);
    process.exitCode = 1;
  }
})();