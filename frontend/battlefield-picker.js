(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const P = () => window.IRON_PIT_ENCOUNTER_PICKER;
  const ready = (item) => Boolean(item?.runnable_template_id && (item?.coverage_status === "raw_ready" || (active?.side === "monsters" && item?.custom && item?.kind === "monster" && item.coverage_status === "custom_ready" && item.compiled_template)));
  let active = null;
  const customCards = (kind, ruleset) => (window.IRON_PIT_CUSTOM_LIBRARY?.list(kind, ruleset) || []).map(item => kind === "monster" ? window.IRON_PIT_CUSTOM_MONSTER_RUNTIME?.decorate(item) || item : item);
  const customPreview = (card) => {
    const frame = el("picker-portrait");
    if (frame && card?.custom) {
      frame.classList.add("custom-card-preview");
      frame.setAttribute("data-custom-card", "true");
      frame.style.outline = "3px solid #cf9dff";
      frame.style.outlineOffset = "3px";
    } else if (frame) {
      frame.classList.remove("custom-card-preview");
      frame.removeAttribute("data-custom-card");
      frame.style.outline = "";
      frame.style.outlineOffset = "";
    }
  };


  function option(value, text, selected = false, disabled = false) {
    const node = document.createElement("option");
    node.value = String(value); node.textContent = text; node.selected = selected; node.disabled = disabled;
    return node;
  }

  function chosenHero(state) {
    if (el("picker-class").value === "custom") return customCards("character", state.ruleset).find(item => item.id === el("picker-level").value) || null;
    const candidates = P().heroBuilds(state.catalog.heroes, el("picker-class").value, Number(el("picker-level").value));
    return P().preferredHero(candidates);
  }

  function runtimeTemplate(card, side) {
    if (card?.compiled_template) return card.compiled_template;
    if (!card?.runnable_template_id) return { id: card?.id, name: card?.name, kind: card?.kind, class_id: card?.class_id, ruleset: card?.ruleset };
    if (card.kind === "character") return window.IRON_PIT_BROWSER_HEROES?.[card.runnable_template_id] || card;
    return (card.ruleset === "2014"
      ? window.IRON_PIT_BROWSER_MONSTERS_2014?.[card.runnable_template_id]
      : window.IRON_PIT_BROWSER_MONSTERS?.[card.runnable_template_id]) || card;
  }

  function renderPreview(card, side) {
    const frame = el("picker-portrait");
    if (!frame) return;
    if (!card) { frame.hidden = true; frame.replaceChildren(); return; }
    const template = runtimeTemplate(card, side);
    const artwork = window.IRON_PIT_COMBATANT_ART?.markup(template) || "";
    const fallback = window.IRON_PIT_FIGURE_PORTRAITS?.markup(template) || "";
    frame.hidden = false;
    const kind = card.kind === "character" ? "hero-art" : "monster-art";
    const hasArt = artwork ? " has-art" : "";
    frame.className = `picker-portrait-frame fighter-portrait ${side} ${kind}${hasArt}`;
    frame.innerHTML = `${artwork}${fallback}`;
    window.IRON_PIT_FIGURE_VISUALS?.decorate(frame, template);
    customPreview(card);
  }

  function populateHero(state, existing) {
    const heroSelect = el("picker-class"), levelSelect = el("picker-level");
    heroSelect.replaceChildren(); levelSelect.replaceChildren();
    const fallback = existing || state.catalog.heroes.find(ready) || state.catalog.heroes[0];
    P().classOptions(state.catalog.heroes).forEach((item) => heroSelect.append(option(item.id, item.name, item.id === fallback.class_id)));
    if (customCards("character", state.ruleset).length) heroSelect.append(option("custom", "✦ Custom Pregens", Boolean(existing?.custom)));
    P().LEVELS.forEach((level) => levelSelect.append(option(level, level, level === Number(fallback.level))));

    function refresh() {
      const chosen = chosenHero(state);
      el("picker-note").textContent = chosen?.custom ? `✦ CUSTOM PREGEN · ${chosen.name} · saved draft. Combat certification required before use.` : ready(chosen)
        ? `${chosen.name} · ${chosen.class_name} ${chosen.level} is ready to fight.`
        : `${chosen?.name || "This hero"} level ${levelSelect.value} is not available yet.`;
      el("confirm-card").disabled = !ready(chosen);
      el("confirm-card").textContent = ready(chosen) ? "Add to slot" : "Not available";
      renderPreview(chosen, "heroes");
    }
    heroSelect.value = fallback.class_id; levelSelect.value = String(fallback.level);
    const refreshLevels = () => {
      levelSelect.replaceChildren();
      if (heroSelect.value === "custom") {
        customCards("character", state.ruleset).forEach(card => levelSelect.append(option(card.id, card.name + " · Lv " + card.level + " · draft")));
      } else {
        P().LEVELS.forEach(level => levelSelect.append(option(level, level)));
        levelSelect.value = String(existing?.level || fallback.level || 1);
      }
      refresh();
    };
    heroSelect.onchange = refreshLevels; levelSelect.onchange = refresh;
    if (existing?.custom) heroSelect.value = "custom";
    refreshLevels();
  }

  function monsterNote(state, rows, chosen) {
    const certified = rows.filter(ready).length;
    if (!rows.length) return "No monsters exist at this Challenge Rating.";
    if (chosen?.custom) return ready(chosen) ? `✦ CUSTOM MONSTER · ${chosen.name} · ready for homebrew battle (not official RAW-certified).` : `✦ CUSTOM MONSTER · ${chosen.name} · ${chosen.compile_error || "draft not ready for combat"}`;
    if (chosen && !ready(chosen)) return `${chosen.name} is listed, but is not ready to fight yet.`;
    if (state.ruleset === "2014") return `${rows.length} 2014 monster${rows.length === 1 ? "" : "s"} at this Challenge Rating.`;
    return `${rows.length} monster${rows.length === 1 ? "" : "s"} shown · ${certified} ready to fight.`;
  }

  function populateMonster(state, existing, side = "monsters") {
    const all = [...state.catalog.monsters, ...customCards("monster", state.ruleset)], crSelect = el("picker-cr"), monsterSelect = el("picker-monster");
    crSelect.replaceChildren(option("all", `All CRs · ${all.length} monsters`, true));
    P().challengeRatings(state.catalog.monsters).forEach((cr) => crSelect.append(option(cr, `CR ${cr}`)));
    if (all.some(item => item.custom)) crSelect.append(option("custom", "✦ Custom Monsters"));

    function refreshNote(rows) {
      const chosen = rows.find((monster) => monster.id === monsterSelect.value) || null;
      el("picker-note").textContent = monsterNote(state, rows, chosen);
      el("confirm-card").disabled = !ready(chosen);
      el("confirm-card").textContent = ready(chosen) ? "Add to slot" : "Not available";
      renderPreview(chosen, "monsters");
    }
    function refreshMonsters() {
      const rows = crSelect.value === "custom" ? all.filter(item => item.custom) : P().sortedMonsters(all.filter(item => !item.custom), crSelect.value); monsterSelect.replaceChildren();
      rows.forEach((monster) => monsterSelect.append(option(
        monster.id, monster.custom ? `✦ CUSTOM · ${monster.name} · ${ready(monster) ? "playable homebrew" : "draft (not ready)"}` : `CR ${monster.challenge_rating} · ${monster.name}${ready(monster) ? "" : " · not available"}`,
        monster.id === existing?.id,
      )));
      const existingShown = existing && rows.some((monster) => monster.id === existing.id), firstReady = rows.find(ready);
      if (existingShown) monsterSelect.value = existing.id;
      else if (firstReady) monsterSelect.value = firstReady.id;
      else if (rows[0]) monsterSelect.value = rows[0].id;
      refreshNote(rows);
    }
    if (existing) crSelect.value = existing.custom ? "custom" : String(existing.challenge_rating);
    crSelect.onchange = refreshMonsters;
    monsterSelect.onchange = () => refreshNote(crSelect.value === "custom" ? all.filter(item => item.custom) : P().sortedMonsters(all.filter(item => !item.custom), crSelect.value));
    refreshMonsters();
  }

  function selectedCard(state) {
    if (!active) return null;
    if (el("picker-kind").value === "pregen") return chosenHero(state);
    return [...state.catalog.monsters, ...customCards("monster", state.ruleset)].find((monster) => monster.id === el("picker-monster").value) || null;
  }

  function open(state, side, index, onConfirm, onRemove) {
    active = { side, index, onConfirm, onRemove };
    const existing = (side === "heroes" ? state.heroSlots : state.monsterSlots)[index];
    const sideLabel = side === "heroes" ? "TEAM A" : "TEAM B";
    el("picker-kicker").textContent = `${sideLabel} SLOT ${index + 1}`;
    el("picker-title").textContent = existing ? `Change ${existing.name}` : "Choose a combatant";
    el("remove-card").hidden = !existing; el("confirm-card").textContent = "Add to slot";
    el("picker-kind").value = existing ? (existing.kind === "monster" ? "monster" : "pregen") : (side === "heroes" ? "pregen" : "monster");
    const refreshKind = () => {
      const monsterMode = el("picker-kind").value === "monster";
      el("hero-picker-fields").hidden = monsterMode;
      el("monster-picker-fields").hidden = !monsterMode;
      if (monsterMode) populateMonster(state, existing?.kind === "monster" ? existing : null, side);
      else populateHero(state, existing?.kind === "character" ? existing : null);
    };
    el("picker-kind").onchange = refreshKind; refreshKind();
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
    el("card-picker").addEventListener("close", () => { active = null; renderPreview(null); });
  }

  window.IRON_PIT_BATTLEFIELD_PICKER = { bind, open };
})();
