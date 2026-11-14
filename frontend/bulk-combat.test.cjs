"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    // Test schema: canonical battle events, one stream per suite, all case seeds.
    const controls = {};
    for (const id of ["bulk-bag", "bulk-pairs", "bulk-stop", "bulk-copy",
      "bulk-save", "bulk-progress", "bulk-status"]) {
      controls[id] = {disabled: false, handlers: {},
        addEventListener(name, handler) { this.handlers[name] = handler; }};
    }
    const files = [], messages = [];
    const context = {console, setTimeout, clearTimeout, Blob, URL, Date,
      document: {getElementById: id => controls[id] || null},
      navigator: {clipboard: {async writeText(text) { messages.push(text); }}}};
    context.window = context;
    context.window.showSaveFilePicker = async () => {
      const file = {parts: [], closed: false};
      files.push(file);
      return {async createWritable() { return {
        async write(part) { file.parts.push(part); },
        async close() { file.closed = true; },
      }; }};
    };
    const load = file => vm.runInNewContext(
      fs.readFileSync(path.join(__dirname, file), "utf8"),
      context, {filename: file});
    load("battle-log-format.js");
    load("battle-log-export.js");
    load("bulk-combat-validation.js");
    load("bulk-combat-file.js");
    load("bulk-combat-ui.js");
    load("bulk-combat-runner.js");

    const event = {round_number: 1, event_type: "attack", actor_name: "Hero",
      target_name: "Bag", attack_name: "Sword", hit: true, target_ac: 10,
      hp_before: 10000, hp_after: 9994,
      damage_roll: {total: 6}, damage_components: [
        {total: 6, applied_total: 6, damage_type: "slashing"}],
      audit: {steps: [{rule: "Attack bonus", detail: "15 + 4 = 19"}]},
      unformatted_provenance: {source_id: "exact-card-id"}};
    const makeBattle = () => ({events: [event], rounds: 1,
      outcome: "heroes_win", setup: {heroes: [], monsters: [{combatant_id: "bag-1"}]}});
    const writer = await context.IRON_PIT_BULK_COMBAT_FILE.open("bag", 12345);
    await writer.fight(0, 1, {edition: "2014", label: "Hero vs Bag"},
      51, makeBattle(), "diag-51");
    await writer.close({completed: 1, passed: 1});
    assert.equal(files.length, 1);
    assert.equal(files[0].closed, true);
    const full = files[0].parts.join("");
    assert.match(full, /FIGHT 1 OF 1/);
    assert.match(full, /Round 1 · attack/);
    assert.match(full, /Attack bonus: 15 \+ 4 = 19/);
    assert.match(full, /unformatted_provenance/);
    assert.match(full, /exact-card-id/);
    assert.match(full, /fights_logged/);

    const card = {id: "h14", ruleset: "2014", kind: "character",
      name: "Hero", coverage_status: "raw_ready", runnable_template_id: "h14"};
    const monster = {id: "m14", ruleset: "2014", kind: "monster",
      name: "Monster", coverage_status: "raw_ready", runnable_template_id: "m14"};
    const bag = {id: "bag", name: "Punching Bag", ruleset: "2014",
      coverage_status: "custom_ready", runnable_template_id: "bag",
      compiled_template: {id: "bag"}};
    const heroSource = {id: "h14", ruleset: "2014"};
    const monsterSource = {id: "m14", ruleset: "2014"};
    context.IRON_PIT_BROWSER_TURBO = {
      deriveSeed: (_base, index) => index + 100,
      runSeeded: () => ({battle: makeBattle(), diagnostic_id: "seeded"}),
    };
    context.IRON_PIT_TEST_ALL_RUNNER = {
      sources: () => [["h14", heroSource], ["m14", monsterSource]],
    };
    context.IRON_PIT_TEST_ALL_PLAN = {async create(mode) {
      assert.equal(mode, "pairs");
      return {total: 2, at: index => ({kind: "duel", label: "Hero vs Monster " + index,
        selection: {ruleset: "2014", hero_ids: ["h14"], monster_ids: ["m14"]}})};
    }};
    context.IRON_PIT_TEST_BAG_PLAN = {create() {
      return {total: 1, at: () => ({kind: "punching_bag", edition: "2014",
        source_kind: "pregen", source_id: "h14", label: "Hero vs Bag"})};
    }};
    context.IRON_PIT_TEST_BAG_COVERAGE = {audit: () => ({
      declared_count: 1, exercised_count: 0, not_observed_count: 1,
      exercised: [], not_observed: [{id: "limited-ability"}]})};
    context.IRON_PIT_TEST_BAG_FIGHT = {
      run: () => ({replay: {battle: makeBattle(), diagnostic_id: "bag"},
        source: heroSource, source_actor_id: "h1", bag_actor_id: "bag-1"}),
    };
    context.IRON_PIT_BATTLEFIELD_BAG_RUNNER = {bagCard: () => bag};
    context.IRON_PIT_BATTLEFIELD_REPLAY = {async play() {}};
    context.IRON_PIT_BATTLEFIELD_VIEW = {writeLog() {}, showResult() {}};
    const state = {fighting: false, session: null, ruleset: "2014",
      catalog: {heroes: [card], monsters: [monster]}};
    const api = {state, updateControls() {},
      async ensureRuleset(edition) { state.ruleset = edition; },
      load() {}};
    context.IRON_PIT_BULK_COMBAT_RUNNER.install(api);
    assert.equal(typeof controls["bulk-bag"].handlers.click, "function");
    const waitForCompletion = async () => {
      for (let i = 0; i < 200; i++) {
        await new Promise(resolve => setTimeout(resolve, 5));
        if (!state.fighting && !controls["bulk-stop"].disabled) continue;
        if (!state.fighting && controls["bulk-stop"].disabled) return;
      }
      throw new Error("Bulk suite did not finish.");
    };
    controls["bulk-bag"].handlers.click();
    await waitForCompletion();
    assert.equal(files.length, 2);
    assert.equal((files[1].parts.join("").match(/FIGHT \d+ OF 3/g) || []).length, 3,
      "All three Punching Bag attempts must be fully logged.");
    assert.match(files[1].parts.join(""), /"completed": 3/);
    assert.match(files[1].parts.join(""), /limited-ability/);
    controls["bulk-pairs"].handlers.click();
    await waitForCompletion();
    assert.equal(files.length, 3);
    assert.equal((files[2].parts.join("").match(/FIGHT \d+ OF 2/g) || []).length, 2);
    assert.equal(state.fighting, false);
    assert.equal(files[2].closed, true);
    assert.ok(!controls["bulk-status"].textContent.includes("Test stopped"));

    for (const htmlName of ["index.html", "frontend/index.html"]) {
      const html = fs.readFileSync(path.join(__dirname, "..", htmlName), "utf8");
      for (const id of ["bulk-bag", "bulk-pairs", "bulk-stop",
        "bulk-copy", "bulk-save", "bulk-progress", "bulk-status"]) {
        assert.ok(html.includes('id="' + id + '"'), htmlName + " missing " + id);
      }
      for (const script of ["engine-test-lab-sweep-plan.js",
        "engine-test-lab-bag-fight.js", "bulk-combat-file.js",
        "bulk-combat-runner.js", "app.js"]) {
        assert.ok(html.includes('src="' + script + '"'),
          htmlName + " missing script " + script);
      }
    }
    const individual = fs.readFileSync(path.join(__dirname,
      "engine-test-lab.html"), "utf8");
    assert.match(individual, /pregen-only.css/);
    assert.match(individual, /id="pregen-copy"/);
    assert.match(individual, /id="pregen-save"/);
    console.log("Two real seeded bulk modes, all-attempt streaming logs and mirrored hero pages passed.");
  } catch (error) {
    console.error("Simplified Iron Pit bulk UI regression failed", error);
    process.exitCode = 1;
  }
})();