"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

(async () => {
  try {
    const root = path.join(__dirname, "..");
    const read = name => fs.readFileSync(path.join(root, name), "utf8");
    const playerCss = read("frontend/player-mode.css");
    for (const file of ["index.html", "frontend/index.html"]) {
      const html = read(file);
      assert.match(html, /<body class="player-mode">/);
      assert.match(html, /href="player-mode.css"/);
      assert.match(html, /class="mode-nav"/);
      for (const id of ["pit", "fight-button", "card-picker", "result-panel"])
        assert.ok(html.includes('id="' + id + '"'), file + " lost " + id);
    }
    for (const selector of [".pit-options-bar", ".formation-board",
      ".log-panel", ".preset-panel", ".pitch-panel", ".site-footer"])
      assert.ok(playerCss.includes(selector), "Not hidden in player mode: " + selector);

    const lab = read("frontend/engine-test-lab.html");
    for (const id of ["test-preset-cards", "test-bag-all", "test-pairs-all",
      "test-presets-all", "bag-run", "sweep-run", "all-presets", "bag-download",
      "sweep-download", "events", "seed"])
      assert.ok(lab.includes('id="' + id + '"'), "Missing test workbench " + id);
    assert.ok(lab.includes('src="engine-test-lab-dashboard.js"'));

    // Minimal DOM integration fixture tests only the page routing.
    // Real combat correctness stays with the existing browser/Python suite.
    class Element {
      constructor(tag = "div") {
        this.tag = tag; this.children = []; this.handlers = {};
        this.dataset = {}; this.disabled = false; this.textContent = "";
        this.value = ""; this.open = false;
      }
      append(...nodes) { this.children.push(...nodes); }
      replaceChildren(...nodes) {
        this.children = nodes.flatMap(n => n.tag === "#fragment" ? n.children : [n]);
      }
      setAttribute(key, value) { this[key] = value; }
      addEventListener(type, callback) { this.handlers[type] = callback; }
      click() { this.handlers.click?.(); }
      scrollIntoView() {}
    }
    const ids = {};
    for (const id of ["test-preset-cards", "test-preset-cards-status",
      "test-bag-all", "test-pairs-all", "test-presets-all", "bag-stop",
      "sweep-stop", "bag-run", "sweep-run", "all-presets", "sweep-mode",
      "advanced-tests", "test-dashboard-status", "events", "summary",
      "bag-panel", "sweep-panel"])
      ids[id] = new Element();
    ids["bag-stop"].disabled = ids["sweep-stop"].disabled = true;
    const calls = {bag: 0, pairs: 0, presets: 0, fight: 0};
    ids["bag-run"].addEventListener("click", () => calls.bag++);
    ids["sweep-run"].addEventListener("click", () => calls.pairs++);
    ids["all-presets"].addEventListener("click", () => calls.presets++);
    const hero = {id:"hero",ruleset:"2014"}, monster = {id:"monster",ruleset:"2014"};
    const selection = {ruleset:"2014",hero_ids:["hero"],monster_ids:["monster"]};
    const recipe = {id:"sample",ruleset:"2014",level:1,
      title:"Sample 1v1",classes:["fighter"],monsters:["goblin"],
      purpose:"Attack",seed:12345,aspects:[{kind:"feature",value:"attack"}]};
    const event = {event_type:"attack",feature_id:"attack",actor_id:"hero"};
    const window = {
      IRON_PIT_COMBAT_PRESET_RECIPES:{recipes:[recipe]},
      IRON_PIT_TEST_ALL_PLAN:{create:async mode => {
        assert.equal(mode,"presets");
        return {total:1,at:() => ({kind:"preset",label:recipe.title,
          selection,seed:12345,required_aspects:recipe.aspects})};
      }},
      IRON_PIT_TEST_ALL_RUNNER:{sources:() => [["hero",hero],["monster",monster]]},
      IRON_PIT_BROWSER_TURBO:{runSeeded:() => {
        calls.fight++; return {battle:{outcome:"heroes_win",rounds:1,events:[event]}};
      }},
      IRON_PIT_COMBAT_PRESETS:{aspectFired:(battle,spec) =>
        battle.events.some(e => e.feature_id === spec.value)},
      IRON_PIT_BATTLE_LAB:{fingerprint: battle => JSON.stringify(battle)},
    };
    const document = {
      getElementById:id => {
        assert.ok(ids[id], "Unexpected UI element " + id);
        return ids[id];
      },
      createElement:tag => new Element(tag),
      createDocumentFragment:() => new Element("#fragment"),
    };
    const browserContext = {window, document, console};
    // The individual page now relies on the same full event formatter as
    // real fights. Load both canonical log modules before its dashboard.
    vm.runInNewContext(read("frontend/battle-log-format.js"), browserContext);
    vm.runInNewContext(read("frontend/battle-log-export.js"), browserContext);
    vm.runInNewContext(read("frontend/engine-test-lab-dashboard.js"), browserContext);
    await new Promise(resolve => setImmediate(resolve));
    const cards = ids["test-preset-cards"].children;
    assert.equal(cards.length,1,"One source recipe must create one fight card");
    assert.equal(cards[0].tag,"article");
    const button = cards[0].children.find(c => c.tag === "button");
    button.click();
    assert.equal(calls.fight,2,"Card must use real seeded runner and replay parity");
    assert.equal(cards[0].children.at(-1).dataset.result,"pass");
    ids["test-bag-all"].click();
    ids["test-pairs-all"].click();
    ids["test-presets-all"].click();
    assert.deepEqual([calls.bag,calls.pairs,calls.presets],[1,1,1]);
    assert.equal(ids["sweep-mode"].value,"pairs");
    assert.equal(ids["advanced-tests"].open,true);
    assert.equal(ids["test-dashboard-status"].textContent,"");
    console.log("Production page split: player-only controls and shared test workbench OK");
  } catch (error) {
    console.error("Production page split regression failed",error);
    process.exitCode = 1;
  }
})();
