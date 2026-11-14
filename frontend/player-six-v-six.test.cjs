"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

// Data contract: six immutable selected cards per side, no extra combat slots.
// Display mapping: indexes 0..2 melee, indexes 3..5 ranged.
try {
  const css = fs.readFileSync(path.join(__dirname, "player-six-v-six.css"), "utf8");
  const app = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
  const view = fs.readFileSync(path.join(__dirname, "battlefield-view.js"), "utf8");
  const originalPortraits = fs.readFileSync(path.join(__dirname, "figure-portraits.css"), "utf8");
  assert.match(originalPortraits, /max-height:210px/,
    "The source art's maximum supported size must remain available outside the compact board.");
  assert.match(css, /--pit-slot-size:\s*clamp\(/,
    "Slot size must come from the viewport, never from a card's contents.");
  assert.match(css, /grid-template-rows:\s*repeat\(3,var\(--pit-slot-size\)\)/,
    "Both sides must have exactly three identical fixed-height rows.");
  const slot = css.match(/body\.player-mode #pit \.battle-card\s*\{([^}]*)\}/s)?.[1];
  const empty = css.match(/body\.player-mode #pit \.battle-card\.empty-slot\s*\{([^}]*)\}/s)?.[1];
  assert.ok(slot && empty, "Both occupied and empty cards need the same sizing contract.");
  for (const [kind, rule] of [["common",slot],["empty",empty]]) {
    assert.match(rule, /height:\s*var\(--pit-slot-size\)/,kind+" cards must have fixed height.");
    assert.match(rule, /min-height:\s*0/,kind+" cards must not retain the old min-height.");
    assert.match(rule, /max-height:\s*var\(--pit-slot-size\)/,kind+" cards must not grow.");
  }
  assert.match(css, /\.battle-card\.occupied\s*\{\s*display:\s*grid/,
    "Occupied cards must lay out art and text inside—not enlarge—their slot.");
  assert.match(css, /grid-template-columns:\s*minmax\(0,9fr\)\s+minmax\(0,11fr\)/,
    "The art and live card metadata must both fit inside the fixed card.");
  assert.match(css, /aspect-ratio:\s*3\s*\/\s*4/,
    "Show complete 3:4 source portraits in the fixed card.");
  assert.match(css, /\.portrait-image\s*\{\s*object-fit:\s*contain/,
    "Keep full artwork visible rather than center-cropping.");
  assert.match(css, /\.card-status-lanes\s*\{[^}]*overflow:\s*auto/s,
    "An unusual number of effects cannot stretch its card or the battlefield.");
  assert.doesNotMatch(css, /min-height:\s*(?:268|220|188)px/,
    "Old mismatched empty/occupied card minimums must not return.");
  assert.match(app, /const MAX_SLOTS = 6;/);
  assert.match(view, /const MAX_SLOTS = 6;/);
  assert.match(css, /grid-template-columns:\s*minmax\(0,1fr\)\s+minmax\(136px,174px\)\s+minmax\(0,1fr\)/,
    "Both teams must flank one central controls column.");
  assert.match(css, /grid-template-rows:\s*repeat\(3,var\(--pit-slot-size\)\)/,
    "Three paired rows show six combatants per side.");
  const placement = (side, index, col, row) => {
    const rx = new RegExp("#" + side + "-slots > :nth-child\\(" + index +
      "\\) \\{ grid-area: " + row + " / " + col + "; \\}");
    assert.match(css, rx, "Wrong " + side + " slot " + index + " position.");
  };
  for (let row = 1; row <= 3; row++) {
    placement("hero", row, 2, row);
    placement("hero", row + 3, 1, row);
    placement("monster", row, 1, row);
    placement("monster", row + 3, 2, row);
  }
  for (const pageName of ["index.html", "frontend/index.html"]) {
    const html = fs.readFileSync(path.join(__dirname, "..", pageName), "utf8");
    assert.equal((html.match(/id="fight-button"/g) || []).length, 1,
      pageName + " must contain one shared Fight/Stop button.");
    assert.ok(html.indexOf('src="battle-fight-stop.js"') < html.indexOf('src="battle-actions.js"'),
      pageName + " must initialize the replay stop controller before actions.");
    assert.ok(html.indexOf('src="player-control-state.js"') < html.indexOf('src="app.js"'),
      pageName + " must initialize the control-state projection before app boot.");
    assert.equal((html.match(/class="lane-headers"/g) || []).length, 2,
      pageName + " requires two mirrored lane legends.");
    assert.match(html, /<span>RANGED<\/span><span>MELEE<\/span><\/div><div id="hero-slots"/);
    assert.match(html, /<span>MELEE<\/span><span>RANGED<\/span><\/div><div id="monster-slots"/);
    for (const [id, side] of [["hero-slots", "heroes"], ["monster-slots", "monsters"]]) {
      const anchor = html.indexOf('id="' + id + '"');
      assert.ok(anchor !== -1, "Missing " + id);
      const segment = html.slice(anchor, html.indexOf("</div></div>", anchor));
      assert.equal((segment.match(new RegExp('class="battle-card empty-slot ' + side + '"', "g")) || []).length,
        6, pageName + " must offer exactly six initial combatant slots for " + side);
    }
    assert.ok(html.indexOf('href="player-six-v-six.css"') >
      html.indexOf('href="bulk-combat.css"'), "Mirrored formation must override legacy board styles.");
  }
  console.log("Mirrored 6v6: 3 ranged + 3 melee per team, one Fight button, no engine edits.");
} catch (error) {
  console.error("Mirrored battlefield layout regression failed", error);
  process.exitCode = 1;
}