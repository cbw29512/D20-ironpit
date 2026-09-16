(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  let bundlePromise = null;

  function loadScript(src, marker) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.async = true;
      script.dataset.ironPitRuleset = "2014";
      script.onload = () => window[marker] === true
        ? resolve()
        : reject(new Error(`${src} loaded without its readiness marker.`));
      script.onerror = () => reject(new Error(`${src} could not be loaded.`));
      document.head.append(script);
    });
  }

  function ensureBundle(ruleset) {
    if (ruleset !== "2014") return Promise.resolve();
    const heroesReady = window.IRON_PIT_2014_HEROES_READY === true && window.IRON_PIT_BROWSER_HEROES_2014;
    const monstersReady = window.IRON_PIT_2014_MVP_READY === true && window.IRON_PIT_BROWSER_MONSTERS_2014;
    if (heroesReady && monstersReady) return Promise.resolve();
    if (bundlePromise) return bundlePromise;
    bundlePromise = Promise.all([
      heroesReady ? Promise.resolve() : loadScript("browser-heroes-2014.js", "IRON_PIT_2014_HEROES_READY"),
      monstersReady ? Promise.resolve() : loadScript("browser-monsters-2014.js", "IRON_PIT_2014_MVP_READY"),
    ]).then(() => undefined);
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
      ? "<strong>D&D 5e (2014) test combat lane.</strong> Pick a certified 2014 pregen for Team A and certified 2014 monsters for Team B."
      : "<strong>D&D 5e (2024) compatible combat simulation system.</strong> Load the cards, roll initiative, and watch a rules-driven fight play out.";
    if (headerNotes[0]) headerNotes[0].textContent = is2014
      ? "2014 is isolated from 2024. Only separately certified 2014 heroes and monsters enter this lane."
      : "2024 production lane. Only explicitly certified hero levels and monsters can enter automated combat.";
    const auditNote = document.querySelector(".log-panel .rules-note");
    if (auditNote) auditNote.textContent = is2014 ? "D&D 2014 / SRD 5.1 test lane · expandable rules audit" : "D&D 2024 / SRD 5.2.1 · expandable rules audit";
    const left = document.querySelector(".hero-field .field-heading span"), right = document.querySelector(".monster-field .field-heading span");
    if (left) left.textContent = is2014 ? "2014 PREGENS" : "HERO CARDS";
    if (right) right.textContent = is2014 ? "2014 MONSTERS" : "MONSTER CARDS";
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