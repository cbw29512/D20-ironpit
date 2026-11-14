"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
(async () => {
  try {
    require("./browser-test-runtime.cjs").loadWebsite();
    const load = name => vm.runInThisContext(
      fs.readFileSync(path.join(__dirname, name), "utf8"), {filename: name});
    for (const script of ["custom-monster-runtime.js", "battle-lab.js",
      "browser-turbo.js", "engine-test-lab-punching-bag.js",
      "engine-test-lab-bag-fight.js", "battle-log-format.js",
      "battle-log-export.js"]) load(script);
    const baseline = JSON.stringify(window.IRON_PIT_BROWSER_HEROES);
    const rows = Object.values(window.IRON_PIT_BROWSER_HEROES);
    assert.equal(rows.filter(card => card.ruleset === "2014").length, 240);
    assert.equal(rows.filter(card => card.ruleset === "2024").length, 240);
    function node(name = "div") {
      return {tagName: name.toUpperCase(),value:"",textContent:"",disabled:false,
        children:[],handlers:{},isFragment:name === "fragment",
        append(...items) {this.children.push(...items);},
        replaceChildren(...items) {this.children = items.flatMap(x =>
          x.isFragment ? x.children : [x]);},
        addEventListener(key, cb) {this.handlers[key] = cb;},
        scrollIntoView() {},
      };
    }
    const nodes = {};
    for (const id of ["single-edition","single-level","single-class",
      "single-status","single-pregen-cards","pregen-log-panel","events"])
      nodes[id] = node();
    nodes["single-edition"].value = "2014";
    nodes["single-level"].value = "1";
    nodes["single-class"].value = "all";
    global.document = {getElementById: id => nodes[id] || null,
      createElement: node, createDocumentFragment: () => node("fragment")};
    load("pregen-single.js");
    assert.equal(nodes["single-pregen-cards"].children.length, 12,
      "All 12 level-one classes must have standalone combat cards.");
    const first = nodes["single-pregen-cards"].children[0];
    assert.equal(first.tagName,"ARTICLE");
    assert.match(first.children[1].textContent,/2014/);
    first.children[2].handlers.click();
    for (let i = 0; i < 250 &&
      !nodes["events"].textContent.startsWith("IRON PIT — COMPLETE PREGEN FIGHT");
      i++) await new Promise(resolve => setTimeout(resolve, 10));
    assert.match(nodes["events"].textContent,/===== EVERY COMBAT ROUND =====/);
    assert.match(nodes["events"].textContent,/Round 1/);
    assert.match(nodes["events"].textContent,/===== FULL RAW ENGINE EVENTS/);
    assert.match(nodes["events"].textContent,/"round_number"/);
    assert.equal(JSON.stringify(window.IRON_PIT_BROWSER_HEROES),baseline,
      "One-click individual pregen battle cannot mutate any source.");
    nodes["single-edition"].value = "2024";
    nodes["single-edition"].handlers.change();
    assert.equal(nodes["single-pregen-cards"].children.length,12);
    assert.match(nodes["single-pregen-cards"].children[0].children[1].textContent,/2024/);
    nodes["single-level"].value = "20";
    nodes["single-level"].handlers.change();
    assert.equal(nodes["single-pregen-cards"].children.length,12);
    nodes["single-class"].value = "wizard";
    nodes["single-class"].handlers.change();
    assert.equal(nodes["single-pregen-cards"].children.length,1);
    const html = fs.readFileSync(path.join(__dirname,"engine-test-lab.html"),"utf8");
    for(const id of ["single-pregens","single-edition","single-level",
      "single-class","single-pregen-cards","pregen-log-panel","pregen-copy",
      "pregen-save"])assert.ok(html.includes('id="'+id+'"'));
    assert.match(html,/src="pregen-single.js"/);
    const css=fs.readFileSync(path.join(__dirname,"pregen-only.css"),"utf8");
    assert.match(css,/#single-pregens/);
    console.log("480 separate pregen fights, real seeded bag replay, full event log and filters passed.");
  } catch(error) {
    console.error("Individual pregen UI regression failed",error);
    process.exitCode=1;
  }
})();