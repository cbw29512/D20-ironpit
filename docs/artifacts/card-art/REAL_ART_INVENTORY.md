# Real card-art inventory

Hero pregens have Chris-approved full-color painterly portraits. Twenty-six approved monster silhouettes are framed to 3:4 WebP and wired for both editions when the roster creature matches.

Processed hero assets are `frontend/assets/portraits/heroes/hero-{2014|2024}-{class}.webp` (3:4, about 50–85 KB). One file per character per edition is reused across levels 1–20.

Processed monster assets are `frontend/assets/portraits/monsters/{id}.webp` (3:4, 480×640, under 20 KB). The same raster serves the matching 2014 and 2024 roster ids.

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

## Monsters — 26 approved silhouettes; remaining cards keep the SVG glyph

Live fight-board / picker captures of the wired silhouettes:

- `docs/artifacts/card-art/before-after-monsters.png`
- `docs/artifacts/card-art/2014-monster-sample-board.png`
- `docs/artifacts/card-art/2024-monster-sample-board.png`

The same creature image is registered to the real 2014 runtime id (`2014-{slug}`), the 2024 certified runtime id (`srd-{slug}`, or `srd-goblin-warrior` for Goblin), and the 2024 catalog id (`srd-5.2.1-2024-monster-{slug}`) when that row is genuinely the same creature.

Not mapped, even when a similar name exists:

- Goblin art is not used for Goblin Minion, Goblin Boss, or Hobgoblin
- Minotaur art is 2014-only; 2024 has Minotaur of Baphomet and Minotaur Skeleton, which are different creatures
- Skeleton / Zombie / Crocodile art is not used for Warhorse Skeleton, Minotaur Skeleton, Ogre Zombie, or Giant Crocodile
- Hippopotamus and Manticore exist in the 2024 roster only
- Berserker, Elephant, Giant Ape, Unicorn, and Roc have 2014 runtime ids plus 2024 catalog ids; they are not in the certified 2024 runtime subset

| File | 2014 runtime | 2024 runtime | 2024 catalog |
|---|---|---|---|
| `goblin.webp` | `2014-goblin` | `srd-goblin-warrior` | `srd-5.2.1-2024-monster-goblin-warrior` |
| `berserker.webp` | `2014-berserker` | — | `srd-5.2.1-2024-monster-berserker` |
| `brown-bear.webp` | `2014-brown-bear` | `srd-brown-bear` | `srd-5.2.1-2024-monster-brown-bear` |
| `dire-wolf.webp` | `2014-dire-wolf` | `srd-dire-wolf` | `srd-5.2.1-2024-monster-dire-wolf` |
| `owlbear.webp` | `2014-owlbear` | `srd-owlbear` | `srd-5.2.1-2024-monster-owlbear` |
| `minotaur.webp` | `2014-minotaur` | — | — |
| `skeleton.webp` | `2014-skeleton` | `srd-skeleton` | `srd-5.2.1-2024-monster-skeleton` |
| `red-dragon-wyrmling.webp` | `2014-red-dragon-wyrmling` | `srd-red-dragon-wyrmling` | `srd-5.2.1-2024-monster-red-dragon-wyrmling` |
| `blue-dragon-wyrmling.webp` | `2014-blue-dragon-wyrmling` | `srd-blue-dragon-wyrmling` | `srd-5.2.1-2024-monster-blue-dragon-wyrmling` |
| `young-red-dragon.webp` | `2014-young-red-dragon` | `srd-young-red-dragon` | `srd-5.2.1-2024-monster-young-red-dragon` |
| `young-black-dragon.webp` | `2014-young-black-dragon` | `srd-young-black-dragon` | `srd-5.2.1-2024-monster-young-black-dragon` |
| `zombie.webp` | `2014-zombie` | `srd-zombie` | `srd-5.2.1-2024-monster-zombie` |
| `elephant.webp` | `2014-elephant` | — | `srd-5.2.1-2024-monster-elephant` |
| `giant-ape.webp` | `2014-giant-ape` | — | `srd-5.2.1-2024-monster-giant-ape` |
| `giant-constrictor-snake.webp` | `2014-giant-constrictor-snake` | `srd-giant-constrictor-snake` | `srd-5.2.1-2024-monster-giant-constrictor-snake` |
| `giant-scorpion.webp` | `2014-giant-scorpion` | `srd-giant-scorpion` | `srd-5.2.1-2024-monster-giant-scorpion` |
| `hell-hound.webp` | `2014-hell-hound` | `srd-hell-hound` | `srd-5.2.1-2024-monster-hell-hound` |
| `unicorn.webp` | `2014-unicorn` | — | `srd-5.2.1-2024-monster-unicorn` |
| `roc.webp` | `2014-roc` | — | `srd-5.2.1-2024-monster-roc` |
| `crocodile.webp` | `2014-crocodile` | `srd-crocodile` | `srd-5.2.1-2024-monster-crocodile` |
| `hippopotamus.webp` | — | `srd-hippopotamus` | `srd-5.2.1-2024-monster-hippopotamus` |
| `manticore.webp` | — | `srd-manticore` | `srd-5.2.1-2024-monster-manticore` |
| `triceratops.webp` | `2014-triceratops` | `srd-triceratops` | `srd-5.2.1-2024-monster-triceratops` |
| `tyrannosaurus-rex.webp` | `2014-tyrannosaurus-rex` | `srd-tyrannosaurus-rex` | `srd-5.2.1-2024-monster-tyrannosaurus-rex` |
| `warhorse-skeleton.webp` | `2014-warhorse-skeleton` | `srd-warhorse-skeleton` | `srd-5.2.1-2024-monster-warhorse-skeleton` |
| `wyvern.webp` | `2014-wyvern` | `srd-wyvern` | `srd-5.2.1-2024-monster-wyvern` |

Every other monster still uses `figure-portraits.js`. See `ART_SHOPPING_LIST.md` for the remaining missing/inaccurate table.
