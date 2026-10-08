# Universal AoE telegraph and combat log — living implementation tracker

## Locked user intent (2026-10-08)

Iron Pit uses 6 vs 6 positions: three front and three back on each side, all creatures one 5-foot square regardless of printed size. Initial backliners automatically become effective frontline on last frontline defeat, without spatial teleportation. A spell or monster area affects authoritative occupied squares and may affect allies. **The engine decides targets; visualization never determines combat outcomes.**

- Every spatial combat action, including eligible monster abilities and pregen spells in both rulesets, may display its printed shape (radius/sphere, cone, line, cube, emanation, walls, etc.), printed extent and valid range, then highlight the occupied grid squares and ally/enemy targets the engine would affect. Do not convert Fireball's 20-foot-radius sphere into a cube mechanically: render the sphere's intersection with the square grid. Printed obstruction/cover and concentration/persistent duration remain source-specific.
- Visual palette: fire red/orange; lightning white/blue-white; cold light blue; necrotic dark violet/black; poison green; radiant gold; psychic/charms transparent grey/violet. Nonphysical single-target events use a translucent target cue with caster/action text instead of fake spatial geometry.
- On selection: show an outline preview before execution; on resolution: flash the confirmed engine area/targets and show the combat event; transient preview disappears. Persistent environmental areas remain visible as long as their authoritative effect exists.
- Existing recorded event log is the **single source of truth**. Show caster, action, edition, origin, shape/extent, targets including allies, actual dice and modifiers, hit/save outcomes, damage/healing/conditions and expiration when available. Preserve source event IDs and round/turn ordering. Never fabricate rolls or inferred outcomes for display.
- Future integration: optional external/offline ESP32 touchscreen dice roller can provide rolls if and only if the engine's dice-provider interface, deterministic replay, and audit provenance requirements are respected. **Not connected yet.** No external hardware dependency for core play.

## State of delivery

- **DONE / merged:** PR #657 implements universal backline promotion, including ranged/spellcasters, with Python/browser and CI certification.
- **IN REVIEW:** PR #656 records locked 6v6 formation; PR #658 changes Python/browser physical footprints to one square; neither is to be called merged without verification.
- **ALREADY PRESENT:** `backend/app/combat/area_targeting.py`, `frontend/browser-area-targeting.js`, `frontend/browser-area-shapes.js` calculate placement/geometry; `frontend/battle-log-export.js` exports recorded events. Reuse, don't replace.
- **THIS PR / FIRST SLICE:** browser preview grid-cell projector using shared shape predicates and a damage-flavor palette, plus focused Node tests. Data-only; no clickable UI or rendering hookup yet.
- **NEXT:** exact-head certification, merge; wire preview/cast/clear lifecycle in combat UI to existing action selection and resolved events; then test Fireball, Lightning Bolt, Burning Hands, Thunderwave and dragon lines/cones on the 12-position board including friendly fire; then persistent effects and nonphysical status flashes.
- **ACCEPTANCE GATE:** geometry/target membership agrees across Python and browser and event log displays only authoritative rolls; no custom logic per monster/spell; 2014/2024 source separation; no changes to artwork ownership or Netlify deployment.
