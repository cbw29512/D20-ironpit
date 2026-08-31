(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;
  const ready = (item) => item.coverage_status === "raw_ready" && item.runnable_template_id;

  function option(value, text, selected = false, disabled = false) {
    const node = document.createElement("option");
    node.value = String(value); node.textContent = text; node.selected = selected; node.disabled = disabled;
    return node;
  }

  function labeledSelect(labelText, className = "") {
    const label = document.createElement("label");
    label.className = `picker-field ${className}`.trim();
    const caption = document.createElement("span"), select = document.createElement("select");
    caption.textContent = labelText; label.append(caption, select);
    return { label, select };
  }

  function renderParty(state, onPartySize, onHeroChange) {
    const size = el("party-size");
    size.value = String(state.heroSlots.length);
    size.onchange = () => onPartySize(Number(size.value));
    const root = el("hero-slot-pickers"); root.replaceChildren();
    const heroes = P().classOptions(state.catalog.heroes);
    state.heroSlots.forEach((slot, index) => {
      const row = document.createElement("div"); row.className = "hero-slot-picker";
      const heading = document.createElement("strong"); heading.textContent = `Character ${index + 1}`;
      const heroField = labeledSelect("Hero");
      heroes.forEach((item) => heroField.select.append(option(item.id, item.name, item.id === slot.class_id)));
      heroField.select.onchange = () => onHeroChange(index, { class_id: heroField.select.value });
      const levelField = labeledSelect("Level");
      P().LEVELS.forEach((level) => levelField.select.append(option(level, level, level === Number(slot.level))));
      levelField.select.onchange = () => onHeroChange(index, { level: Number(levelField.select.value) });
      const chosen = P().cardForSlot(state.catalog.heroes, slot);
      const status = document.createElement("small"), isReady = ready(chosen || {});
      status.className = `slot-status ${isReady ? "ready" : "blocked"}`;
      status.textContent = isReady
        ? `${chosen.name} · ${chosen.class_name} ${chosen.level} · RAW ready`
        : `${chosen?.name || "Hero"} level ${slot.level} is not RAW-certified yet.`;
      row.append(heading, heroField.label, levelField.label, status); root.append(row);
    });
  }

  function renderMonsterFilters(state, onCrChange, onMonsterChange) {
    const runnable = state.catalog.monsters.filter(ready);
    const cr = el("monster-cr-filter"); cr.replaceChildren(option("all", "All certified CRs", state.monsterCr === "all"));
    P().challengeRatings(runnable).forEach((value) => cr.append(option(value, `CR ${value}`, value === state.monsterCr)));
    cr.onchange = () => onCrChange(cr.value);
    const picker = el("monster-picker"); picker.replaceChildren();
    const monsters = P().sortedMonsters(runnable, state.monsterCr);
    const ids = monsters.map((monster) => monster.id);
    monsters.forEach((monster) => picker.append(option(
      monster.id, `CR ${monster.challenge_rating} · ${monster.name}`, monster.id === state.monsterChoice,
    )));
    const selected = ids.includes(state.monsterChoice) ? state.monsterChoice : ids[0] || null;
    if (selected) picker.value = selected;
    else picker.append(option("", "No certified monsters at this CR", true, true));
    picker.onchange = () => onMonsterChange(picker.value);
    el("add-monster").disabled = state.monsters.length >= 6 || selected === null;
    el("monster-picker-note").textContent = `${runnable.length} RAW-certified monster cards available.`;
    return selected;
  }

  window.createEncounterPickerView = () => ({ renderMonsterFilters, renderParty });
})();
