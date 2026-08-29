(() => {
  "use strict";

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  const delay = (ms) => sleep(reduced() ? Math.min(80, ms) : ms);
  const el = (id) => document.getElementById(id);
  const nodes = new Map();

  function figure(member) {
    const state = member.state, node = document.createElement("div");
    node.className = `pit-fighter ${member.side}`;
    node.dataset.combatantId = member.combatant_id;
    node.innerHTML = `<strong></strong><div class="stick-figure" aria-hidden="true"><i class="head"></i><i class="arms"></i><i class="body"></i><i class="legs"></i></div><div class="pit-hp"><span></span></div><small></small>`;
    node.querySelector("strong").textContent = state.template.name;
    node.querySelector("small").textContent = `${state.template.max_hp} HP`;
    node.querySelector(".pit-hp span").style.width = "100%";
    nodes.set(member.combatant_id, node);
    return node;
  }

  function reset(setup) {
    nodes.clear();
    el("pit-heroes").replaceChildren(...setup.heroes.map(figure));
    el("pit-monsters").replaceChildren(...setup.monsters.map(figure));
    el("pit-callout").textContent = "ROLL INITIATIVE";
    el("pit-round").textContent = "";
    el("pit-arena").hidden = false;
  }

  function hp(node, value, max) {
    const safe = Math.max(0, Math.min(Number(value) || 0, max));
    node.querySelector("small").textContent = `${safe} / ${max} HP`;
    node.querySelector(".pit-hp span").style.width = `${(safe / max) * 100}%`;
    if (safe === 0) node.classList.add("downed");
    else node.classList.remove("downed", "dead");
  }

  function callout(text, critical = false) {
    const node = el("pit-callout");
    node.textContent = text;
    node.classList.toggle("critical", critical);
  }

  async function attack(event) {
    const actor = nodes.get(event.actor_id), target = nodes.get(event.target_id);
    if (!actor || !target) return;
    actor.classList.add("attacking");
    if (event.critical) callout(`${event.actor_name} — CRITICAL HIT!`, true);
    else callout(`${event.actor_name} attacks ${event.target_name}`);
    await delay(180);
    if (event.hit) target.classList.add("hit");
    await delay(180);
    if (event.hp_after != null) hp(target, event.hp_after, Number(target.dataset.maxHp || target.querySelector("small").textContent.split("/").pop()) || event.hp_before || 1);
    if (event.is_dead) target.classList.add("dead");
    actor.classList.remove("attacking"); target.classList.remove("hit");
    await delay(150);
  }

  async function movement(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(`${event.actor_name} closes to ${event.distance_after_ft} ft`);
    actor.classList.add("advancing"); await delay(260); actor.classList.remove("advancing");
  }

  async function healing(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(event.description); actor.classList.add("healing");
    hp(actor, event.hp_after, Number(actor.dataset.maxHp)); await delay(280); actor.classList.remove("healing");
  }

  async function deathSave(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(event.description); actor.classList.add("death-save");
    if (event.hp_after != null) hp(actor, event.hp_after, Number(actor.dataset.maxHp));
    if (event.is_dead) actor.classList.add("dead");
    await delay(300); actor.classList.remove("death-save");
  }

  async function playEvent(event) {
    el("pit-round").textContent = `ROUND ${event.round_number}`;
    if (event.event_type === "attack") return attack(event);
    if (event.event_type === "movement") return movement(event);
    if (event.event_type === "healing") return healing(event);
    if (event.event_type === "death_save") return deathSave(event);
    if (event.event_type === "victory" || event.event_type === "draw") { callout(event.description); return delay(500); }
    if (event.event_type === "initiative") { callout(event.description); return delay(110); }
    if (event.description) callout(event.description);
    return delay(120);
  }

  async function play(battle) {
    reset(battle.setup);
    for (const member of [...battle.setup.heroes, ...battle.setup.monsters]) {
      const node = nodes.get(member.combatant_id); if (node) node.dataset.maxHp = String(member.state.template.max_hp);
    }
    el("pit-arena").scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "center" });
    for (const event of battle.events || []) await playEvent(event);
    return battle;
  }

  window.playIronPitBattle = play;
})();
