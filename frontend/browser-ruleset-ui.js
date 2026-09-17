(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  let bundlePromise = null;

  function ensureBundle(ruleset) {
    if (ruleset !== "2014") return Promise.resolve();
    if (window.IRON_PIT_2014_MVP_READY === true && window.IRON_PIT_BROWSER_MONSTERS_2014) return Promise.resolve();
    if (bundlePromise) return bundlePromise;
    bundlePromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "browser-monsters-2014.js";
      script.async = true;
      script.dataset.ironPitRuleset = "2014";
      script.onload = () => window.IRON_PIT_2014_MVP_READY === true
        ? resolve()
        : reject(new Error("2014 browser bundle loaded without its readiness marker."));
      script.onerror = () => reject(new Error("2014 browser bundle could not be loaded."));
      document.head.append(script);
    });
    return bundlePromise;
  }

  function summary(state) {
    if (!state.catalog) return "";
    if (state.ruleset === "2014") {
      return `${state.catalog.hero_ready_count}/${state.catalog.hero_count} certified 2014 hero levels · ${state.catalog.monster_ready_count}/${state.catalog.monster_count} certified 2014 monsters · test lane.`;
    }
    return `${state.catalog.hero_ready_count}/${state.catalog.hero_count} certified hero levels · ${state.catalog.monster_ready_count}/${state.catalog.monster_count} certified monsters.`;
  }

  function update(state) {
    const is2014 = state.ruleset === "2014", header = document.querySelector("header.hero");
    const eyebrow = header?.querySelector("p.eyebrow"), introStrong = header?.querySelector("p strong");
    const headerNotes = header?.querySelectorAll("p.rules-note") || [];
    if (eyebrow) eyebrow.textContent = is2014 ? "D&D 5e 2014 · SRD 5.1 TEST LANE" : "D&D 5e 2024 · SRD 5.2.1";
    if (introStrong?.parentElement) introStrong.parentElement.innerHTML = is2014
      ? "<strong>D&D 5e (2014) test combat lane.</strong> Pick a certified 2014 pregen and certified 2014 monsters, then run them through the shared Iron Pit engine."
      : "<strong>D&D 5e (2024) compatible combat simulation system.</strong> Load the cards, roll initiative, and watch a rules-driven fight play out.";
    if (headerNotes[0]) headerNotes[0].textContent = is2014
      ? "2014 is isolated from 2024. Only currently certified 2014 pregens and monsters are selectable."
      : "2024 production lane. Only explicitly certified hero levels and monsters can enter automated combat.";
    const auditNote = document.querySelector(".log-panel .rules-note");
    if (auditNote) auditNote.textContent = is2014 ? "D&D 2014 / SRD 5.1 test lane · expandable rules audit" : "D&D 2024 / SRD 5.2.1 · expandable rules audit";
    const left = document.querySelector(".hero-field .field-heading span"), right = document.querySelector(".monster-field .field-heading span");
    if (left) left.textContent = "HERO CARDS";
    if (right) right.textContent = "MONSTER CARDS";
    el("ruleset-summary").textContent = summary(state);
    el("ruleset-control").dataset.ruleset = state.ruleset;
    el("ruleset-select").value = state.ruleset;
    document.title = is2014 ? "The Iron Pit — D&D 5e 2014 Test Lane" : "The Iron Pit — D&D 5e 2024 Combat Simulator";
  }

  function syncDisabled(state) {
    const active = Boolean(state.session && !state.session.complete);
    el("ruleset-select").disabled = state.fighting || active;
  }

  function install(state, onChange) {
    const control = el("ruleset-control"), select = el("ruleset-select"), note = el("ruleset-summary");
    if (!control || !select || !note) throw new Error("Static ruleset control is missing from the Iron Pit page.");
    control.dataset.ruleset = state.ruleset;
    select.value = state.ruleset;
    select.addEventListener("change", () => onChange(select.value));
  }

  window.IRON_PIT_RULESET_UI = { ensureBundle, install, syncDisabled, update };
})();
