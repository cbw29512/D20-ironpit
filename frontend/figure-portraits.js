(() => {
  "use strict";

  const esc = (value) => String(value || "Creature").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[char]));

  const SHAPES = {
    humanoid: '<circle cx="50" cy="25" r="12"/><path d="M31 83 36 45Q50 36 64 45l5 38-10 2-6-28-2 28H40l-2-28-6 28z"/><path d="m66 46 16-18 4 4-14 22z"/>',
    brute: '<circle cx="50" cy="24" r="15"/><path d="M19 79 27 43Q50 31 73 43l8 36-13 4-8-25-3 29H43l-3-29-8 25z"/><path d="M23 44 8 61l7 5 18-16zM77 44l15 17-7 5-18-16z"/>',
    quadruped: '<ellipse cx="55" cy="55" rx="31" ry="18"/><circle cx="22" cy="48" r="13"/><path d="M28 65 23 88h9l7-25zm39 0 4 23h9l-3-29zM80 49q17-11 17-24-9 15-23 17z"/>',
    bear: '<ellipse cx="56" cy="56" rx="32" ry="22"/><circle cx="22" cy="47" r="15"/><circle cx="13" cy="34" r="6"/><circle cx="29" cy="33" r="6"/><path d="m33 68-5 20h11l6-21zm34 0 4 20h11l-4-23z"/>',
    hoofed: '<ellipse cx="56" cy="55" rx="30" ry="16"/><path d="M28 50 17 29l7-3 14 22z"/><circle cx="20" cy="39" r="11"/><path d="m39 64-4 25h8l7-25zm31 0 4 25h8l-2-28zM9 30 4 13l5-2 8 17zm14-2 7-16 5 3-5 18z"/>',
    reptile: '<path d="M8 51q9-18 29-13l41 9 18-9-12 16 12 14-21-8-38 8Q14 70 8 51Z"/><path d="m33 66-12 18 8 3 14-18zm34-2 9 20 8-4-7-19z"/>',
    snake: '<path fill="none" stroke="currentColor" stroke-width="13" stroke-linecap="round" d="M18 72q22 20 48 1T77 39Q68 19 47 26T23 42"/><path d="M14 32 29 24l8 12-16 9z"/>',
    crab: '<ellipse cx="50" cy="58" rx="25" ry="18"/><path d="M27 50 10 37 3 47l18 13zm46 0 17-13 7 10-18 13zM27 69 12 83l8 4 16-13zm46 0 15 14-8 4-16-13z"/><circle cx="10" cy="34" r="10"/><circle cx="90" cy="34" r="10"/>',
    bird: '<path d="M49 47 7 21l23 38-18 17 35-12 3 26 7-27 35 13-18-18 20-37-39 25z"/><circle cx="52" cy="28" r="10"/><path d="m60 27 18 5-17 7z"/>',
    bat: '<path d="M49 50 8 24l11 21-12 8 19 8-6 18 27-16 3 27 7-27 27 16-6-18 19-8-12-8 10-21-38 25z"/><circle cx="52" cy="31" r="9"/><path d="m45 24-5-13 10 8 7-9 2 15z"/>',
    pterosaur: '<path d="M48 49 3 23l30 7 16 12 16-12 32-7-43 28 3 31-10-23z"/><path d="M48 38 34 16l17 8 13-7-8 22z"/><path d="m55 29 32-5-30 14z"/>',
    "aquatic-reptile": '<ellipse cx="58" cy="60" rx="30" ry="17"/><path d="M35 56 22 27Q18 14 31 10l8 6-8 8 14 28z"/><path d="M36 68 15 83l3 7 26-13zm43 0 16 15-4 7-21-13zM84 57l15-6-12 13z"/>',
    spider: '<ellipse cx="50" cy="55" rx="18" ry="23"/><circle cx="50" cy="31" r="12"/><path fill="none" stroke="currentColor" stroke-width="7" stroke-linecap="round" d="M37 44 17 29M35 53 10 48M35 62 12 72M40 70 24 89M63 44l20-15M65 53l25-5M65 62l23 10M60 70l16 19"/>',
    "winged-insect": '<ellipse cx="50" cy="56" rx="11" ry="27"/><circle cx="50" cy="25" r="9"/><ellipse cx="29" cy="49" rx="18" ry="29" transform="rotate(35 29 49)"/><ellipse cx="71" cy="49" rx="18" ry="29" transform="rotate(-35 71 49)"/><path d="M43 78h14l-7 16z"/>',
    centipede: '<path fill="none" stroke="currentColor" stroke-width="14" stroke-linecap="round" d="M12 63q18-42 38-12t38-10"/><path fill="none" stroke="currentColor" stroke-width="4" d="m20 50-12-9m18 4-8-14m18 12-1-16m12 17 6-15m6 21 13-12m-53 28-14 6m25 1-9 15m22-17-1 17m18-22 8 14m9-23 13 8"/>',
    insect: '<ellipse cx="50" cy="58" rx="15" ry="28"/><circle cx="50" cy="25" r="10"/><path fill="none" stroke="currentColor" stroke-width="6" d="m37 45-22-13m21 27-27 1m30 14-20 17m44-46 22-13M64 59l27 1M61 74l20 17"/>',
    plant: '<path d="M45 90V50Q28 45 19 28q21 2 31 15Q60 23 82 19 75 40 57 49v41z"/><path d="M43 65 22 55q3 18 22 21zm15-1 22-12q-3 19-22 23z"/>',
    frog: '<ellipse cx="50" cy="61" rx="28" ry="22"/><circle cx="35" cy="38" r="11"/><circle cx="65" cy="38" r="11"/><path d="M31 69 8 82l5 8 30-12zm38 0 23 13-5 8-30-12z"/>',
    primate: '<circle cx="50" cy="27" r="14"/><path d="M31 77q-5-31 19-36 25 5 19 36l-13-1-6-22-6 22z"/><path d="M36 48 14 70l7 6 22-18zm28 0 22 22-7 6-22-18z"/>',
    unknown: '<circle cx="50" cy="50" r="34" fill="none" stroke="currentColor" stroke-width="8"/><path d="M38 39q2-15 15-15 14 0 14 12 0 8-10 13-7 4-7 12" fill="none" stroke="currentColor" stroke-width="8" stroke-linecap="round"/><circle cx="50" cy="75" r="5"/>',
  };

  function markup(template) {
    const info = window.IRON_PIT_FIGURE_VISUALS?.profile(template) || { form: "unknown", detail: "unknown" };
    const shape = SHAPES[info.form] || SHAPES.unknown;
    const title = esc(template?.name);
    return `<svg class="portrait-svg" viewBox="0 0 100 100" role="img" aria-label="${title}"><title>${title}</title><g class="portrait-ink">${shape}</g></svg>`;
  }

  window.IRON_PIT_FIGURE_PORTRAITS = { markup };
})();