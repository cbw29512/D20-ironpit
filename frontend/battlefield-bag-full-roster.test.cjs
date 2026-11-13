"use strict";
// End-to-end, memory-bounded player Test All acceptance for all 480 pregens.
// Uses real engine + real player gauntlet reporter; only UI drawing is stubbed.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    require("./browser-test-runtime.cjs").loadWebsite();
    for (const file of [
      "custom-monster-runtime.js", "battle-lab.js", "browser-turbo.js",
      "browser-audit.js", "browser-execution.js",
      "engine-test-lab-punching-bag.js", "engine-test-lab-bag-coverage.js",
      "battlefield-bag-report.js", "battlefield-bag-runner.js",
    ]) {
      vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), {
        filename: file,
      });
    }

    // Data schema: one source-backed, ready hero card per class, level, edition.
    const source = window.IRON_PIT_BROWSER_HEROES;
    const entries = Object.values(source).map(hero => ({
      name: hero.name, ruleset: hero.ruleset, kind: "character",
      class_id: hero.class_id, level: hero.level,
      coverage_status: "raw_ready", runnable_template_id: hero.id,
    }));
    for (const edition of ["2014", "2024"]) {
      assert.equal(entries.filter(card => card.ruleset === edition).length, 240,
        "Expected the complete 12-class x 20-level " + edition + " roster.");
    }
    const original = JSON.stringify(source);
    const state = {ruleset: "2014", catalog: null, fighting: false,
      session: null, hasRun: false};
    let loaded = null, casesInspected = 0, battlesRendered = 0;
    const violations = [];
    global.document = {getElementById: () => ({textContent: ""})};
    window.requestAnimationFrame = done => setImmediate(done);
    window.IRON_PIT_BATTLEFIELD_REPLAY = {
      async play(battle, _slotMap, options) {
        assert.equal(options.instant, true);
        assert.ok(battle.events.length, "Real combat events are required.");
        battlesRendered += 1;
      },
    };
    window.IRON_PIT_BATTLEFIELD_VIEW = {
      writeLog(battle) { assert.ok(battle.events.length); },
      showResult(battle) { assert.ok(battle.outcome); },
    };

    // State logic: the real runner switches editions, loads one fighter and
    // the compiled bag, resolves a seeded encounter, records, then advances.
    const api = {
      state,
      updateControls() {},
      async ensureRuleset(edition) {
        state.ruleset = edition;
        state.catalog = {ruleset: edition, heroes: entries.filter(
          card => card.ruleset === edition)};
      },
      load(heroCards, monsterCards) {
        assert.equal(heroCards.length, 1);
        assert.equal(monsterCards.length, 1);
        loaded = {hero: heroCards[0], bag: monsterCards[0]};
      },
      matchup() {
        assert.ok(loaded, "The real gauntlet must load combatant cards.");
        const hero = loaded.hero, bag = loaded.bag;
        return {heroes: {cards: [hero], indexes: [0]},
          monsters: {cards: [bag], indexes: [0]}, error: null,
          selection: {ruleset: hero.ruleset,
            hero_ids: [hero.runnable_template_id],
            monster_ids: [bag.runnable_template_id],
            compiled_monsters: {[bag.runnable_template_id]: bag.compiled_template}}};
      },
    };
    const control = {running: false, stopRequested: false};
    const report = await window.IRON_PIT_BATTLEFIELD_BAG_RUNNER.run(
      api, control, progress => {
        // Inspect every report row, then discard verbose events to keep the
        // 480-fight CI run bounded in memory; production export is unchanged.
        while (casesInspected < progress.cases.length) {
          const row = progress.cases[casesInspected++];
          if (row.problems.length || row.events.some(
            event => event.event_type === "movement")) {
            violations.push({edition: row.edition, card: row.card_id,
              problems: row.problems});
          }
          row.events = [];
        }
      },
    );
    assert.equal(report.total, 480);
    assert.equal(report.completed, 480);
    assert.equal(report.skipped, 0);
    assert.equal(report.stopped, false);
    assert.equal(battlesRendered, 480);
    assert.equal(JSON.stringify(source), original, "Source heroes must remain immutable.");
    assert.equal(state.fighting, false);
    assert.deepEqual(violations.slice(0, 20), [],
      "The full real battlefield pregen sweep has failing combat cases.");
    assert.equal(report.failed, 0,
      "All 480 player-facing Punching Bag fights must have no rule violations.");
    console.log("Player battlefield full-roster Punching Bag: 480/480 passed.");
  } catch (error) {
    console.error("Full-roster player battlefield Punching Bag audit failed", error);
    process.exitCode = 1;
  }
})();
