"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

const root = path.resolve(__dirname, "..");
const config = fs.readFileSync(path.join(root, "netlify.toml"), "utf8");
const deployment = fs.readFileSync(path.join(root, "docs", "DEPLOYMENT.md"), "utf8");

assert.match(config, /^\s*publish\s*=\s*"frontend"\s*$/m, "Netlify must publish the static frontend");
assert.match(config, /^\s*command\s*=.*pip install -e \.\/backend.*prepare_static_site\.py.*$/m,
  "Netlify production build must install the rules reference and prepare the static site");
assert.match(config, /^\s*ignore\s*=\s*'test "\$CONTEXT" != "production"'\s*$/m,
  "Netlify must retain the production-only ignore guard");
assert.doesNotMatch(config, /^\s*\[context\.(?:deploy-preview|branch-deploy)\]/m,
  "repository config must not add preview or branch-deploy build overrides");

for (const policy of [
  "Production branch is `main`.",
  "Deploy Previews are disabled.",
  "Branch deploys are disabled.",
  "GitHub Actions handles branch/PR certification.",
]) assert.ok(deployment.includes(policy), `deployment policy is missing: ${policy}`);

const workflowDir = path.join(root, ".github", "workflows");
for (const file of fs.readdirSync(workflowDir).filter((name) => /\.ya?ml$/.test(name))) {
  const text = fs.readFileSync(path.join(workflowDir, file), "utf8");
  assert.doesNotMatch(text, /\bnetlify\s+deploy\b/i, `${file} must not spend Netlify deploy credits from GitHub CI`);
}

console.log("Production-only Netlify credit policy is locked to main/static production with previews and branch deploys excluded.");
