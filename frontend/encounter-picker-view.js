(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;

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
    const classes = P().classOptions(state.catalog.heroes);
    state.heroSlots.forEach((slot, index) => {
      const row = document.createElement("div"); row.className = "hero-slot-picker";
      const heading = document.createElement("strong"); heading.textContent = `Character ${index + 1}`;
      const classField = labeledSelect("Class");
      classes.forEach((item) => classField.select.append(option(item.id, item.name, item.id === slot.class_id)));
      classField.select.onchange = () => onHeroChange(index, { class_id: classField.select.value });
      const levelField = labeledSelect("Level");
      P().LEVELS.forEach((level) => levelField.select.append(option(level, level, level === Number(slot.level))));
      levelField.select.onchange = () => onHeroChange(index, { level: Number(levelField.select.value) });
      const buildField = labeledSelect("Build / Card", "build-field");
      const builds = P().heroBuilds(state.catalog.heroes, slot.class_id, slot.level);
      builds.forEach((hero) => {
        const ready = hero.coverage_status === "raw_ready" && hero.runnable_template_id;
        buildField.select.append(option(hero.id, `${hero.build_name}${ready ? " · RAW ready" : " · not certified yet"}`, hero.id === slot.card_id));
      });
      buildField.select.onchange = () => onHeroChange(index, { card_id: buildField.select.value });
      const chosen = P().cardForSlot(state.catalog.heroes, slot);
      const status = document.createElement("small");
      const ready = chosen?.coverage_status === "raw_ready" && chosen?.runnable_template_id;
      status.className = `slot-status ${ready ? "ready" : "blocked"}`;
      status.textContent = ready ? `RAW ready · ${chosen.name}` : "This class/level build is not RAW-certified yet.";
      row.append(heading, classField.label, levelField.label, buildField.label, status); root.append(row);
    });
  }

  function renderMonsterFilters(state, onCrChange, onMonsterChange) {
    const cr = el("monster-cr-filter"); cr.replaceChildren(option("all", "All CRs", state.monsterCr === "all"));
    P().challengeRatings(state.catalog.monsters).forEach((value) => cr.append(option(value, `CR ${value}`, value === state.monsterCr)));
    cr.onchange = () => onCrChange(cr.value);
    const picker = el("monster-picker"); picker.replaceChildren();
    const monsters = P().sortedMonsters(state.catalog.monsters, state.monsterCr);
    const readyIds = [];
    monsters.forEach((monster) => {
      const ready = monster.coverage_status === "raw_ready" && monster.runnable_template_id;
      if (ready) readyIds.push(monster.id);
      picker.append(option(monster.id, `CR ${monster.challenge_rating} · ${monster.name}${ready ? "" : " · not ready"}`, false, !ready));
    });
    const selected = readyIds.includes(state.monsterChoice) ? state.monsterChoice : readyIds[0] || null;
    if (selected) picker.value = selected;
    else picker.append(option("", "No RAW-certified monsters at this CR", true, true));
    picker.onchange = () => onMonsterChange(picker.value);
    el("add-monster").disabled = state.monsters.length >= 8 || selected === null;
    return selected;
  }

  window.createEncounterPickerView = () => ({ renderMonsterFilters, renderParty });
})();
