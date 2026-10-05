(() => {
  "use strict";

  const esc = (value) => String(value || "Creature").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[char]));

  const SHAPES = {
    humanoid: '<circle cx="50" cy="24" r="11"/><path d="M34 86 38 46q12-10 24 0l4 40-9 2-5-26-2 26H46l-2-26-5 26z"/><path d="m66 46 15-16 4 4-13 20z"/>',
    goblin: '<path d="M28 22 18 10l8 4 10 10 6-12 6 12 10-10 8-4-10 12h-36z"/><circle cx="50" cy="30" r="10"/><path d="M38 84 41 50q9-8 18 0l3 34-8 2-3-20-2 20H46l-2-20-3 20z"/>',
    hobgoblin: '<circle cx="50" cy="22" r="12"/><path d="M29 86 35 46q15-12 30 0l6 40-11 3-6-26-3 26H49l-3-26-6 26z"/><path d="m72 48 14-12 4 5-12 16z"/>',
    kobold: '<path d="M42 20 34 8l8 8 8-10 8 10 8-8-8 12z"/><ellipse cx="50" cy="30" rx="11" ry="9"/><path d="M40 82 43 50q7-8 14 0l3 32z"/><path d="M62 58q18 8 16 28-10-8-16-20z"/>',
    skeleton: '<ellipse cx="50" cy="22" rx="11" ry="12"/><path d="M42 32h16l-2 6H44z"/><path d="M40 42h20v3H40zm0 7h20v3H40zm0 7h20v3H40z"/><path d="M38 86 42 44h5l2 28 2-28h5l4 42-8 2-3-22H49l-3 22z"/>',
    brute: '<circle cx="50" cy="23" r="14"/><path d="M20 80 28 44q22-14 44 0l8 36-13 4-8-24-3 28H44l-3-28-8 24z"/><path d="M24 44 8 62l7 5 18-16zM76 44l16 18-7 5-18-16z"/>',
    troll: '<path d="M48 8h6l2 10-10 2z"/><circle cx="50" cy="24" r="12"/><path d="M36 86 40 50q10-10 20 0l4 36z"/><path d="M22 88 36 48l8 4-8 36zm56 0L64 48l-8 4 8 36z"/>',
    quadruped: '<ellipse cx="56" cy="56" rx="30" ry="17"/><circle cx="23" cy="48" r="12"/><path d="M29 66 24 88h8l6-24zm38 0 4 22h8l-3-28zM80 50q16-10 16-22-8 14-22 16z"/>',
    bear: '<ellipse cx="56" cy="56" rx="31" ry="21"/><circle cx="23" cy="47" r="14"/><circle cx="14" cy="34" r="6"/><circle cx="30" cy="33" r="6"/><path d="m34 68-5 20h10l6-21zm33 0 4 20h10l-4-23z"/>',
    owlbear: '<ellipse cx="56" cy="58" rx="30" ry="20"/><path d="M10 46q8-22 28-16 4-10 14-8 10 2 12 12 16 2 20 16-8 8-22 6l-8-8-10 8q-18 4-34-10z"/><path d="M28 48 16 58l16 4z"/><path d="m36 70-4 18h10l5-18zm32 0 4 18h10l-5-20z"/>',
    hoofed: '<ellipse cx="56" cy="56" rx="29" ry="15"/><path d="M28 50 18 30l6-3 13 21z"/><circle cx="21" cy="40" r="10"/><path d="m40 64-4 24h7l7-24zm30 0 4 24h7l-2-27zM10 30 6 14l4-2 7 16zm13-2 6-15 5 3-5 17z"/>',
    unicorn: '<ellipse cx="58" cy="58" rx="28" ry="14"/><path d="M34 48 22 28l18-20 4 16 10 16z"/><circle cx="24" cy="42" r="10"/><path d="m42 66-3 22h7l6-22zm28 0 3 22h7l-2-24z"/>',
    reptile: '<path d="M8 52q9-18 28-13l40 9 18-9-12 16 12 14-20-8-38 8Q14 70 8 52Z"/><path d="m33 66-12 18 8 3 14-18zm34-2 9 20 8-4-7-19z"/>',
    dragon: '<path d="M6 58q10-20 30-14l28 6 18-22 14 6-10 18 16 10-22 2-16 12-14 2-6 22H28l6-22Q16 72 6 58Z"/><path d="M40 28 18 8l22 14 16-16 6 20z"/><path d="m68 58 10 28H66l-8-24z"/>',
    theropod: '<path d="M9 54q9-18 30-16l25 5 20-16 13 4-9 15 9 9-20 2-16 9-15 1-5 22H29l5-23Q18 66 9 54Z"/><path d="m32 46-20-9 17 16zm32 15 11 26H63l-9-22z"/>',
    snake: '<path fill="none" stroke="currentColor" stroke-width="13" stroke-linecap="round" d="M18 72q22 20 48 1T77 39Q68 19 47 26T23 42"/><path d="M14 32 29 24l8 12-16 9z"/>',
    crab: '<ellipse cx="50" cy="58" rx="24" ry="17"/><path d="M27 50 10 37 3 47l18 13zm46 0 17-13 7 10-18 13z"/><circle cx="10" cy="34" r="9"/><circle cx="90" cy="34" r="9"/>',
    scorpion: '<ellipse cx="48" cy="62" rx="20" ry="14"/><path d="M28 56 8 44l8 16zm44 0 22-10-6 16zM70 48q24-28 8-40-2 16-16 22z"/><path d="M62 40 78 8l8 6-10 30z"/>',
    bird: '<path d="M49 47 7 21l23 38-18 17 35-12 3 26 7-27 35 13-18-18 20-37-39 25z"/><circle cx="52" cy="28" r="10"/><path d="m60 27 18 5-17 7z"/>',
    bat: '<path d="M49 50 8 24l11 21-12 8 19 8-6 18 27-16 3 27 7-27 27 16-6-18 19-8-12-8 10-21-38 25z"/><circle cx="52" cy="31" r="9"/>',
    pterosaur: '<path d="M48 49 3 23l30 7 16 12 16-12 32-7-43 28 3 31-10-23z"/><path d="M48 38 34 16l17 8 13-7-8 22z"/>',
    "aquatic-reptile": '<ellipse cx="58" cy="60" rx="29" ry="16"/><path d="M35 56 22 27Q18 14 31 10l8 6-8 8 14 28z"/><path d="M36 68 15 83l3 7 26-13z"/>',
    fish: '<path d="M8 50q18-24 46-18 20 4 28 18-8 14-28 18-28 6-46-18z"/><path d="M78 50 96 32v36z"/><circle cx="28" cy="46" r="3"/>',
    "aquatic-mammal": '<path d="M6 58q16-26 50-20 22 4 30 16-6 8-20 10l6 16-16-8q-28 8-50-14z"/><path d="M84 48 98 30l-6 22z"/>',
    spider: '<ellipse cx="50" cy="55" rx="17" ry="22"/><circle cx="50" cy="31" r="11"/><path fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round" d="M37 44 17 29M35 53 10 48M35 62 12 72M40 70 24 89M63 44l20-15M65 53l25-5M65 62l23 10M60 70l16 19"/>',
    "winged-insect": '<ellipse cx="50" cy="56" rx="10" ry="26"/><circle cx="50" cy="25" r="8"/><ellipse cx="29" cy="49" rx="17" ry="28" transform="rotate(35 29 49)"/><ellipse cx="71" cy="49" rx="17" ry="28" transform="rotate(-35 71 49)"/>',
    centipede: '<path fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round" d="M12 63q18-42 38-12t38-10"/>',
    insect: '<ellipse cx="50" cy="58" rx="14" ry="27"/><circle cx="50" cy="25" r="9"/>',
    plant: '<path d="M45 90V50Q28 45 19 28q21 2 31 15Q60 23 82 19 75 40 57 49v41z"/>',
    fungus: '<path d="M22 48q8-28 28-28t28 28H22z"/><path d="M44 48h12v40H44z"/><circle cx="30" cy="70" r="6"/><circle cx="70" cy="64" r="5"/>',
    frog: '<ellipse cx="50" cy="61" rx="27" ry="21"/><circle cx="35" cy="38" r="10"/><circle cx="65" cy="38" r="10"/><path d="M31 69 8 82l5 8 30-12z"/>',
    primate: '<circle cx="50" cy="26" r="13"/><path d="M31 78q-5-31 19-36 25 5 19 36l-13-1-6-22-6 22z"/><path d="M36 48 14 70l7 6 22-18z"/>',
    hippogriff: '<path d="M18 52 4 28l22 8 12 10 18-28 22-8-16 30 20 8-8 10-28-4-10 22H22l8-22z"/><circle cx="28" cy="36" r="8"/><path d="m34 36 16 2-14 8z"/>',
    gargoyle: '<path d="M18 40 4 18l24 10 8-16 12 16 24-10-14 22 22 18-20 4-8 28H28l-4-28-18-4z"/><circle cx="42" cy="34" r="8"/>',
    weapon: '<path d="M62 8 92 38 58 72 42 56z"/><path d="M42 56 18 80l10 8 24-24z"/><path d="M38 52h28v8H38z"/>',
    swarm: '<circle cx="24" cy="30" r="8"/><circle cx="46" cy="22" r="7"/><circle cx="68" cy="28" r="9"/><circle cx="32" cy="52" r="8"/><circle cx="56" cy="48" r="10"/><circle cx="78" cy="54" r="7"/><circle cx="40" cy="74" r="8"/><circle cx="64" cy="76" r="9"/>',
    unknown: '<circle cx="50" cy="50" r="34" fill="none" stroke="currentColor" stroke-width="8"/><path d="M38 39q2-15 15-15 14 0 14 12 0 8-10 13-7 4-7 12" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><circle cx="50" cy="75" r="5"/>',
  };

  function keyFor(template, info) {
    const name = String(template?.name || "").toLowerCase();
    const detail = String(info?.detail || "").toLowerCase();
    const blob = `${name} ${detail}`;
    if (/unicorn/.test(blob)) return "unicorn";
    if (/owlbear/.test(blob)) return "owlbear";
    if (/troll/.test(blob)) return "troll";
    if (/(^| )goblin/.test(` ${blob}`) && !/hobgoblin/.test(blob)) return "goblin";
    if (/hobgoblin/.test(blob)) return "hobgoblin";
    if (/kobold/.test(blob)) return "kobold";
    if (/skeleton/.test(blob) && (info.form === "humanoid" || info.form === "unknown")) return "skeleton";
    if (/dragon|wyvern/.test(blob)) return "dragon";
    if (/violet fungus|fungus/.test(blob)) return "fungus";
    if (/\bsnake\b/.test(blob)) return "snake";
    if (/(^| )ape\b/.test(` ${name}`)) return "primate";
    if (/lion|winter wolf/.test(blob)) return "quadruped";
    if (/elephant|mammoth/.test(blob)) return "hoofed";
    if (/quipper|sea horse/.test(blob)) return "fish";
    if (/roc\b/.test(blob)) return "bird";
    if (/twig blight/.test(blob)) return "plant";
    if (/pegasus/.test(blob)) return "hippogriff";
    if (/(fire|frost|hill|stone) giant/.test(blob)) return "brute";
    if (info?.form && info.form !== "unknown" && SHAPES[info.form]) return info.form;
    const guessed = window.IRON_PIT_FIGURE_VISUALS?.inferredProfile?.(name)?.form;
    return guessed && guessed !== "unknown" && SHAPES[guessed] ? guessed : "humanoid";
  }

  function markup(template) {
    try {
      const info = window.IRON_PIT_FIGURE_VISUALS?.profile(template) || { form: "unknown", detail: "unknown" };
      const key = keyFor(template, info);
      const title = esc(template?.name);
      return `<svg class="portrait-svg" viewBox="0 0 100 100" role="img" aria-label="${title}"><title>${title}</title><g class="portrait-ink">${SHAPES[key] || SHAPES.unknown}</g></svg>`;
    } catch (error) {
      console.error("Failed to render figure portrait", { templateId: template?.id, error });
      throw error;
    }
  }

  window.IRON_PIT_FIGURE_PORTRAITS = { keyFor, markup };
})();
