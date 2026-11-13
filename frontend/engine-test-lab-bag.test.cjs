"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
require("./browser-test-runtime.cjs").loadWebsite();

(async () => {
  try {
    for (const file of [
      "custom-monster-runtime.js",
      "battle-lab.js",
      "browser-turbo.js",
      "engine-test-lab-sweep-plan.js",
      "engine-test-lab-punching-bag.js",
      "engine-test-lab-bag-plan.js",
      "engine-test-lab-bag-fight.js",
      "engine-test-lab-bag-coverage.js",
      "engine-test-lab-bag-runner.js",
    ]) vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"),
      {filename: file});

    const bagApi = window.IRON_PIT_TEST_PUNCHING_BAG;
    const fight = window.IRON_PIT_TEST_BAG_FIGHT;
    const coverage = window.IRON_PIT_TEST_BAG_COVERAGE;
    const plan = window.IRON_PIT_TEST_BAG_PLAN.create();
    const initialHeroes = window.IRON_PIT_BROWSER_HEROES;
    const heroSnapshot = JSON.stringify(initialHeroes);
    const groupCounts = plan.groups.map(g => g.ids.length);
    assert.equal(plan.groups.length, 4);
    assert.ok(groupCounts.every(n => n > 0), "Both editions need heroes and monsters.");
    assert.equal(groupCounts[0], Object.keys(window.IRON_PIT_BROWSER_MONSTERS_2014).length,
      "Must exercise every currently certified 2014 monster without a frozen count.");
    assert.ok(groupCounts[2] >= 141, "Must include every certified 2024 monster.");
    assert.equal(plan.total, groupCounts.reduce((a,b) => a+b, 0));
    assert.equal(new Set(Array.from({length:plan.total}, (_,i) => {
      const c = plan.at(i); return c.edition + ":" + c.source_kind + ":" + c.source_id;
    })).size, plan.total, "Every variant must be scheduled exactly once.");

    for (const edition of ["2014", "2024"]) {
      const bag = bagApi.template(edition);
      assert.equal(bag.name, "Punching Bag");
      assert.equal(bag.armor_class, 10);
      assert.equal(bag.max_hp, 10000);
      assert.equal(bag.attacks.length, 1);
      assert.equal(bag.attacks[0].damageBonus, -4);
      assert.equal(bag.attacks[0].diceCount, 1);
      assert.equal(bag.attacks[0].diceSize, 2);
      assert.ok(!Object.hasOwn(window.IRON_PIT_BROWSER_MONSTERS || {}, bag.id));
      assert.ok(!Object.hasOwn(window.IRON_PIT_BROWSER_MONSTERS_2014 || {}, bag.id));
      assert.ok(!Object.hasOwn(initialHeroes, bag.id));
    }

    const sourceIds = {
      "2014": {
        monster: "2014-goblin",
        pregen: Object.values(initialHeroes).find(
          h => h.ruleset === "2014" && h.class_id === "fighter" && h.level === 1)?.id,
      },
      "2024": {
        monster: Object.values(window.IRON_PIT_BROWSER_MONSTERS).find(
          m => m.attacks?.length && m.ruleset === "2024")?.id,
        pregen: Object.values(initialHeroes).find(
          h => h.ruleset === "2024" && h.class_id === "fighter" && h.level === 1)?.id,
      },
    };
    const cases = [];
    for (const edition of ["2014", "2024"]) {
      for (const kind of ["monster", "pregen"]) {
        const source_id = sourceIds[edition][kind];
        assert.ok(source_id, `Missing certified test source: ${edition} ${kind}`);
        const entry = {kind: "punching_bag", edition, source_kind: kind, source_id};
        const source = fight.sourceCard(entry), before = JSON.stringify(source);
        const executed = fight.run(entry, 1234567);
        assert.ok(["heroes_win", "monsters_win", "draw"].includes(
          executed.replay.battle.outcome));
        assert.ok(executed.replay.battle.events.length > 0);
        const dummy = [...executed.replay.battle.setup.heroes,
          ...executed.replay.battle.setup.monsters].find(
            member => member.state.template.name === "Punching Bag");
        assert.ok(dummy);
        assert.equal(dummy.state.template.max_hp, 10000);
        assert.ok(!executed.replay.battle.events.some(e =>
          e.actor_id === executed.bag_actor_id && (e.damage_roll?.total || 0) > 0),
          "The harmless Punching Bag must not damage anyone.");
        const audit = coverage.audit(source, executed.replay.battle.events,
          executed.source_actor_id);
        assert.ok(audit.declared_count >= 1, "Source abilities must be enumerated.");
        assert.equal(audit.exercised_count + audit.not_observed_count,
          audit.declared_count);
        assert.equal(JSON.stringify(source), before, "Source cards stay immutable.");
        assert.strictEqual(window.IRON_PIT_BROWSER_HEROES, initialHeroes,
          "Temporary hero-side bag registry must be restored.");
        cases.push(entry);
      }
    }
    const mini = {total: 2, at: i => cases[i]};
    const report = await window.IRON_PIT_TEST_BAG_RUNNER.run(
      mini, 12345, 1, {stopRequested: false});
    assert.equal(report.completed, 2);
    assert.equal(report.cases.length, 2);
    assert.equal(report.fights_executed, 2);
    assert.equal(report.skipped, 0);
    assert.equal(JSON.stringify(initialHeroes), heroSnapshot);
    const lab = fs.readFileSync(path.join(__dirname, "engine-test-lab.html"), "utf8");
    const scripts = [...lab.matchAll(/<script defer src="([^"]+)"/g)]
      .map(m => m[1]);
    for (const file of ["custom-monster-runtime.js",
      "engine-test-lab-punching-bag.js", "engine-test-lab-bag-plan.js",
      "engine-test-lab-bag-fight.js", "engine-test-lab-bag-coverage.js",
      "engine-test-lab-bag-runner.js", "engine-test-lab-bag-ui.js"])
      assert.ok(scripts.includes(file), `Missing lab module: ${file}`);
    assert.ok(scripts.indexOf("custom-monster-runtime.js") <
      scripts.indexOf("engine-test-lab-punching-bag.js"));
    assert.match(lab, /id="bag-run"/);
    assert.match(lab, /id="bag-download"/);
    for (const file of ["index.html", "../index.html"]) {
      const html = fs.readFileSync(path.join(__dirname, file), "utf8");
      assert.match(html, /name="run" value="bag"/);
    }
    console.log("Punching Bag 2014/2024 all-source plan, real fights, logs and isolation passed.");
  } catch (error) {
    console.error("Punching Bag all-monster/pregen gauntlet regression failed.", error);
    process.exitCode = 1;
  }
})();
