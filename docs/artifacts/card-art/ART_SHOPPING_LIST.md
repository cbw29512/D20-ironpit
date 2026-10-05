# Iron Pit card-art shopping list

Generated from this presentation branch. Hero pregens have framed color portraits. Twenty-six approved monster silhouettes are framed to 3:4; remaining monsters keep SVG glyphs.

**Real-art inventory:** `docs/artifacts/card-art/REAL_ART_INVENTORY.md`. All 24 unique pregens have framed color portraits. Do not treat pipeline demo drawings as source pictures.

Live examples: `docs/artifacts/card-art/before-after-2014-2024-karnok-seraphine.png` and `docs/artifacts/card-art/before-after-monsters.png`.

- **Heroes keep full-color portraits**, one per character per edition, reused across levels 1–20. Frame/crop with `--mode color-frame`.
- **Approved monster silhouettes** keep their gold rim and amber vignette. Reframe with `--mode vignette-contain` so the whole creature fits; do not recut them through `--mode silhouette`.

Keep licensed originals and processed assets in separate folders. Never overwrite originals.

```bash
python scripts/process_portrait_silhouettes.py \
  --mode color-frame \
  --input frontend/assets/portraits/originals/heroes \
  --output frontend/assets/portraits/heroes

python scripts/process_portrait_silhouettes.py \
  --mode vignette-contain \
  --input frontend/assets/portraits/originals/monsters \
  --output frontend/assets/portraits/monsters
```

Status key:

- `missing` — no licensed source picture yet
- `inaccurate` — current on-card fallback still depicts the wrong creature or omits a printed defining feature
- `good` — licensed source is framed (hero) or silhouetted (monster) correctly

## Unique pregens (one portrait each, reused for levels 1–20)

### 2014 — 12 characters

| Portrait id | Name | Class | Status |
|---|---|---|---|
| `hero-2014-barbarian` | Rokhan Stonefury | Barbarian | good |
| `hero-2014-bard` | Lyra Silverstring | Bard | good |
| `hero-2014-cleric` | Seraphine Dawnshield | Cleric | good |
| `hero-2014-druid` | Thalen Greenbough | Druid | good |
| `hero-2014-fighter` | Karnok Stoneward | Fighter | good |
| `hero-2014-monk` | Kael Stillwater | Monk | good |
| `hero-2014-paladin` | Aurelia Brightshield | Paladin | good |
| `hero-2014-ranger` | Rowan Ashtrail | Ranger | good |
| `hero-2014-rogue` | Mara Quickstep | Rogue | good |
| `hero-2014-sorcerer` | Nyra Emberveil | Sorcerer | good |
| `hero-2014-warlock` | Varek Ashenmark | Warlock | good |
| `hero-2014-wizard` | Elian Starweaver | Wizard | good |

### 2024 — 12 characters

| Portrait id | Name | Class | Status |
|---|---|---|---|
| `hero-2024-barbarian` | Rokhan Stonefury | Barbarian | good |
| `hero-2024-bard` | Lyra Silverstring | Bard | good |
| `hero-2024-cleric` | Seraphine Dawnshield | Cleric | good |
| `hero-2024-druid` | Thalen Greenbough | Druid | good |
| `hero-2024-fighter` | Karnok Stoneward | Fighter | good |
| `hero-2024-monk` | Kael Stillwater | Monk | good |
| `hero-2024-paladin` | Aurelia Brightshield | Paladin | good |
| `hero-2024-ranger` | Rowan Ashtrail | Ranger | good |
| `hero-2024-rogue` | Mara Quickstep | Rogue | good |
| `hero-2024-sorcerer` | Nyra Emberveil | Sorcerer | good |
| `hero-2024-warlock` | Varek Ashenmark | Warlock | good |
| `hero-2024-wizard` | Elian Starweaver | Wizard | good |

Edition isolation is mandatory: do not reuse a 2014 portrait for the 2024 counterpart.

## Monsters (one portrait per creature per edition)

### 2014 certified card roster — 131 (inaccurate: 4)

| Id | Name | Type | CR | Status | Why |
|---|---|---|---|---|---|
| `2014-allosaurus` | Allosaurus | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-ankylosaurus` | Ankylosaurus | beast | 3 | inaccurate | Generic reptile omits the printed club tail and armor plates. |
| `2014-ape` | Ape | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-awakened-shrub` | Awakened Shrub | plant | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-awakened-tree` | Awakened Tree | plant | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-axe-beak` | Axe Beak | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-baboon` | Baboon | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-badger` | Badger | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-bandit` | Bandit | humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-bat` | Bat | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-berserker` | Berserker | humanoid | 2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-black-bear` | Black Bear | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-black-dragon-wyrmling` | Black Dragon Wyrmling | dragon | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-blood-hawk` | Blood Hawk | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-blue-dragon-wyrmling` | Blue Dragon Wyrmling | dragon | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-brown-bear` | Brown Bear | beast | 1 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-camel` | Camel | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-cat` | Cat | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-chimera` | Chimera | monstrosity | 6 | inaccurate | Generic outline omits the printed lion, goat, and dragon heads. |
| `2014-commoner` | Commoner | humanoid | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-constrictor-snake` | Constrictor Snake | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-crab` | Crab | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-crocodile` | Crocodile | beast | 1/2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-deer` | Deer | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-dire-wolf` | Dire Wolf | beast | 1 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-draft-horse` | Draft Horse | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-eagle` | Eagle | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-elephant` | Elephant | beast | 4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-elk` | Elk | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-fire-giant` | Fire Giant | giant | 9 | missing | Needs a licensed source picture of this printed creature. |
| `2014-flying-snake` | Flying Snake | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-frost-giant` | Frost Giant | giant | 8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-ape` | Giant Ape | beast | 7 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-giant-badger` | Giant Badger | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-bat` | Giant Bat | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-centipede` | Giant Centipede | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-constrictor-snake` | Giant Constrictor Snake | beast | 2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-giant-crab` | Giant Crab | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-crocodile` | Giant Crocodile | beast | 5 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-eagle` | Giant Eagle | beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-elk` | Giant Elk | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-fire-beetle` | Giant Fire Beetle | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-goat` | Giant Goat | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-lizard` | Giant Lizard | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-owl` | Giant Owl | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-poisonous-snake` | Giant Poisonous Snake | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-rat` | Giant Rat | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-scorpion` | Giant Scorpion | beast | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-giant-sea-horse` | Giant Sea Horse | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-shark` | Giant Shark | beast | 5 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-vulture` | Giant Vulture | beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-wasp` | Giant Wasp | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-weasel` | Giant Weasel | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-giant-wolf-spider` | Giant Wolf Spider | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-goat` | Goat | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-goblin` | Goblin | humanoid | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-green-dragon-wyrmling` | Green Dragon Wyrmling | dragon | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-griffon` | Griffon | monstrosity | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-guard` | Guard | humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-hawk` | Hawk | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-hell-hound` | Hell Hound | fiend | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-hill-giant` | Hill Giant | giant | 5 | missing | Needs a licensed source picture of this printed creature. |
| `2014-hippogriff` | Hippogriff | monstrosity | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-hunter-shark` | Hunter Shark | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-hyena` | Hyena | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-jackal` | Jackal | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-killer-whale` | Killer Whale | beast | 3 | missing | Needs a licensed source picture of this printed creature. |
| `2014-kobold` | Kobold | humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-lion` | Lion | beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-lizard` | Lizard | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-mammoth` | Mammoth | beast | 6 | missing | Needs a licensed source picture of this printed creature. |
| `2014-mastiff` | Mastiff | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-merfolk` | Merfolk | humanoid | 1/8 | inaccurate | Humanoid-with-legs silhouette omits the printed aquatic anatomy. |
| `2014-minotaur` | Minotaur | monstrosity | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-minotaur-skeleton` | Minotaur Skeleton | undead | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-mule` | Mule | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-noble` | Noble | humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-ogre` | Ogre | giant | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-ogre-zombie` | Ogre Zombie | undead | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-owl` | Owl | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-owlbear` | Owlbear | monstrosity | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-panther` | Panther | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-pegasus` | Pegasus | celestial | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-plesiosaurus` | Plesiosaurus | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-poisonous-snake` | Poisonous Snake | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-polar-bear` | Polar Bear | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-pony` | Pony | beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-pteranodon` | Pteranodon | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-quipper` | Quipper | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-rat` | Rat | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-raven` | Raven | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-red-dragon-wyrmling` | Red Dragon Wyrmling | dragon | 4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-reef-shark` | Reef Shark | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-rhinoceros` | Rhinoceros | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-riding-horse` | Riding Horse | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-roc` | Roc | monstrosity | 11 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-saber-toothed-tiger` | Saber-Toothed Tiger | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-satyr` | Satyr | fey | 1/2 | inaccurate | Generic humanoid outline omits goat legs and horns. |
| `2014-scorpion` | Scorpion | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-skeleton` | Skeleton | undead | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-spider` | Spider | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-spy` | Spy | humanoid | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-bats` | Swarm of Bats | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-insects` | Swarm of Insects | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-poisonous-snakes` | Swarm of Poisonous Snakes | beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-quippers` | Swarm of Quippers | beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-rats` | Swarm of Rats | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-swarm-of-ravens` | Swarm of Ravens | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-thug` | Thug | humanoid | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-tiger` | Tiger | beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `2014-tribal-warrior` | Tribal Warrior | humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-triceratops` | Triceratops | beast | 5 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-troll` | Troll | giant | 5 | missing | Needs a licensed source picture of this printed creature. |
| `2014-twig-blight` | Twig Blight | plant | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-tyrannosaurus-rex` | Tyrannosaurus Rex | beast | 8 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-unicorn` | Unicorn | celestial | 5 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-vulture` | Vulture | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-warhorse` | Warhorse | beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-warhorse-skeleton` | Warhorse Skeleton | undead | 1/2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-weasel` | Weasel | beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `2014-white-dragon-wyrmling` | White Dragon Wyrmling | dragon | 2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-winter-wolf` | Winter Wolf | monstrosity | 3 | missing | Needs a licensed source picture of this printed creature. |
| `2014-wolf` | Wolf | beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `2014-worg` | Worg | monstrosity | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `2014-wyvern` | Wyvern | dragon | 6 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-young-black-dragon` | Young Black Dragon | dragon | 7 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-young-blue-dragon` | Young Blue Dragon | dragon | 9 | missing | Needs a licensed source picture of this printed creature. |
| `2014-young-green-dragon` | Young Green Dragon | dragon | 8 | missing | Needs a licensed source picture of this printed creature. |
| `2014-young-red-dragon` | Young Red Dragon | dragon | 10 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `2014-young-white-dragon` | Young White Dragon | dragon | 6 | missing | Needs a licensed source picture of this printed creature. |
| `2014-zombie` | Zombie | undead | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |

### 2024 certified card roster — 140 (inaccurate: 7)

| Id | Name | Type | CR | Status | Why |
|---|---|---|---|---|---|
| `srd-allosaurus` | Allosaurus | Beast (Dinosaur) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-animated-armor` | Animated Armor | Construct | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-animated-flying-sword` | Animated Flying Sword | Construct | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-ankylosaurus` | Ankylosaurus | Beast (Dinosaur) | 3 | inaccurate | Generic reptile omits the printed club tail and armor plates. |
| `srd-archelon` | Archelon | Beast (Dinosaur) | 4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-awakened-shrub` | Awakened Shrub | Plant | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-awakened-tree` | Awakened Tree | Plant | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-axe-beak` | Axe Beak | Monstrosity | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-baboon` | Baboon | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-badger` | Badger | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-bandit` | Bandit | Humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-bandit-captain` | Bandit Captain | Humanoid | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-bat` | Bat | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-black-bear` | Black Bear | Beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-black-dragon-wyrmling` | Black Dragon Wyrmling | Dragon (Chromatic) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-blood-hawk` | Blood Hawk | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-blue-dragon-wyrmling` | Blue Dragon Wyrmling | Dragon (Chromatic) | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-boar` | Boar | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-brown-bear` | Brown Bear | Beast | 1 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-camel` | Camel | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-cat` | Cat | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-commoner` | Commoner | Humanoid | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-constrictor-snake` | Constrictor Snake | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-crab` | Crab | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-crocodile` | Crocodile | Beast | 1/2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-cultist` | Cultist | Humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-deer` | Deer | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-dire-wolf` | Dire Wolf | Beast | 1 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-draft-horse` | Draft Horse | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-druid` | Druid | Humanoid (Druid) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-eagle` | Eagle | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-earth-elemental` | Earth Elemental | Elemental | 5 | inaccurate | Generic brute omits the printed walking-stone anatomy. |
| `srd-elk` | Elk | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-flying-snake` | Flying Snake | Monstrosity | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-frog` | Frog | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-gargoyle` | Gargoyle | Elemental | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-badger` | Giant Badger | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-bat` | Giant Bat | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-boar` | Giant Boar | Beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-centipede` | Giant Centipede | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-constrictor-snake` | Giant Constrictor Snake | Beast | 2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-giant-crab` | Giant Crab | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-crocodile` | Giant Crocodile | Beast | 5 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-eagle` | Giant Eagle | Celestial | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-elk` | Giant Elk | Celestial | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-fire-beetle` | Giant Fire Beetle | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-goat` | Giant Goat | Beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-lizard` | Giant Lizard | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-owl` | Giant Owl | Celestial | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-rat` | Giant Rat | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-scorpion` | Giant Scorpion | Beast | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-giant-shark` | Giant Shark | Beast | 5 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-venomous-snake` | Giant Venomous Snake | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-vulture` | Giant Vulture | Monstrosity | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-wasp` | Giant Wasp | Beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-weasel` | Giant Weasel | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-giant-wolf-spider` | Giant Wolf Spider | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-goat` | Goat | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-goblin-boss` | Goblin Boss | Fey (Goblinoid) | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-goblin-minion` | Goblin Minion | Fey (Goblinoid) | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-goblin-warrior` | Goblin Warrior | Fey (Goblinoid) | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-green-dragon-wyrmling` | Green Dragon Wyrmling | Dragon (Chromatic) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-grick` | Grick | Aberration | 2 | inaccurate | Snake coil is the wrong anatomy for a tentacled worm-like aberration. |
| `srd-griffon` | Griffon | Monstrosity | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-grimlock` | Grimlock | Aberration | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-guard` | Guard | Humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-guard-captain` | Guard Captain | Humanoid | 4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hawk` | Hawk | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hell-hound` | Hell Hound | Fiend | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-hill-giant` | Hill Giant | Giant | 5 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hippogriff` | Hippogriff | Monstrosity | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hippopotamus` | Hippopotamus | Beast | 4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-hobgoblin-warrior` | Hobgoblin Warrior | Fey (Goblinoid) | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hunter-shark` | Hunter Shark | Beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-hyena` | Hyena | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-jackal` | Jackal | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-killer-whale` | Killer Whale | Beast | 3 | missing | Needs a licensed source picture of this printed creature. |
| `srd-knight` | Knight | Humanoid | 3 | missing | Needs a licensed source picture of this printed creature. |
| `srd-kobold-warrior` | Kobold Warrior | Dragon | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-lemure` | Lemure | Fiend (Devil) | 0 | inaccurate | Generic brute omits the printed molten, bloated devil anatomy. |
| `srd-lizard` | Lizard | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-manticore` | Manticore | Monstrosity | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-mastiff` | Mastiff | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-merfolk-skirmisher` | Merfolk Skirmisher | Elemental | 1/8 | inaccurate | Humanoid-with-legs silhouette omits the printed aquatic anatomy. |
| `srd-minotaur-skeleton` | Minotaur Skeleton | Undead | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-mule` | Mule | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-noble` | Noble | Humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-ogre` | Ogre | Giant | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-ogre-zombie` | Ogre Zombie | Undead | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-owl` | Owl | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-owlbear` | Owlbear | Monstrosity | 3 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-panther` | Panther | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-pegasus` | Pegasus | Celestial | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-piranha` | Piranha | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-plesiosaurus` | Plesiosaurus | Beast (Dinosaur) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-polar-bear` | Polar Bear | Beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-pony` | Pony | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-pteranodon` | Pteranodon | Beast (Dinosaur) | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-rat` | Rat | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-raven` | Raven | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-red-dragon-wyrmling` | Red Dragon Wyrmling | Dragon (Chromatic) | 4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-reef-shark` | Reef Shark | Beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-rhinoceros` | Rhinoceros | Beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-riding-horse` | Riding Horse | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-saber-toothed-tiger` | Saber-Toothed Tiger | Beast | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-sahuagin-warrior` | Sahuagin Warrior | Fiend | 1/2 | inaccurate | Humanoid-with-legs silhouette omits the printed aquatic anatomy. |
| `srd-scorpion` | Scorpion | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-scout` | Scout | Humanoid | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-skeleton` | Skeleton | Undead | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-spider` | Spider | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-spy` | Spy | Humanoid | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-bats` | Swarm of Bats | Swarm of Tiny Beasts | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-crawling-claws` | Swarm of Crawling Claws | Swarm of Tiny Undead | 3 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-insects` | Swarm of Insects | Swarm of Tiny Beasts | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-piranhas` | Swarm of Piranhas | Swarm of Tiny Beasts | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-rats` | Swarm of Rats | Swarm of Tiny Beasts | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-swarm-of-venomous-snakes` | Swarm of Venomous Snakes | Swarm of Tiny Beasts | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-tiger` | Tiger | Beast | 1 | missing | Needs a licensed source picture of this printed creature. |
| `srd-tough` | Tough | Humanoid | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-triceratops` | Triceratops | Beast (Dinosaur) | 5 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-tyrannosaurus-rex` | Tyrannosaurus Rex | Beast (Dinosaur) | 8 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-venomous-snake` | Venomous Snake | Beast | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-violet-fungus` | Violet Fungus | Plant | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-vulture` | Vulture | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-warhorse` | Warhorse | Beast | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-warhorse-skeleton` | Warhorse Skeleton | Undead | 1/2 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-warrior-infantry` | Warrior Infantry | Humanoid | 1/8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-warrior-veteran` | Warrior Veteran | Humanoid | 3 | missing | Needs a licensed source picture of this printed creature. |
| `srd-weasel` | Weasel | Beast | 0 | missing | Needs a licensed source picture of this printed creature. |
| `srd-white-dragon-wyrmling` | White Dragon Wyrmling | Dragon (Chromatic) | 2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-wolf` | Wolf | Beast | 1/4 | missing | Needs a licensed source picture of this printed creature. |
| `srd-worg` | Worg | Fey | 1/2 | missing | Needs a licensed source picture of this printed creature. |
| `srd-wyvern` | Wyvern | Dragon | 6 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-xorn` | Xorn | Elemental | 5 | inaccurate | Generic brute omits the printed radial three-arm, three-leg body. |
| `srd-young-black-dragon` | Young Black Dragon | Dragon (Chromatic) | 7 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-young-blue-dragon` | Young Blue Dragon | Dragon (Chromatic) | 9 | missing | Needs a licensed source picture of this printed creature. |
| `srd-young-green-dragon` | Young Green Dragon | Dragon (Chromatic) | 8 | missing | Needs a licensed source picture of this printed creature. |
| `srd-young-red-dragon` | Young Red Dragon | Dragon (Chromatic) | 10 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |
| `srd-young-white-dragon` | Young White Dragon | Dragon (Chromatic) | 6 | missing | Needs a licensed source picture of this printed creature. |
| `srd-zombie` | Zombie | Undead | 1/4 | good | Chris-approved 3:4 silhouette; same raster as the matching edition counterpart. |

The 2024 picker catalog also lists **330** SRD names. Extra uncertified rows still need one accurate portrait each when they become cards.

