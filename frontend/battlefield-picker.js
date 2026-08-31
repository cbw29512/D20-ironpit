(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;
  const ready = (item) => Boolean(item?.coverage_status === "raw_ready" && item?.runnable_template_id);
  let active = null;

  function option(value, text, selected = false, disabled = false) {
    const node = document.createElement("option");
    node.value = String(value); node.textContent = text; node.selected = selected; node.disabled = disabled;
    return node;
  }

  function chosenHero(state) {
    const candidates = P().heroBuilds(state.catalog.heroes, el("picker-class").value, Number(el("picker-level").value));
    return P().preferredHero(candidates);
  }

  function populateHero(state, existing) {
    const heroSelect = el("picker-class"), levelSelect = el("picker-level");
    heroSelect.replaceChildren(); levelSelect.replaceChildren();
    const fallback = existing || state.catalog.heroes.find(ready) || state.catalog.heroes[0];
    P().classOptions(state.catalog.heroes).forEach((item) => heroSelect.append(option(item.id, item.name, item.id === fallback.class_id)));
    P().LEVELS.forEach((level) => levelSelect.append(option(level, level, level === Number(fallback.level))));

    function refresh() {
      const chosen = chosenHero(state);
      el("picker-note").textContent = ready(chosen)
        ? `${chosen.name} · ${chosen.class_name} ${chosen.level} is RAW-certified for automated combat.`
        : `${chosen?.name || "This hero"} level ${levelSelect.value} is not RAW-certified yet.`;
      el("confirm-card").disabled = !ready(chosen);
      el("confirm-card").textContent = ready(chosen) ? "Add to Slot" : "Certification Pending";
    }
    heroSelect.value = fallback.class_id; levelSelect.value = String(fallback.level);
    heroSelect.onchange = refresh; levelSelect.onchange = refresh; refresh();
  }

  function monsterNote(rows, chosen) {
    const certified = rows.filter(ready).length;
    if (!rows.length) return "No SRD monsters exist at this Challenge Rating.";
    if (chosen && !ready(chosen)) return `${chosen.name} is in the SRD catalog, but its outcome-changing combat mechanics are still being RAW-certified.`;
    return `${rows.length} SRD monster${rows.length === 1 ? "" : "s"} shown · ${certified} RAW-ready for automated combat.`;
  }

  function populateMonster(state, existing) {
    const all = state.catalog.monsters, crSelect = el("picker-cr"), monsterSelect = el("picker-monster");
    crSelect.replaceChildren(option("all", `All CRs · ${all.length} monsters`, true));
    P().challengeRatings(all).forEach((cr) => crSelect.append(option(cr, `CR ${cr}`)));

    function refreshNote(rows) {
      const chosen = rows.find((monster) => monster.id === monsterSelect.value) || null;
      el("picker-note").textContent = monsterNote(rows, chosen);
      el("confirm-card").disabled = !ready(chosen);
      el("confirm-card").textContent = ready(chosen) ? "Add to Slot" : "Certification Pending";
    }
    function refreshMonsters() {
      const rows = P().sortedMonsters(all, crSelect.value); monsterSelect.replaceChildren();
      rows.forEach((monster) => monsterSelect.append(option(
        monster.id, `CR ${monster.challenge_rating} · ${monster.name}${ready(monster) ? " · RAW READY" : " · certification pending"}`,
        monster.id === existing?.id,
      )));
      const existingShown = existing && rows.some((monster) => monster.id === existing.id), firstReady = rows.find(ready);
      if (existingShown) monsterSelect.value = existing.id;
      else if (firstReady) monsterSelect.value = firstReady.id;
      else if (rows[0]) monsterSelect.value = rows[0].id;
      refreshNote(rows);
    }
    if (existing) crSelect.value = String(existing.challenge_rating);
    crSelect.onchange = refreshMonsters;
    monsterSelect.onchange = () => refreshNote(P().sortedMonsters(all, crSelect.value));
    refreshMonsters();
  }

  function selectedCard(state) {
    if (!active) return null;
    if (active.side === "heroes") return chosenHero(state);
    return state.catalog.monsters.find((monster) => monster.id === el("picker-monster").value) || null;
  }

  function open(state, side, index, onConfirm, onRemove) {
    active = { side, index, onConfirm, onRemove };
    const existing = (side === "heroes" ? state.heroSlots : state.monsterSlots)[index];
    el("picker-kicker").textContent = `${side === "heroes" ? "HERO" : "MONSTER"} SLOT ${index + 1}`;
    el("picker-title").textContent = existing ? `Change ${existing.name}` : side === "heroes" ? "Choose a hero" : "Choose a monster";
    el("hero-picker-fields").hidden = side !== "heroes"; el("monster-picker-fields").hidden = side !== "monsters";
    el("remove-card").hidden = !existing; el("confirm-card").textContent = "Add to Slot";
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
