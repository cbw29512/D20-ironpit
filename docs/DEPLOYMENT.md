# Iron Pit D20 Deployment Checklist

## Cost policy

Netlify is reserved for deliberate production deployment and real production bandwidth testing.

- [ ] Production branch is `main`.
- [ ] Netlify **Deploy Previews are disabled**.
- [ ] Netlify **Branch deploys are set to None**.
- [ ] GitHub Actions handles branch/PR validation instead of Netlify.
- [ ] `netlify.toml` keeps the production-only build guard enabled.
- [ ] Feature work stays on branches and is merged to `main` only after exact-head CI passes.

The repository guard skips Netlify builds whenever `CONTEXT` is not `production`. Netlify build hooks are intentionally not blocked by the ignore command, so only trigger one manually when a deliberate production-style test is wanted.

## Backend — Render

- [ ] Open Render and choose **New > Blueprint**.
- [ ] Connect `cbw29512/D20-ironpit`.
- [ ] Confirm the Blueprint path is `render.yaml`.
- [ ] Deploy the `iron-pit-d20-api` web service.
- [ ] Copy the assigned `https://...onrender.com` URL.
- [ ] Verify `GET <api-url>/health` returns `{"status":"ok"}`.

## Frontend — Netlify

- [ ] Import `cbw29512/D20-ironpit` from GitHub.
- [ ] Use `main` as the production branch.
- [ ] Confirm Netlify reads the root `netlify.toml`.
- [ ] Set `IRON_PIT_API_BASE` to the Render API URL for the Production context.
- [ ] In **Project configuration > Build & deploy > Continuous Deployment > Branches and deploy contexts**, disable Deploy Previews and set Branch deploys to None.
- [ ] Deploy the production site.

## Production smoke test

- [ ] The roster loads from `/api/roster`.
- [ ] At least one Hero Card and one Monster Card can be selected.
- [ ] Up to 8 Hero Cards and 8 Monster Cards can be added.
- [ ] Duplicate monster cards remain independent combatants.
- [ ] Party Total Levels updates correctly.
- [ ] Monster Total CR updates correctly.
- [ ] Starting distance can be selected.
- [ ] **FIGHT** calls `/api/encounters/fight`.
- [ ] Initiative order appears.
- [ ] Battle events appear in the DM Details log.
- [ ] Final HP/survivors appear.
- [ ] The fight ends only when an entire side is down or the safety round limit is reached.

## Security before accounts/payments

- [ ] Restrict CORS to known production frontend origins.
- [ ] Add rate limiting before exposing high-volume simulations.
- [ ] Never commit service keys, payment credentials, or private environment values.
