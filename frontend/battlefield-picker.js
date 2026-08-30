(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;
  const ready = (item) => Boolean(["raw_ready", "raw_playable"].includes(item?.coverage_status) && item?.runnable_template_id);
  const full = (item) => item?.coverage_status === "raw_ready";
  let active = null;

  function option(value, text, selected = false, disabled = false) {
    const node = document.createElement("option"); node.value = String(value); node.textContent = text;
    node.selected = selected; node.disabled = disabled; return node;
  }

  function populateHero(state, existing) {
    const classSelect = el("picker-class"), levelSelect = el("picker-level"), heroSelect = el("picker-hero");
    classSelect.replaceChildren(); levelSelect.replaceChildren(); heroSelect.replaceChildren();
    const fallback = existing || state.catalog.heroes.find(ready) || state.catalog.heroes[0];
    P().classOptions(state.catalog.heroes).forEach((item) => classSelect.append(option(item.id, item.name, item.id === fallback.class_id)));
    P().LEVELS.forEach((level) => levelSelect.append(option(level, level, level === Number(fallback.level))));

    function refreshBuilds() {
      const builds = P().heroBuilds(state.catalog.heroes, classSelect.value, Number(levelSelect.value));
      heroSelect.replaceChildren();
      builds.forEach((hero) => heroSelect.append(option(
        hero.id,
        full(hero) ? `${hero.name} · FULL RAW` : ready(hero) ? `${hero.name} · RAW core` : `${hero.build_name} · unavailable`,
        hero.id === existing?.id,
        !ready(hero),
      )));
      const chosen = builds.find((hero) => hero.id === heroSelect.value) || builds.find(ready) || builds[0] || null;
      if (chosen && ready(chosen)) heroSelect.value = chosen.id;
      el("picker-note").textContent = full(chosen)
        ? "Full automated feature coverage certified."
        : ready(chosen) ? "Playable now with RAW core combat; advanced class/subclass actions continue to be certified without blocking the card."
          : "This pregen has no runnable combat template.";
      el("confirm-card").disabled = !ready(chosen);
    }
    classSelect.value = fallback.class_id; levelSelect.value = String(fallback.level);
    classSelect.onchange = refreshBuilds; levelSelect.onchange = refreshBuilds;
    heroSelect.onchange = refreshBuilds; refreshBuilds();
  }

  function populateMonster(state, existing) {
    const all = state.catalog.monsters.filter(ready);
    const crSelect = el("picker-cr"), monsterSelect = el("picker-monster");
    crSelect.replaceChildren(option("all", "All CRs", true));
    P().challengeRatings(all).forEach((cr) => crSelect.append(option(cr, `CR ${cr}`)));

    function refreshMonsters() {
      const rows = P().sortedMonsters(all, crSelect.value);
      monsterSelect.replaceChildren();
      rows.forEach((monster) => monsterSelect.append(option(monster.id, `CR ${monster.challenge_rating} · ${monster.name}`, monster.id === existing?.id)));
      if (existing && rows.some((monster) => monster.id === existing.id)) monsterSelect.value = existing.id;
      el("picker-note").textContent = `${rows.length} RAW-certified monster card${rows.length === 1 ? "" : "s"} available.`;
      el("confirm-card").disabled = rows.length === 0;
    }
    if (existing) crSelect.value = String(existing.challenge_rating);
    crSelect.onchange = refreshMonsters; refreshMonsters();
  }

  function selectedCard(state) {
    if (!active) return null;
    if (active.side === "heroes") return state.catalog.heroes.find((hero) => hero.id === el("picker-hero").value) || null;
    return state.catalog.monsters.find((monster) => monster.id === el("picker-monster").value) || null;
  }

  function open(state, side, index, onConfirm, onRemove) {
    active = { side, index, onConfirm, onRemove };
    const existing = (side === "heroes" ? state.heroSlots : state.monsterSlots)[index];
    el("picker-kicker").textContent = `${side === "heroes" ? "HERO" : "MONSTER"} SLOT ${index + 1}`;
    el("picker-title").textContent = existing ? `Change ${existing.name}` : side === "heroes" ? "Choose a pregen" : "Choose a monster";
    el("hero-picker-fields").hidden = side !== "heroes"; el("monster-picker-fields").hidden = side !== "monsters";
    el("remove-card").hidden = !existing;
    if (side === "heroes") populateHero(state, existing); else populateMonster(state, existing);
    el("card-picker").showModal();
  }

  function bind(stateProvider) {
    el("confirm-card").addEventListener("click", () => {
      const state = stateProvider(), card = selectedCard(state); if (!active || !ready(card)) return;
      active.onConfirm(active.side, active.index, card); el("card-picker").close(); active = null;
    });
    el("remove-card").addEventListener("click", () => {
      if (!active) return; active.onRemove(active.side, active.index); el("card-picker").close(); active = null;
    });
    el("card-picker").addEventListener("close", () => { active = null; });
  }

  window.IRON_PIT_BATTLEFIELD_PICKER = { bind, open };
})();
