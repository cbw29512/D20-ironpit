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
      return `<img class="portrait-image ${kind}" src="${attr(asset.src)}"${srcset} sizes="${sizes}" alt="${alt}" loading="lazy" decoding="async" onerror="this.classList.add('is-broken');this.removeAttribute('src');const frame=this.closest('.fighter-portrait');if(frame)frame.classList.add('art-broken');"${position}>`;
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
    ["ape", "Ape", ["2014-ape", "srd-5.2.1-2024-monster-ape"]], ["bandit", "Bandit", ["2014-bandit", "srd-bandit"]],
    ["basilisk", "Basilisk", ["srd-5.2.1-2024-monster-basilisk"]], ["berserker", "Berserker", ["2014-berserker", "srd-5.2.1-2024-monster-berserker"]],
    ["black-bear", "Black Bear", ["2014-black-bear", "srd-black-bear"]], ["blood-hawk", "Blood Hawk", ["2014-blood-hawk", "srd-blood-hawk"]],
    ["blue-dragon-wyrmling", "Blue Dragon Wyrmling", ["2014-blue-dragon-wyrmling", "srd-blue-dragon-wyrmling"]], ["boar", "Boar", ["srd-boar"]],
    ["brown-bear", "Brown Bear", ["2014-brown-bear", "srd-brown-bear"]], ["bugbear-warrior", "Bugbear Warrior", ["srd-5.2.1-2024-monster-bugbear-warrior"]],
    ["chimera", "Chimera", ["2014-chimera", "srd-5.2.1-2024-monster-chimera"]], ["cockatrice", "Cockatrice", ["srd-5.2.1-2024-monster-cockatrice"]],
    ["constrictor-snake", "Constrictor Snake", ["2014-constrictor-snake", "srd-constrictor-snake"]], ["crocodile", "Crocodile", ["2014-crocodile", "srd-crocodile"]],
    ["cultist", "Cultist", ["srd-cultist"]], ["dire-wolf", "Dire Wolf", ["2014-dire-wolf", "srd-dire-wolf"]],
    ["elephant", "Elephant", ["2014-elephant", "srd-5.2.1-2024-monster-elephant"]], ["ghost", "Ghost", ["srd-5.2.1-2024-monster-ghost"]],
    ["ghoul", "Ghoul", ["srd-5.2.1-2024-monster-ghoul"]], ["giant-ape", "Giant Ape", ["2014-giant-ape", "srd-5.2.1-2024-monster-giant-ape"]],
    ["giant-constrictor-snake", "Giant Constrictor Snake", ["2014-giant-constrictor-snake", "srd-giant-constrictor-snake"]],
    ["giant-crocodile", "Giant Crocodile", ["2014-giant-crocodile", "srd-giant-crocodile"]], ["giant-rat", "Giant Rat", ["2014-giant-rat", "srd-giant-rat"]],
    ["giant-scorpion", "Giant Scorpion", ["2014-giant-scorpion", "srd-giant-scorpion"]], ["giant-spider", "Giant Spider", ["srd-5.2.1-2024-monster-giant-spider"]],
    ["giant-wolf-spider", "Giant Wolf Spider", ["2014-giant-wolf-spider", "srd-giant-wolf-spider"]],
    ["goblin", "Goblin", ["2014-goblin", "srd-goblin-warrior", "srd-5.2.1-2024-monster-goblin-warrior"]],
    ["goblin-boss", "Goblin Boss", ["srd-goblin-boss"]], ["goblin-minion", "Goblin Minion", ["srd-goblin-minion"]],
    ["gorgon", "Gorgon", ["srd-5.2.1-2024-monster-gorgon"]], ["griffon", "Griffon", ["2014-griffon", "srd-griffon"]],
    ["guard", "Guard", ["2014-guard", "srd-guard"]], ["harpy", "Harpy", ["srd-5.2.1-2024-monster-harpy"]],
    ["hell-hound", "Hell Hound", ["2014-hell-hound", "srd-hell-hound"]], ["hippogriff", "Hippogriff", ["2014-hippogriff", "srd-hippogriff"]],
    ["hippopotamus", "Hippopotamus", ["srd-hippopotamus"]], ["hobgoblin-warrior", "Hobgoblin Warrior", ["srd-hobgoblin-warrior"]],
    ["hydra", "Hydra", ["srd-5.2.1-2024-monster-hydra"]], ["imp", "Imp", ["srd-5.2.1-2024-monster-imp"]],
    ["knight", "Knight", ["srd-knight"]], ["mage", "Mage", ["srd-5.2.1-2024-monster-mage"]],
    ["manticore", "Manticore", ["srd-manticore"]], ["medusa", "Medusa", ["srd-5.2.1-2024-monster-medusa"]],
    ["minotaur", "Minotaur", ["2014-minotaur"]], ["minotaur-of-baphomet", "Minotaur of Baphomet", ["srd-5.2.1-2024-monster-minotaur-of-baphomet"]],
    ["minotaur-skeleton", "Minotaur Skeleton", ["2014-minotaur-skeleton", "srd-minotaur-skeleton"]],
    ["ogre", "Ogre", ["2014-ogre", "srd-ogre"]], ["ogre-zombie", "Ogre Zombie", ["2014-ogre-zombie", "srd-ogre-zombie"]],
    ["owlbear", "Owlbear", ["2014-owlbear", "srd-owlbear"]], ["pegasus", "Pegasus", ["2014-pegasus", "srd-pegasus"]],
    ["priest", "Priest", ["srd-5.2.1-2024-monster-priest"]], ["quasit", "Quasit", ["srd-5.2.1-2024-monster-quasit"]],
    ["red-dragon-wyrmling", "Red Dragon Wyrmling", ["2014-red-dragon-wyrmling", "srd-red-dragon-wyrmling"]],
    ["roc", "Roc", ["2014-roc", "srd-5.2.1-2024-monster-roc"]], ["skeleton", "Skeleton", ["2014-skeleton", "srd-skeleton"]],
    ["specter", "Specter", ["srd-5.2.1-2024-monster-specter"]], ["stirge", "Stirge", ["srd-5.2.1-2024-monster-stirge"]],
    ["triceratops", "Triceratops", ["2014-triceratops", "srd-triceratops"]], ["troll", "Troll", ["2014-troll", "srd-5.2.1-2024-monster-troll"]],
    ["tyrannosaurus-rex", "Tyrannosaurus Rex", ["2014-tyrannosaurus-rex", "srd-tyrannosaurus-rex"]],
    ["unicorn", "Unicorn", ["2014-unicorn", "srd-5.2.1-2024-monster-unicorn"]],
    ["vampire-spawn", "Vampire Spawn", ["srd-5.2.1-2024-monster-vampire-spawn"]],
    ["warhorse-skeleton", "Warhorse Skeleton", ["2014-warhorse-skeleton", "srd-warhorse-skeleton"]],
    ["wight", "Wight", ["srd-5.2.1-2024-monster-wight"]], ["wolf", "Wolf", ["2014-wolf", "srd-wolf"]],
    ["worg", "Worg", ["2014-worg", "srd-worg"]], ["wyvern", "Wyvern", ["2014-wyvern", "srd-wyvern"]],
    ["young-black-dragon", "Young Black Dragon", ["2014-young-black-dragon", "srd-young-black-dragon"]],
    ["young-red-dragon", "Young Red Dragon", ["2014-young-red-dragon", "srd-young-red-dragon"]],
    ["zombie", "Zombie", ["2014-zombie", "srd-zombie"]],
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
