# Iron Pit Production Deployment

## Canonical release path

1. Feature work stays off `main`.
2. Exact branch head passes CI.
3. Certified PR merges to `main`.
4. `main` CI runs again on the merge commit.
5. Render deploys the API only after linked checks pass.
6. GitHub Pages publishes the certified frontend automatically after successful `main` CI.
7. Netlify may also publish the production frontend; non-production Netlify deploys remain skipped to conserve credits.

## Production endpoints

- GitHub Pages frontend: `https://cbw29512.github.io/D20-ironpit/`
- Netlify project: `ironpit` (default Netlify domain is `https://ironpit.netlify.app/` unless a custom primary domain is configured)
- Render service: `iron-pit-d20-api`
- Default API base: `https://iron-pit-d20-api.onrender.com`
- API health endpoint: `/health`

`frontend/config.js` contains the stable Render default so GitHub Pages works without a build-time environment variable. Netlify's production build can override it with `IRON_PIT_API_BASE`.

## Cost policy

Netlify is reserved for deliberate production deployment and real production bandwidth testing.

- Production branch: `main`.
- Deploy Previews: disabled/skipped.
- Branch deploys: disabled/skipped.
- GitHub Actions handles routine validation and the GitHub Pages production mirror.
- `netlify.toml` keeps the production-only build guard enabled.

## Backend — Render

`render.yaml` defines the Docker web service and:

- health checks `/health`;
- waits for linked CI checks before auto-deploying;
- restricts CORS to the GitHub Pages and Netlify production origins;
- runs the API from `backend/Dockerfile`.

The free Render plan can cold-start after inactivity. The frontend health gate allows extra startup time and keeps FIGHT disabled if the API remains unavailable. Upgrade the Render instance before sustained public traffic.

## Frontend startup contract

The browser must:

1. resolve a nonblank public API base;
2. receive `{ "status": "ok" }` from `/health`;
3. load `/api/catalog`;
4. enable FIGHT only after those checks pass.

A failed health check leaves the combat controls disabled and shows a visible production-engine-offline status instead of silently failing.

## Production smoke test

- Root URL redirects to `/frontend/`.
- Current `main` encounter-builder assets are present.
- `/health` succeeds.
- Catalog reports 720 hero build slots and 328 SRD monsters.
- Only `raw_ready` cards can be added to automated fights.
- 1–8 heroes and 1–8 monsters can be selected.
- Duplicate cards remain independent combatants.
- Party Total Levels and Monster Total CR update correctly.
- Starting distance can be selected.
- FIGHT calls `/api/encounters/fight`.
- Initiative, battle events, final HP, and winner render.
- Natural 20 / natural 1 visual effects replay from server events.
- The fight ends only when an entire side is defeated or the safety limit is reached.

## Security posture

- No deployment secrets are committed.
- Netlify sends `nosniff`, Referrer Policy, Permissions Policy, and Content Security Policy headers.
- Render CORS is restricted to known production origins.
- Public fight endpoints reject uncertified runtime IDs.
- Add rate limiting before high-volume public launch or monetization.
