# Real card-art inventory

Hero pregens have Chris-approved full-color painterly portraits. Monsters still have no licensed rasters.

Processed hero assets are `frontend/assets/portraits/heroes/hero-{2014|2024}-{class}.webp` (3:4, about 50–85 KB). One file per character per edition is reused across levels 1–20.

Live fight-board screenshots of the wired portraits:

- `docs/artifacts/card-art/before-after-2014-2024-karnok-seraphine.png` — 2014 Karnok, 2024 Karnok, and 2014 Seraphine
- `docs/artifacts/card-art/2014-karnok-card.png` / `2024-karnok-card.png`
- `docs/artifacts/card-art/2014-seraphine-card.png` / `2024-seraphine-card.png`
- `docs/artifacts/card-art/2014-sample-board.png` / `2024-sample-board.png`
- `docs/artifacts/card-art/2014-picker-karnok.png` — roster/selection dialog
- `docs/artifacts/card-art/load-combat-board.png` — Load Combat board after a recorded monk duel

## Heroes — 24 of 24 have real color portraits

One portrait per character per edition, reused across levels 1–20.

| Portrait id | Name | Class | Real art |
|---|---|---|---|
| `hero-2014-barbarian` | Rokhan Stonefury | Barbarian | `frontend/assets/portraits/heroes/hero-2014-barbarian.webp` |
| `hero-2014-bard` | Lyra Silverstring | Bard | `frontend/assets/portraits/heroes/hero-2014-bard.webp` |
| `hero-2014-cleric` | Seraphine Dawnshield | Cleric | `frontend/assets/portraits/heroes/hero-2014-cleric.webp` |
| `hero-2014-druid` | Thalen Greenbough | Druid | `frontend/assets/portraits/heroes/hero-2014-druid.webp` |
| `hero-2014-fighter` | Karnok Stoneward | Fighter | `frontend/assets/portraits/heroes/hero-2014-fighter.webp` |
| `hero-2014-monk` | Kael Stillwater | Monk | `frontend/assets/portraits/heroes/hero-2014-monk.webp` |
| `hero-2014-paladin` | Aurelia Brightshield | Paladin | `frontend/assets/portraits/heroes/hero-2014-paladin.webp` |
| `hero-2014-ranger` | Rowan Ashtrail | Ranger | `frontend/assets/portraits/heroes/hero-2014-ranger.webp` |
| `hero-2014-rogue` | Mara Quickstep | Rogue | `frontend/assets/portraits/heroes/hero-2014-rogue.webp` |
| `hero-2014-sorcerer` | Nyra Emberveil | Sorcerer | `frontend/assets/portraits/heroes/hero-2014-sorcerer.webp` |
| `hero-2014-warlock` | Varek Ashenmark | Warlock | `frontend/assets/portraits/heroes/hero-2014-warlock.webp` |
| `hero-2014-wizard` | Elian Starweaver | Wizard | `frontend/assets/portraits/heroes/hero-2014-wizard.webp` |
| `hero-2024-barbarian` | Rokhan Stonefury | Barbarian | `frontend/assets/portraits/heroes/hero-2024-barbarian.webp` |
| `hero-2024-bard` | Lyra Silverstring | Bard | `frontend/assets/portraits/heroes/hero-2024-bard.webp` |
| `hero-2024-cleric` | Seraphine Dawnshield | Cleric | `frontend/assets/portraits/heroes/hero-2024-cleric.webp` |
| `hero-2024-druid` | Thalen Greenbough | Druid | `frontend/assets/portraits/heroes/hero-2024-druid.webp` |
| `hero-2024-fighter` | Karnok Stoneward | Fighter | `frontend/assets/portraits/heroes/hero-2024-fighter.webp` |
| `hero-2024-monk` | Kael Stillwater | Monk | `frontend/assets/portraits/heroes/hero-2024-monk.webp` |
| `hero-2024-paladin` | Aurelia Brightshield | Paladin | `frontend/assets/portraits/heroes/hero-2024-paladin.webp` |
| `hero-2024-ranger` | Rowan Ashtrail | Ranger | `frontend/assets/portraits/heroes/hero-2024-ranger.webp` |
| `hero-2024-rogue` | Mara Quickstep | Rogue | `frontend/assets/portraits/heroes/hero-2024-rogue.webp` |
| `hero-2024-sorcerer` | Nyra Emberveil | Sorcerer | `frontend/assets/portraits/heroes/hero-2024-sorcerer.webp` |
| `hero-2024-warlock` | Varek Ashenmark | Warlock | `frontend/assets/portraits/heroes/hero-2024-warlock.webp` |
| `hero-2024-wizard` | Elian Starweaver | Wizard | `frontend/assets/portraits/heroes/hero-2024-wizard.webp` |

## Monsters — 0 licensed rasters; live art is the SVG glyph

Every certified 2014 and 2024 monster card uses `figure-portraits.js`. No monster has a licensed photograph or painted raster.

The Goblin glyph is the most specific shipped monster picture: small humanoid, pointed ears, scimitar. Other creatures use form-specific glyphs (skeleton, unicorn, dragon, fish, and so on). Several fallbacks are still anatomically incomplete; those stay `inaccurate` on the shopping list.

See `ART_SHOPPING_LIST.md` for the full missing/inaccurate monster table.
