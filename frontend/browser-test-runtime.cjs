"use strict";

const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

// Load the website's module order so standalone fixtures cannot hide missing dependencies.
function loadWebsite(page = "frontend/index.html") {
  try {
    global.window = globalThis;
    const root = path.resolve(__dirname, "..");
    const html = fs.readFileSync(path.join(root, page), "utf8");
    for (const [, file] of html.matchAll(/<script[^>]*src="([^"]+)"/g)) {
      if (!file.startsWith("browser-")) continue;
      vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
      if (file === "browser-engine.js") break;
    }
    // Mirror the post-engine catalog modules and the lazily loaded 2014 bundle.
    // The real page loads the Wanted scripts before browser-catalog.js.
    for (const file of ["browser-wanted-2014.js", "browser-wanted-posters.js", "browser-monsters-2014.js"]) {
      vm.runInThisContext(fs.readFileSync(path.join(__dirname, file), "utf8"), { filename: file });
    }
  } catch (error) {
    console.error("Website runtime fixture failed to initialize.", page, error);
    throw error;
  }
}

module.exports = { loadWebsite };
