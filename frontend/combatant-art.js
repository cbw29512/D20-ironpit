(() => {
  "use strict";

  const registry = new Map();

  function entryKey(entry) {
    return entry?.portrait_id || entry?.template_id || "";
  }

  function portraitId(template) {
    try {
      if (!template) return null;
      if (template.portrait_id) return String(template.portrait_id);
      if (template.kind === "character" && template.class_id && template.ruleset) {
        return `hero-${template.ruleset}-${template.class_id}`;
      }
      const raw = String(template.id || "");
      if (!raw) return null;
      if (template.kind === "character") return raw.replace(/-l\d+$/i, "") || raw;
      return raw;
    } catch (error) {
      console.error("Failed to derive combatant portrait id", { templateId: template?.id, error });
      throw error;
    }
  }

  function candidateIds(template) {
    const ids = [];
    const push = (value) => { if (value && !ids.includes(value)) ids.push(value); };
    const raw = String(template?.id || "");
    push(portraitId(template));
    push(template?.id);
    push(raw.replace(/-l\d+$/i, ""));
    push(raw.replace(/^catalog-/, ""));
    push(raw.replace(/^catalog-2014-/, ""));
    push(raw.replace(/^2014-/, ""));
    push(raw.replace(/^srd-5\.2\.1-2024-monster-/, ""));
    push(raw.replace(/^srd-/, ""));
    return ids;
  }

  function register(entries) {
    try {
      for (const entry of entries || []) {
        const key = entryKey(entry);
        if (!key || !entry?.src || !entry?.license || !entry?.source) {
          throw new Error("Combatant art entries require portrait_id or template_id, plus src, license, and source.");
        }
        if (registry.has(key)) throw new Error(`Duplicate combatant art entry: ${key}`);
        registry.set(key, Object.freeze({ ...entry, portrait_id: key }));
      }
    } catch (error) {
      console.error("Failed to register combatant artwork", { error });
      throw error;
    }
  }

  function assetFor(template) {
    try {
      for (const key of candidateIds(template)) {
        const asset = registry.get(key);
        if (asset) return asset;
      }
      return null;
    } catch (error) {
      console.error("Failed to resolve combatant artwork", { templateId: template?.id, error });
      throw error;
    }
  }

  function attr(value) {
    return String(value || "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[char]));
  }

  function markup(template) {
    try {
      const asset = assetFor(template);
      if (!asset) return null;
      const srcset = asset.srcset ? ` srcset="${attr(asset.srcset)}"` : "";
      const position = asset.object_position ? ` style="object-position:${attr(asset.object_position)}"` : "";
      const alt = attr(asset.alt || template?.name || "Combatant artwork");
      const sizes = attr(asset.sizes || "(max-width: 620px) 42vw, 12rem");
      const kind = template?.kind === "character" ? "portrait-image-hero" : "portrait-image-monster";
      return `<img class="portrait-image ${kind}" src="${attr(asset.src)}"${srcset} sizes="${sizes}" width="480" height="640" alt="${alt}" loading="lazy" decoding="async" onerror="this.classList.add('is-broken');this.removeAttribute('src');const frame=this.closest('.fighter-portrait');if(frame)frame.classList.add('art-broken');"${position}>`;
    } catch (error) {
      console.error("Failed to render combatant artwork", { templateId: template?.id, error });
      throw error;
    }
  }

  function provenance(template) {
    try {
      const asset = assetFor(template);
      if (!asset) return null;
      return { license: asset.license, source: asset.source };
    } catch (error) {
      console.error("Failed to resolve combatant artwork provenance", { templateId: template?.id, error });
      throw error;
    }
  }

  const HERO_NAMES = {
    barbarian: "Rokhan Stonefury", bard: "Lyra Silverstring", cleric: "Seraphine Dawnshield",
    druid: "Thalen Greenbough", fighter: "Karnok Stoneward", monk: "Kael Stillwater",
    paladin: "Aurelia Brightshield", ranger: "Rowan Ashtrail", rogue: "Mara Quickstep",
    sorcerer: "Nyra Emberveil", warlock: "Varek Ashenmark", wizard: "Elian Starweaver",
  };

  function heroPortraits() {
    const entries = [];
    for (const ruleset of ["2014", "2024"]) {
      for (const [classId, name] of Object.entries(HERO_NAMES)) {
        entries.push({
          portrait_id: `hero-${ruleset}-${classId}`,
          src: `assets/portraits/heroes/hero-${ruleset}-${classId}.webp`,
          alt: `${name} ${ruleset}`,
          license: "Iron Pit pregen portrait",
          source: "Chris-approved painterly pregen portraits",
        });
      }
    }
    return entries;
  }

  // file, printed name, extra roster/catalog ids. Same raster serves both editions.
  const MONSTER_ART = [
    ["aboleth", "Aboleth", []], ["adult-black-dragon", "Adult Black Dragon", []], ["adult-blue-dragon", "Adult Blue Dragon", []], ["adult-brass-dragon", "Adult Brass Dragon", []], ["adult-bronze-dragon", "Adult Bronze Dragon", []], ["adult-copper-dragon", "Adult Copper Dragon", []],
    ["adult-gold-dragon", "Adult Gold Dragon", []], ["adult-green-dragon", "Adult Green Dragon", []], ["adult-red-dragon", "Adult Red Dragon", []], ["adult-silver-dragon", "Adult Silver Dragon", []], ["adult-white-dragon", "Adult White Dragon", []], ["air-elemental", "Air Elemental", []],
    ["allosaurus", "Allosaurus", ["2014-allosaurus", "srd-allosaurus"]], ["ancient-black-dragon", "Ancient Black Dragon", []], ["ancient-blue-dragon", "Ancient Blue Dragon", []], ["ancient-brass-dragon", "Ancient Brass Dragon", []], ["ancient-bronze-dragon", "Ancient Bronze Dragon", []], ["ancient-copper-dragon", "Ancient Copper Dragon", []],
    ["ancient-gold-dragon", "Ancient Gold Dragon", []], ["ancient-green-dragon", "Ancient Green Dragon", []], ["ancient-red-dragon", "Ancient Red Dragon", []], ["ancient-silver-dragon", "Ancient Silver Dragon", []], ["ancient-white-dragon", "Ancient White Dragon", []], ["animated-armor", "Animated Armor", ["srd-animated-armor"]],
    ["animated-flying-sword", "Animated Flying Sword", ["srd-animated-flying-sword"]], ["animated-rug-of-smothering", "Animated Rug of Smothering", []], ["ankheg", "Ankheg", []], ["ankylosaurus", "Ankylosaurus", ["2014-ankylosaurus", "srd-ankylosaurus"]], ["ape", "Ape", ["2014-ape"]], ["archelon", "Archelon", ["srd-archelon"]],
    ["archmage", "Archmage", []], ["assassin", "Assassin", []], ["awakened-shrub", "Awakened Shrub", ["2014-awakened-shrub", "srd-awakened-shrub"]], ["awakened-tree", "Awakened Tree", ["2014-awakened-tree", "srd-awakened-tree"]], ["axe-beak", "Axe Beak", ["2014-axe-beak", "srd-axe-beak"]], ["azer", "Azer", ["srd-5.2.1-2024-monster-azer-sentinel"]],
    ["baboon", "Baboon", ["2014-baboon", "srd-baboon"]], ["badger", "Badger", ["2014-badger", "srd-badger"]], ["balor", "Balor", []], ["bandit", "Bandit", ["2014-bandit", "srd-bandit"]], ["bandit-captain", "Bandit Captain", ["srd-bandit-captain"]], ["barbed-devil", "Barbed Devil", []],
    ["basilisk", "Basilisk", []], ["bat", "Bat", ["2014-bat", "srd-bat"]], ["bearded-devil", "Bearded Devil", []], ["behir", "Behir", []], ["berserker", "Berserker", ["2014-berserker"]], ["black-bear", "Black Bear", ["2014-black-bear", "srd-black-bear"]],
    ["black-dragon-wyrmling", "Black Dragon Wyrmling", ["2014-black-dragon-wyrmling", "srd-black-dragon-wyrmling"]], ["black-pudding", "Black Pudding", []], ["blink-dog", "Blink Dog", []], ["blood-hawk", "Blood Hawk", ["2014-blood-hawk", "srd-blood-hawk"]], ["blue-dragon-wyrmling", "Blue Dragon Wyrmling", ["2014-blue-dragon-wyrmling", "srd-blue-dragon-wyrmling"]], ["boar", "Boar", ["srd-boar"]],
    ["bone-devil", "Bone Devil", []], ["brass-dragon-wyrmling", "Brass Dragon Wyrmling", []], ["bronze-dragon-wyrmling", "Bronze Dragon Wyrmling", []], ["brown-bear", "Brown Bear", ["2014-brown-bear", "srd-brown-bear"]], ["bugbear-stalker", "Bugbear Stalker", []], ["bugbear-warrior", "Bugbear Warrior", []],
    ["bulette", "Bulette", []], ["camel", "Camel", ["2014-camel", "srd-camel"]], ["cat", "Cat", ["2014-cat", "srd-cat"]], ["centaur", "Centaur", ["srd-5.2.1-2024-monster-centaur-trooper"]], ["chain-devil", "Chain Devil", []], ["chimera", "Chimera", ["2014-chimera"]],
    ["chuul", "Chuul", []], ["clay-golem", "Clay Golem", []], ["cloaker", "Cloaker", []], ["cloud-giant", "Cloud Giant", []], ["cockatrice", "Cockatrice", []], ["commoner", "Commoner", ["2014-commoner", "srd-commoner"]],
    ["constrictor-snake", "Constrictor Snake", ["2014-constrictor-snake", "srd-constrictor-snake"]], ["copper-dragon-wyrmling", "Copper Dragon Wyrmling", []], ["couatl", "Couatl", []], ["crocodile", "Crocodile", ["2014-crocodile", "srd-crocodile"]], ["cultist", "Cultist", ["srd-cultist"]], ["cultist-fanatic", "Cultist Fanatic", []],
    ["darkmantle", "Darkmantle", []], ["death-dog", "Death Dog", []], ["deer", "Deer", ["2014-deer", "srd-deer"]], ["deva", "Deva", []], ["dire-wolf", "Dire Wolf", ["2014-dire-wolf", "srd-dire-wolf"]], ["djinni", "Djinni", []],
    ["doppelganger", "Doppelganger", []], ["draft-horse", "Draft Horse", ["2014-draft-horse", "srd-draft-horse"]], ["dragon-turtle", "Dragon Turtle", []], ["dretch", "Dretch", []], ["drider", "Drider", []], ["druid", "Druid", ["srd-druid"]],
    ["dryad", "Dryad", []], ["dust-mephit", "Dust Mephit", []], ["eagle", "Eagle", ["2014-eagle", "srd-eagle"]], ["earth-elemental", "Earth Elemental", ["srd-earth-elemental"]], ["efreeti", "Efreeti", []], ["elephant", "Elephant", ["2014-elephant"]],
    ["elk", "Elk", ["2014-elk", "srd-elk"]], ["erinyes", "Erinyes", []], ["ettercap", "Ettercap", []], ["ettin", "Ettin", []], ["fire-elemental", "Fire Elemental", []], ["fire-giant", "Fire Giant", ["2014-fire-giant"]],
    ["flesh-golem", "Flesh Golem", []], ["flying-snake", "Flying Snake", ["2014-flying-snake", "srd-flying-snake"]], ["frog", "Frog", ["srd-frog"]], ["frost-giant", "Frost Giant", ["2014-frost-giant"]], ["gargoyle", "Gargoyle", ["srd-gargoyle"]], ["gelatinous-cube", "Gelatinous Cube", []],
    ["ghast", "Ghast", []], ["ghost", "Ghost", []], ["ghoul", "Ghoul", []], ["giant-ape", "Giant Ape", ["2014-giant-ape"]], ["giant-badger", "Giant Badger", ["2014-giant-badger", "srd-giant-badger"]], ["giant-bat", "Giant Bat", ["2014-giant-bat", "srd-giant-bat"]],
    ["giant-boar", "Giant Boar", ["srd-giant-boar"]], ["giant-centipede", "Giant Centipede", ["2014-giant-centipede", "srd-giant-centipede"]], ["giant-constrictor-snake", "Giant Constrictor Snake", ["2014-giant-constrictor-snake", "srd-giant-constrictor-snake"]], ["giant-crab", "Giant Crab", ["2014-giant-crab", "srd-giant-crab"]], ["giant-crocodile", "Giant Crocodile", ["2014-giant-crocodile", "srd-giant-crocodile"]], ["giant-eagle", "Giant Eagle", ["2014-giant-eagle", "srd-giant-eagle"]],
    ["giant-elk", "Giant Elk", ["2014-giant-elk", "srd-giant-elk"]], ["giant-fire-beetle", "Giant Fire Beetle", ["2014-giant-fire-beetle", "srd-giant-fire-beetle"]], ["giant-frog", "Giant Frog", []], ["giant-goat", "Giant Goat", ["2014-giant-goat", "srd-giant-goat"]], ["giant-hyena", "Giant Hyena", []], ["giant-lizard", "Giant Lizard", ["2014-giant-lizard", "srd-giant-lizard"]],
    ["giant-octopus", "Giant Octopus", []], ["giant-owl", "Giant Owl", ["2014-giant-owl", "srd-giant-owl"]], ["giant-rat", "Giant Rat", ["2014-giant-rat", "srd-giant-rat"]], ["giant-scorpion", "Giant Scorpion", ["2014-giant-scorpion", "srd-giant-scorpion"]], ["giant-seahorse", "Giant Seahorse", ["2014-giant-sea-horse"]], ["giant-shark", "Giant Shark", ["2014-giant-shark", "srd-giant-shark"]],
    ["giant-spider", "Giant Spider", []], ["giant-toad", "Giant Toad", []], ["giant-venomous-snake", "Giant Venomous Snake", ["srd-giant-venomous-snake", "2014-giant-poisonous-snake"]], ["giant-vulture", "Giant Vulture", ["2014-giant-vulture", "srd-giant-vulture"]], ["giant-wasp", "Giant Wasp", ["2014-giant-wasp", "srd-giant-wasp"]], ["giant-weasel", "Giant Weasel", ["2014-giant-weasel", "srd-giant-weasel"]],
    ["giant-wolf-spider", "Giant Wolf Spider", ["2014-giant-wolf-spider", "srd-giant-wolf-spider"]], ["gibbering-mouther", "Gibbering Mouther", []], ["glabrezu", "Glabrezu", []], ["gladiator", "Gladiator", []], ["gnoll-warrior", "Gnoll Warrior", []], ["goat", "Goat", ["2014-goat", "srd-goat"]],
    ["goblin", "Goblin", ["2014-goblin", "srd-goblin-warrior", "srd-5.2.1-2024-monster-goblin-warrior"]], ["goblin-boss", "Goblin Boss", ["srd-goblin-boss"]], ["goblin-minion", "Goblin Minion", ["srd-goblin-minion"]], ["gold-dragon-wyrmling", "Gold Dragon Wyrmling", []], ["gorgon", "Gorgon", []], ["gray-ooze", "Gray Ooze", []],
    ["green-dragon-wyrmling", "Green Dragon Wyrmling", ["2014-green-dragon-wyrmling", "srd-green-dragon-wyrmling"]], ["green-hag", "Green Hag", []], ["grick", "Grick", ["srd-grick"]], ["griffon", "Griffon", ["2014-griffon", "srd-griffon"]], ["grimlock", "Grimlock", ["srd-grimlock"]], ["guard", "Guard", ["2014-guard", "srd-guard"]],
    ["guard-captain", "Guard Captain", ["srd-guard-captain"]], ["guardian-naga", "Guardian Naga", []], ["half-dragon", "Half-Dragon", []], ["harpy", "Harpy", []], ["hawk", "Hawk", ["2014-hawk", "srd-hawk"]], ["hell-hound", "Hell Hound", ["2014-hell-hound", "srd-hell-hound"]],
    ["hezrou", "Hezrou", []], ["hill-giant", "Hill Giant", ["2014-hill-giant", "srd-hill-giant"]], ["hippogriff", "Hippogriff", ["2014-hippogriff", "srd-hippogriff"]], ["hippopotamus", "Hippopotamus", ["srd-hippopotamus"]], ["hobgoblin-captain", "Hobgoblin Captain", []], ["hobgoblin-warrior", "Hobgoblin Warrior", ["srd-hobgoblin-warrior"]],
    ["homunculus", "Homunculus", []], ["horned-devil", "Horned Devil", []], ["hunter-shark", "Hunter Shark", ["2014-hunter-shark", "srd-hunter-shark"]], ["hydra", "Hydra", []], ["hyena", "Hyena", ["2014-hyena", "srd-hyena"]], ["ice-mephit", "Ice Mephit", []],
    ["imp", "Imp", []], ["incubus", "Incubus", []], ["invisible-stalker", "Invisible Stalker", []], ["iron-golem", "Iron Golem", []], ["jackal", "Jackal", ["2014-jackal", "srd-jackal"]], ["killer-whale", "Killer Whale", ["2014-killer-whale", "srd-killer-whale"]],
    ["knight", "Knight", ["srd-knight"]], ["kobold-warrior", "Kobold Warrior", ["2014-kobold", "srd-kobold-warrior"]], ["kraken", "Kraken", []], ["lamia", "Lamia", []], ["lemure", "Lemure", ["srd-lemure"]], ["lich", "Lich", []],
    ["lion", "Lion", ["2014-lion"]], ["lizard", "Lizard", ["2014-lizard", "srd-lizard"]], ["mage", "Mage", []], ["magma-mephit", "Magma Mephit", []], ["magmin", "Magmin", []], ["mammoth", "Mammoth", ["2014-mammoth"]],
    ["manticore", "Manticore", ["srd-manticore"]], ["marilith", "Marilith", []], ["mastiff", "Mastiff", ["2014-mastiff", "srd-mastiff"]], ["medusa", "Medusa", []], ["merfolk", "Merfolk", ["2014-merfolk", "srd-merfolk-skirmisher", "srd-5.2.1-2024-monster-merfolk-skirmisher"]], ["merrow", "Merrow", []],
    ["mimic", "Mimic", []], ["minotaur", "Minotaur", ["2014-minotaur"]], ["minotaur-of-baphomet", "Minotaur of Baphomet", []], ["minotaur-skeleton", "Minotaur Skeleton", ["2014-minotaur-skeleton", "srd-minotaur-skeleton"]], ["mule", "Mule", ["2014-mule", "srd-mule"]], ["mummy", "Mummy", []],
    ["nalfeshnee", "Nalfeshnee", []], ["night-hag", "Night Hag", []], ["nightmare", "Nightmare", []], ["noble", "Noble", ["2014-noble", "srd-noble"]], ["ochre-jelly", "Ochre Jelly", []], ["octopus", "Octopus", []],
    ["ogre", "Ogre", ["2014-ogre", "srd-ogre"]], ["ogre-zombie", "Ogre Zombie", ["2014-ogre-zombie", "srd-ogre-zombie"]], ["oni", "Oni", []], ["otyugh", "Otyugh", []], ["owl", "Owl", ["2014-owl", "srd-owl"]], ["owlbear", "Owlbear", ["2014-owlbear", "srd-owlbear"]],
    ["pegasus", "Pegasus", ["2014-pegasus", "srd-pegasus"]], ["phase-spider", "Phase Spider", []], ["pit-fiend", "Pit Fiend", []], ["priest", "Priest", []], ["quasit", "Quasit", []], ["red-dragon-wyrmling", "Red Dragon Wyrmling", ["2014-red-dragon-wyrmling", "srd-red-dragon-wyrmling"]],
    ["roc", "Roc", ["2014-roc"]], ["skeleton", "Skeleton", ["2014-skeleton", "srd-skeleton"]], ["specter", "Specter", []], ["stirge", "Stirge", []], ["triceratops", "Triceratops", ["2014-triceratops", "srd-triceratops"]], ["troll", "Troll", ["2014-troll"]],
    ["tyrannosaurus-rex", "Tyrannosaurus Rex", ["2014-tyrannosaurus-rex", "srd-tyrannosaurus-rex"]], ["unicorn", "Unicorn", ["2014-unicorn"]], ["vampire-spawn", "Vampire Spawn", []], ["warhorse-skeleton", "Warhorse Skeleton", ["2014-warhorse-skeleton", "srd-warhorse-skeleton"]], ["water-elemental", "Water Elemental", []], ["wight", "Wight", []],
    ["wolf", "Wolf", ["2014-wolf", "srd-wolf"]], ["worg", "Worg", ["2014-worg", "srd-worg"]], ["wyvern", "Wyvern", ["2014-wyvern", "srd-wyvern"]], ["young-black-dragon", "Young Black Dragon", ["2014-young-black-dragon", "srd-young-black-dragon"]], ["young-red-dragon", "Young Red Dragon", ["2014-young-red-dragon", "srd-young-red-dragon"]], ["zombie", "Zombie", ["2014-zombie", "srd-zombie"]],
  ];

  function monsterPortraits() {
    const entries = [];
    for (const [fileId, name, ids] of MONSTER_ART) {
      const src = `assets/portraits/monsters/${fileId}.webp`;
      const keys = new Set([fileId, `srd-5.2.1-2024-monster-${fileId}`, ...ids]);
      for (const id of ids) { if (id.startsWith("2014-")) keys.add(`catalog-${id}`); }
      for (const key of keys) {
        entries.push({
          portrait_id: key, src, alt: name,
          license: "Iron Pit monster silhouette",
          source: "Chris-approved monster silhouettes",
        });
      }
    }
    return entries;
  }

  register(heroPortraits());
  register(monsterPortraits());
  window.IRON_PIT_COMBATANT_ART = { assetFor, candidateIds, markup, portraitId, provenance, register };
})();
