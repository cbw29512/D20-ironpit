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
    return side === "heroes" ? window.IRON_PIT_BROWSER_HEROES[card.runnable_template_id]
      : window.IRON_PIT_BROWSER_MONSTERS[card.runnable_template_id];
  }

  function figureMarkup(template) {
    try {
      const artwork = A()?.markup(template);
      const portrait = artwork || P()?.markup(template)
        || '<svg class="portrait-svg" viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="32"/></svg>';
      return `<div class="stick-figure fighter-portrait" aria-hidden="true">${portrait}</div>`;
    } catch (error) {
      console.error("Failed to render battlefield combatant visual", { templateId: template?.id, error });
      throw error;
    }
  }

  function emptySlot(side, index, onOpen) {
    const node = document.createElement("button");
    node.type = "button"; node.className = `battle-card empty-slot ${side}`; node.dataset.slotIndex = String(index);
    node.innerHTML = `<span class="slot-number">${index + 1}</span><b>＋</b><strong>${side === "heroes" ? "ADD PREGEN" : "ADD MONSTER"}</strong><small>Click to choose a card</small>`;
    node.addEventListener("click", () => onOpen(side, index)); return node;
  }

  function occupiedSlot(side, index, card, onOpen) {
    const template = runtimeTemplate(card, side), node = document.createElement("button");
    node.type = "button"; node.className = `battle-card occupied ${side}`; node.dataset.slotIndex = String(index);
    node.innerHTML = `<span class="slot-number">${index + 1}</span><span class="initiative-badge" aria-label="Initiative">—</span><strong class="card-name"></strong><small class="card-meta"></small>${figureMarkup(template)}<div class="card-status-lanes"><div class="card-status-lane card-status-buffs" aria-label="Buffs"><small>BUFFS</small><div class="card-concentration" hidden></div><div class="card-buffs"></div></div><div class="card-status-lane card-status-debuffs" aria-label="Debuffs"><small>DEBUFFS</small><div class="card-debuffs"></div></div></div><div class="card-hp"><span></span></div><small class="hp-text"></small><span class="death-stamp">✕ DEAD</span>`;
    node.querySelector(".card-name").textContent = card.name;
    node.querySelector(".card-meta").textContent = side === "heroes" ? `${card.class_name} · Level ${card.level} · ${card.build_name}` : `${card.monster_type} · CR ${card.challenge_rating}`;
    const hp = Number(template?.max_hp || card.hit_points || 0);
    node.dataset.maxHp = String(hp); node.dataset.currentHp = String(hp); node.querySelector(".hp-text").textContent = `${hp} / ${hp} HP`;
    node.querySelector(".card-hp span").style.width = "100%"; if (template) V()?.decorate(node, template);
    node.addEventListener("click", () => onOpen(side, index)); return node;
  }

  function renderSide(side, slots, onOpen) {
    const root = el(side === "heroes" ? "hero-slots" : "monster-slots"), nodes = [];
    for (let index = 0; index < MAX_SLOTS; index += 1) nodes.push(slots[index] ? occupiedSlot(side, index, slots[index], onOpen) : emptySlot(side, index, onOpen));
    root.replaceChildren(...nodes);
  }

  function render(state, onOpen) {
    renderSide("heroes", state.heroSlots, onOpen); renderSide("monsters", state.monsterSlots, onOpen);
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
    details.className = "rules-audit"; heading.textContent = `RULES AUDIT · ${steps.length} step${steps.length === 1 ? "" : "s"}`; body.className = "rules-audit-steps";
    steps.forEach((item, index) => {
      const row = document.createElement("div"); row.className = "rules-audit-step";
      row.innerHTML = `<span>${index + 1}</span><b></b><p></p>`;
      row.querySelector("b").textContent = String(item.phase || "rule").replaceAll("_", " ").toUpperCase();
      row.querySelector("p").textContent = item.label; body.append(row);
    });
    details.append(heading, body); return details;
  }

  function writeLog(battle) {
    const root = el("battle-log"); root.replaceChildren();
    battle.events.forEach((event) => {
      const li = document.createElement("li"), summary = document.createElement("div");
      summary.className = "battle-log-summary"; summary.textContent = `R${event.round_number}: ${L()?.format(event) || event.description}`; li.append(summary);
      const audit = auditDetails(event); if (audit) li.append(audit);
      if (event.critical) li.classList.add("log-critical");
      if (event.event_type === "attack" && event.attack_roll?.selected_roll === 1) li.classList.add("log-fumble");
      root.append(li);
    });
  }

  window.IRON_PIT_BATTLEFIELD_VIEW = { auditDetails, render, showResult, writeLog };
})();
