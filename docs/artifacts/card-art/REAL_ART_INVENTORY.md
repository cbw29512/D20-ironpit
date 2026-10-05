# Real card-art inventory

Hero pregens have Chris-approved full-color painterly portraits. Ninety-seven approved monster silhouettes are framed to 3:4 WebP and wired for both editions when the roster creature matches.

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

## Monsters — 97 approved silhouettes; remaining cards keep the SVG glyph

Live fight-board / picker captures of the wired silhouettes:

- `docs/artifacts/card-art/before-after-monsters.png`
- `docs/artifacts/card-art/2014-monster-sample-board.png`
- `docs/artifacts/card-art/2024-monster-sample-board.png`
- `docs/artifacts/card-art/2024-batch2-sample-board.png`
- `docs/artifacts/card-art/2014-batch2-sample-board.png`
- `docs/artifacts/card-art/2014-card-wolf.png` / `2014-card-troll.png` / `2014-card-giant-crocodile.png`
- `docs/artifacts/card-art/2024-card-wolf.png` / `2024-card-goblin-boss.png` / `2024-card-hobgoblin-warrior.png` / `2024-card-giant-crocodile.png`
- `docs/artifacts/card-art/2014-picker-wolf.png` / `2024-picker-goblin-boss.png` / `2024-picker-hobgoblin-warrior.png` / `2024-picker-harpy.png`

The same creature image is registered to the real 2014 runtime id (`2014-{slug}`), the 2024 certified runtime id (`srd-{slug}`, or `srd-goblin-warrior` for Goblin), and the 2024 catalog id (`srd-5.2.1-2024-monster-{slug}`) when that row is genuinely the same creature.

Not mapped, even when a similar name exists:

- Goblin art is not used for Goblin Minion, Goblin Boss, or Hobgoblin; those three now have their own files
- 2014 Minotaur art is not used for Minotaur of Baphomet or Minotaur Skeleton
- Skeleton / Zombie / Crocodile / Wolf / Boar / Guard / Spider / Ape / Snake / Rat / Hawk / Bandit / Cultist / Priest / Mage / Vampire / Pegasus / Medusa art is not reused for Warhorse Skeleton, Ogre Zombie, Giant Crocodile, Dire Wolf, Winter Wolf, Giant Boar, Guard Captain, Giant Wolf Spider, Giant Ape, Giant Constrictor Snake, Giant Rat, Blood Hawk vs Hawk, Bandit Captain, Cultist Fanatic, Priest Acolyte, Archmage, Vampire, Unicorn, or Gorgon
- Hippopotamus and Manticore exist in the 2024 roster only
- Berserker, Elephant, Giant Ape, Unicorn, Roc, and Troll have 2014 runtime ids plus 2024 catalog ids; Troll is not in the certified 2024 runtime subset
- Adult dragon art is not used for the matching young, wyrmling, or ancient rows
- Air / Earth / Fire / Water Elemental each have their own raster
- 2024 Azer Sentinel uses `azer.webp`; 2024 Centaur Trooper uses `centaur.webp`
- `orc.webp` was processed but is not registered: neither the 2014 certified roster, the 2024 certified roster, nor the 330-name 2024 catalog has `orc` / `orc-warrior`
- `beholder.webp` was processed but is not registered: neither the 2014 certified roster, the 2024 certified roster, nor the 330-name 2024 catalog has `beholder`

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
| `wolf.webp` | `2014-wolf` | `srd-wolf` | `srd-5.2.1-2024-monster-wolf` |
| `worg.webp` | `2014-worg` | `srd-worg` | `srd-5.2.1-2024-monster-worg` |
| `goblin-minion.webp` | — | `srd-goblin-minion` | `srd-5.2.1-2024-monster-goblin-minion` |
| `goblin-boss.webp` | — | `srd-goblin-boss` | `srd-5.2.1-2024-monster-goblin-boss` |
| `hobgoblin-warrior.webp` | — | `srd-hobgoblin-warrior` | `srd-5.2.1-2024-monster-hobgoblin-warrior` |
| `bugbear-warrior.webp` | — | — | `srd-5.2.1-2024-monster-bugbear-warrior` |
| `ogre.webp` | `2014-ogre` | `srd-ogre` | `srd-5.2.1-2024-monster-ogre` |
| `ogre-zombie.webp` | `2014-ogre-zombie` | `srd-ogre-zombie` | `srd-5.2.1-2024-monster-ogre-zombie` |
| `giant-crocodile.webp` | `2014-giant-crocodile` | `srd-giant-crocodile` | `srd-5.2.1-2024-monster-giant-crocodile` |
| `minotaur-of-baphomet.webp` | — | — | `srd-5.2.1-2024-monster-minotaur-of-baphomet` |
| `minotaur-skeleton.webp` | `2014-minotaur-skeleton` | `srd-minotaur-skeleton` | `srd-5.2.1-2024-monster-minotaur-skeleton` |
| `ghoul.webp` | — | — | `srd-5.2.1-2024-monster-ghoul` |
| `giant-spider.webp` | — | — | `srd-5.2.1-2024-monster-giant-spider` |
| `troll.webp` | `2014-troll` | — | `srd-5.2.1-2024-monster-troll` |
| `boar.webp` | — | `srd-boar` | `srd-5.2.1-2024-monster-boar` |
| `black-bear.webp` | `2014-black-bear` | `srd-black-bear` | `srd-5.2.1-2024-monster-black-bear` |
| `harpy.webp` | — | — | `srd-5.2.1-2024-monster-harpy` |
| `stirge.webp` | — | — | `srd-5.2.1-2024-monster-stirge` |
| `guard.webp` | `2014-guard` | `srd-guard` | `srd-5.2.1-2024-monster-guard` |
| `ape.webp` | `2014-ape` | — | `srd-5.2.1-2024-monster-ape` |
| `blood-hawk.webp` | `2014-blood-hawk` | `srd-blood-hawk` | `srd-5.2.1-2024-monster-blood-hawk` |
| `constrictor-snake.webp` | `2014-constrictor-snake` | `srd-constrictor-snake` | `srd-5.2.1-2024-monster-constrictor-snake` |
| `giant-rat.webp` | `2014-giant-rat` | `srd-giant-rat` | `srd-5.2.1-2024-monster-giant-rat` |
| `giant-wolf-spider.webp` | `2014-giant-wolf-spider` | `srd-giant-wolf-spider` | `srd-5.2.1-2024-monster-giant-wolf-spider` |
| `specter.webp` | — | — | `srd-5.2.1-2024-monster-specter` |
| `wight.webp` | — | — | `srd-5.2.1-2024-monster-wight` |
| `ghost.webp` | — | — | `srd-5.2.1-2024-monster-ghost` |
| `vampire-spawn.webp` | — | — | `srd-5.2.1-2024-monster-vampire-spawn` |
| `bandit.webp` | `2014-bandit` | `srd-bandit` | `srd-5.2.1-2024-monster-bandit` |
| `cultist.webp` | — | `srd-cultist` | `srd-5.2.1-2024-monster-cultist` |
| `priest.webp` | — | — | `srd-5.2.1-2024-monster-priest` |
| `knight.webp` | — | `srd-knight` | `srd-5.2.1-2024-monster-knight` |
| `mage.webp` | — | — | `srd-5.2.1-2024-monster-mage` |
| `imp.webp` | — | — | `srd-5.2.1-2024-monster-imp` |
| `quasit.webp` | — | — | `srd-5.2.1-2024-monster-quasit` |
| `pegasus.webp` | `2014-pegasus` | `srd-pegasus` | `srd-5.2.1-2024-monster-pegasus` |
| `griffon.webp` | `2014-griffon` | `srd-griffon` | `srd-5.2.1-2024-monster-griffon` |
| `hippogriff.webp` | `2014-hippogriff` | `srd-hippogriff` | `srd-5.2.1-2024-monster-hippogriff` |
| `basilisk.webp` | — | — | `srd-5.2.1-2024-monster-basilisk` |
| `cockatrice.webp` | — | — | `srd-5.2.1-2024-monster-cockatrice` |
| `chimera.webp` | `2014-chimera` | — | `srd-5.2.1-2024-monster-chimera` |
| `hydra.webp` | — | — | `srd-5.2.1-2024-monster-hydra` |
| `medusa.webp` | — | — | `srd-5.2.1-2024-monster-medusa` |
| `gorgon.webp` | — | — | `srd-5.2.1-2024-monster-gorgon` |
| `aboleth.webp` | — | — | `srd-5.2.1-2024-monster-aboleth` |
| `adult-black-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-black-dragon` |
| `adult-blue-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-blue-dragon` |
| `adult-brass-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-brass-dragon` |
| `adult-bronze-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-bronze-dragon` |
| `adult-copper-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-copper-dragon` |
| `adult-gold-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-gold-dragon` |
| `adult-green-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-green-dragon` |
| `adult-red-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-red-dragon` |
| `adult-silver-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-silver-dragon` |
| `adult-white-dragon.webp` | — | — | `srd-5.2.1-2024-monster-adult-white-dragon` |
| `air-elemental.webp` | — | — | `srd-5.2.1-2024-monster-air-elemental` |
| `animated-armor.webp` | — | `srd-animated-armor` | `srd-5.2.1-2024-monster-animated-armor` |
| `ankheg.webp` | — | — | `srd-5.2.1-2024-monster-ankheg` |
| `azer.webp` | — | — | `srd-5.2.1-2024-monster-azer-sentinel` |
| `balor.webp` | — | — | `srd-5.2.1-2024-monster-balor` |
| `barbed-devil.webp` | — | — | `srd-5.2.1-2024-monster-barbed-devil` |
| `bearded-devil.webp` | — | — | `srd-5.2.1-2024-monster-bearded-devil` |
| `black-pudding.webp` | — | — | `srd-5.2.1-2024-monster-black-pudding` |
| `bone-devil.webp` | — | — | `srd-5.2.1-2024-monster-bone-devil` |
| `centaur.webp` | — | — | `srd-5.2.1-2024-monster-centaur-trooper` |
| `chuul.webp` | — | — | `srd-5.2.1-2024-monster-chuul` |
| `cloaker.webp` | — | — | `srd-5.2.1-2024-monster-cloaker` |
| `earth-elemental.webp` | — | `srd-earth-elemental` | `srd-5.2.1-2024-monster-earth-elemental` |
| `fire-elemental.webp` | — | — | `srd-5.2.1-2024-monster-fire-elemental` |
| `pit-fiend.webp` | — | — | `srd-5.2.1-2024-monster-pit-fiend` |
| `water-elemental.webp` | — | — | `srd-5.2.1-2024-monster-water-elemental` |

Every other monster still uses `figure-portraits.js`. See `ART_SHOPPING_LIST.md` for the remaining missing/inaccurate table.
