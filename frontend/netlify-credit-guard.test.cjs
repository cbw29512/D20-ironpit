"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { spawnSync } = require("node:child_process");

const root = path.resolve(__dirname, "..");
const config = fs.readFileSync(path.join(root, "netlify.toml"), "utf8");
const match = config.match(/^\s*ignore\s*=\s*'([^']+)'\s*$/m);
assert.ok(match, "netlify.toml must define a single-quoted build.ignore command");
const command = match[1];

function ignoreStatus(context) {
  const result = spawnSync("sh", ["-c", command], {
    cwd: root,
    env: { ...process.env, CONTEXT: context },
    encoding: "utf8",
  });
  assert.equal(result.error, undefined, `Netlify ignore command failed to execute for ${context || "empty context"}`);
  return result.status;
}

// Netlify build.ignore returns 1 to continue a build and 0 to skip it.
assert.equal(ignoreStatus("production"), 1, "production must be allowed to build");
for (const context of ["deploy-preview", "branch-deploy", "dev", ""]) {
  assert.equal(ignoreStatus(context), 0, `${context || "empty context"} must be skipped`);
}

console.log("Netlify build.ignore allows production only and skips preview/branch/dev contexts.");
