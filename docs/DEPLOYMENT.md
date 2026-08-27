# Iron Pit D20 Deployment Checklist

## Backend — Render

- [ ] Open Render and choose **New > Blueprint**.
- [ ] Connect `cbw29512/github-D20`.
- [ ] Confirm the Blueprint path is `render.yaml`.
- [ ] Deploy the `iron-pit-d20-api` free web service.
- [ ] Copy the assigned `https://...onrender.com` URL.
- [ ] Verify `GET <api-url>/health` returns `{"status":"ok"}`.

## Frontend — Netlify

- [ ] Import `cbw29512/github-D20` from GitHub.
- [ ] Use `main` as the production branch.
- [ ] Confirm Netlify reads the root `netlify.toml`.
- [ ] Set `IRON_PIT_API_BASE` to the Render API URL.
- [ ] Deploy the production site.
- [ ] Click **Enter the Pit** and verify the battle completes.

## MVP smoke test

- [ ] Fighter and Goblin start at full HP.
- [ ] Initiative events appear in the battle log.
- [ ] Attack events animate the acting stick figure.
- [ ] Hits update target HP.
- [ ] Misses do not change HP.
- [ ] A natural 20 can produce a critical hit event.
- [ ] The duel ends when one combatant reaches 0 HP.
- [ ] The displayed winner matches the API battle result.

## Security before accounts/payments

- [ ] Replace wildcard CORS with known frontend origins.
- [ ] Add Supabase Auth and server-side token validation.
- [ ] Persist battle results in Postgres.
- [ ] Add rate limiting before exposing high-volume simulations.
- [ ] Never commit service keys, payment credentials, or private environment values.
