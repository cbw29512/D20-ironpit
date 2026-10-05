(() => {
  "use strict";

  const el = (id) => document.getElementById(id);
  const V = () => window.IRON_PIT_FIGURE_VISUALS;
  const P = () => window.IRON_PIT_FIGURE_PORTRAITS;
  const A = () => window.IRON_PIT_COMBATANT_ART;
  const L = () => window.IRON_PIT_BATTLE_LOG;
  const MAX_SLOTS = 6;

  function runtimeTemplate(card, side) {
    if (!card?.runnable_template_id) return null;
    if (card.ruleset === "2014") {
      return side === "heroes"
        ? window.IRON_PIT_BROWSER_HEROES?.[card.runnable_template_id] || null
        : window.IRON_PIT_BROWSER_MONSTERS_2014?.[card.runnable_template_id] || null;
    }
    return side === "heroes" ? window.IRON_PIT_BROWSER_HEROES[card.runnable_template_id]
      : window.IRON_PIT_BROWSER_MONSTERS[card.runnable_template_id];
  }

  function figureMarkup(template) {
    try {
      const fallback = P()?.markup(template)
        || '<svg class="portrait-svg" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="32"/></svg>';
      const artwork = A()?.markup(template) || "";
      const hasArt = artwork ? " has-art" : "";
      const kind = template?.kind === "character" ? " hero-art" : " monster-art";
      return `<div class="stick-figure fighter-portrait${hasArt}${kind}" aria-hidden="true">${artwork}${fallback}</div>`;
    } catch (error) {
      console.error("Failed to render battlefield combatant visual", { templateId: template?.id, error });
      throw error;
    }
  }

  function emptySlot(side, index, onOpen, _ruleset) {
    const node = document.createElement("button");
    const addLabel = side === "monsters" ? "Add monster" : "Add hero";
    node.type = "button"; node.className = `battle-card empty-slot ${side}`; node.dataset.slotIndex = String(index);
    node.innerHTML = `<span class="slot-number">${index + 1}</span><b aria-hidden="true">＋</b><strong>${addLabel}</strong><small>Click to choose</small>`;
    node.addEventListener("click", () => onOpen(side, index)); return node;
  }

  function occupiedSlot(side, index, card, onOpen, onRemove, locked) {
    const template = runtimeTemplate(card, side), node = document.createElement("article");
    const monsterCard = card.kind === "monster";
    const kind = side === "monsters" ? "monster" : "hero";
    node.className = `battle-card occupied ${side}`; node.dataset.slotIndex = String(index);
    node.tabIndex = 0;
    node.setAttribute("aria-label", `${card.name}, ${kind} slot ${index + 1}`);
    node.innerHTML = `<button type="button" class="card-trash"${locked ? " disabled" : ""} aria-label="Remove ${card.name}"><svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M9 3h6l1 2h5v2H3V5h5l1-2zm1 6h2v10h-2V9zm4 0h2v10h-2V9zM6 7h12v12a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2V7z"/></svg></button><span class="slot-number">${index + 1}</span><span class="initiative-badge" aria-label="Initiative">—</span>${figureMarkup(template)}<strong class="card-name"></strong><small class="card-meta"></small><div class="card-status-lanes"><div class="card-status-lane card-status-buffs" aria-label="Buffs"><small>BUFFS</small><div class="card-concentration" hidden></div><div class="card-buffs"></div></div><div class="card-status-lane card-status-debuffs" aria-label="Debuffs"><small>DEBUFFS</small><div class="card-debuffs"></div></div></div><div class="card-hp"><span></span></div><small class="hp-text"></small><span class="death-stamp">✕ DEAD</span>`;
    node.querySelector(".card-name").textContent = card.name;
    node.querySelector(".card-meta").textContent = monsterCard ? `${card.monster_type} · CR ${card.challenge_rating}` : `${card.class_name} · Level ${card.level}`;
    const hp = Number(template?.max_hp || card.hit_points || 0);
    node.dataset.maxHp = String(hp); node.dataset.currentHp = String(hp); node.querySelector(".hp-text").textContent = `${hp} / ${hp} HP`;
    node.querySelector(".card-hp span").style.width = "100%"; if (template) V()?.decorate(node, template);
    node.querySelector(".card-trash").addEventListener("click", (event) => {
      event.preventDefault(); event.stopPropagation();
      if (locked) return;
      onRemove(side, index);
    });
    node.addEventListener("click", (event) => {
      if (event.target.closest(".card-trash")) return;
      onOpen(side, index);
    });
    return node;
  }

  function renderSide(side, slots, onOpen, onRemove, locked, ruleset) {
    const root = el(side === "heroes" ? "hero-slots" : "monster-slots"), nodes = [];
    for (let index = 0; index < MAX_SLOTS; index += 1) {
      nodes.push(slots[index]
        ? occupiedSlot(side, index, slots[index], onOpen, onRemove, locked)
        : emptySlot(side, index, onOpen, ruleset));
    }
    root.replaceChildren(...nodes);
  }

  function render(state, onOpen, onRemove) {
    const locked = Boolean(state.fighting || (state.session && !state.session.complete));
    renderSide("heroes", state.heroSlots, onOpen, onRemove, locked, state.ruleset);
    renderSide("monsters", state.monsterSlots, onOpen, onRemove, locked, state.ruleset);
    const heroes = state.heroSlots.filter(Boolean).length, monsters = state.monsterSlots.filter(Boolean).length;
    el("hero-summary").textContent = `${heroes} / 6`; el("monster-summary").textContent = `${monsters} / 6`;
    const disabled = heroes === 0 || monsters === 0 || state.fighting;
    for (const id of ["fight-button", "step-fight-button", "turbo-button"]) el(id).disabled = disabled;
  }

  function showResult(battle) {
    const combatants = [...battle.setup.heroes, ...battle.setup.monsters];
    const names = new Map(combatants.map((c) => [c.combatant_id, c.state.template.name]));
    const winner = battle.outcome === "heroes_win" ? "HEROES WIN" : battle.outcome === "monsters_win" ? "MONSTERS WIN" : "DRAW";
    el("result-title").textContent = winner; el("round-count").textContent = `${battle.rounds} round${battle.rounds === 1 ? "" : "s"}`;
    const initiative = el("initiative-list"); initiative.replaceChildren();
    battle.initiative.turn_order.forEach((id) => { const li = document.createElement("li"); li.textContent = names.get(id) || id; initiative.append(li); });
    const survivors = el("survivors"); survivors.replaceChildren();
    combatants.forEach((member) => {
      const row = document.createElement("div"), s = member.state;
      const status = s.is_dead || !s.is_alive ? "DEAD" : s.current_hp > 0 ? "ALIVE" : s.is_stable ? "STABLE" : "UNCONSCIOUS";
      row.className = `survivor ${status === "ALIVE" ? "alive" : "down"}`;
      row.textContent = `${s.template.name} — ${status} · ${s.current_hp}/${s.template.max_hp} HP`; survivors.append(row);
    });
    el("result-panel").hidden = false; el("status").textContent = winner;
  }

  function auditDetails(event) {
    const steps = event.audit?.steps || [];
    if (!steps.length) return null;
    const details = document.createElement("details"), heading = document.createElement("summary"), body = document.createElement("div");
    details.className = "rules-audit"; heading.textContent = `Details · ${steps.length} step${steps.length === 1 ? "" : "s"}`; body.className = "rules-audit-steps";
    steps.forEach((item, index) => {
      const text = String(item.label || item.detail || item.outcome || "").trim();
      if (!text || text === "Applied.") return;
      const row = document.createElement("div"); row.className = "rules-audit-step";
      row.innerHTML = `<span>${index + 1}</span><b></b><p></p>`;
      row.querySelector("b").textContent = item.kind || item.phase || item.rule || item.step || "Evidence";
      row.querySelector("p").textContent = text;
      body.append(row);
    });
    details.append(heading, body); return details;
  }

  function eventRow(event) {
    const row = document.createElement("article"), title = document.createElement("strong"), detail = document.createElement("p");
    row.className = "battle-event"; title.textContent = `Round ${event.round_number} · ${event.event_type || "Combat event"}`;
    detail.textContent = L().format(event); row.append(title, detail);
    const audit = auditDetails(event); if (audit) row.append(audit); return row;
  }

  function appendEvents(events) {
    const log = el("battle-log");
    for (const event of events) log.append(eventRow(event));
    log.scrollTop = log.scrollHeight;
  }

  function writeLog(battle) {
    try {
      // Replace the visible projection; Step supplies a prefix, Watch the full stream.
      el("battle-log").replaceChildren();
      appendEvents(battle.events || []);
      window.IRON_PIT_BATTLE_LOG_EXPORT?.remember?.(battle);
      window.IRON_PIT_FORMATION_BOARD?.renderBattle(battle.setup, battle.events || []);
    } catch (error) {
      console.error("Battle event log could not be rendered", error);
      throw error;
    }
  }

  function resetBattleView() {
    el("battle-log").replaceChildren(); el("result-panel").hidden = true;
    window.IRON_PIT_BATTLE_LOG_EXPORT?.remember?.(null);
    window.IRON_PIT_FORMATION_BOARD?.renderBattle({ heroes: [], monsters: [] }, []);
    for (const node of document.querySelectorAll(".battle-card.occupied")) {
      node.classList.remove("dead"); node.querySelector(".initiative-badge").textContent = "—";
      const maxHp = Number(node.dataset.maxHp || 0); node.dataset.currentHp = String(maxHp);
      node.querySelector(".hp-text").textContent = `${maxHp} / ${maxHp} HP`; node.querySelector(".card-hp span").style.width = "100%";
    }
  }

  window.IRON_PIT_BATTLEFIELD_VIEW = { appendEvents, eventRow, render, resetBattleView, showResult, writeLog };
})();
