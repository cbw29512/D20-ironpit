(() => {
  "use strict";

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  const delay = (ms) => sleep(reduced() ? Math.min(80, ms) : ms);
  const el = (id) => document.getElementById(id);
  const V = () => window.IRON_PIT_FIGURE_VISUALS;
  const nodes = new Map();
  const persistent = new Set(["grappled", "restrained", "poisoned"]);

  function figure(member) {
    const state = member.state, node = document.createElement("div");
    node.className = `pit-fighter ${member.side}`;
    node.dataset.combatantId = member.combatant_id;
    node.dataset.maxHp = String(state.template.max_hp);
    node.dataset.conditions = "";
    node.innerHTML = `<strong></strong><div class="stick-figure" aria-hidden="true"><i class="head"></i><i class="body"></i><i class="arms"></i><i class="legs"></i><i class="tail"></i><i class="feature feature-one"></i><i class="feature feature-two"></i><i class="weapon"></i></div><div class="pit-status"></div><div class="pit-hp"><span></span></div><small></small>`;
    node.querySelector("strong").textContent = state.template.name;
    node.querySelector("small").textContent = `${state.template.max_hp} / ${state.template.max_hp} HP`;
    node.querySelector(".pit-hp span").style.width = "100%";
    V()?.decorate(node, state.template);
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

  function hp(node, value) {
    const max = Number(node.dataset.maxHp) || 1;
    const safe = Math.max(0, Math.min(Number(value) || 0, max));
    node.querySelector("small").textContent = `${safe} / ${max} HP`;
    node.querySelector(".pit-hp span").style.width = `${(safe / max) * 100}%`;
    if (safe === 0) node.classList.add("downed");
    else node.classList.remove("downed", "dead");
  }

  function statuses(node, add = [], remove = []) {
    const set = new Set((node.dataset.conditions || "").split(",").filter(Boolean));
    remove.forEach((id) => set.delete(id));
    add.filter((id) => persistent.has(id)).forEach((id) => set.add(id));
    node.dataset.conditions = [...set].join(",");
    node.classList.toggle("is-grappled", set.has("grappled"));
    node.classList.toggle("is-restrained", set.has("restrained"));
    node.classList.toggle("is-poisoned", set.has("poisoned"));
    node.querySelector(".pit-status").textContent = [...set].map((id) => id === "grappled" ? "⛓ GRAPPLED" : id === "restrained" ? "⌁ RESTRAINED" : "☠ POISONED").join(" · ");
  }

  function callout(text, critical = false) {
    const node = el("pit-callout");
    node.textContent = text;
    node.classList.toggle("critical", critical);
  }

  const motionClass = (event) => `motion-${String(event.animation || "strike").replace(/[^a-z0-9-]/gi, "")}`;

  async function attack(event) {
    const actor = nodes.get(event.actor_id), target = nodes.get(event.target_id);
    if (!actor || !target) return;
    const motion = motionClass(event);
    actor.classList.add("attacking", motion);
    callout(event.critical ? `${event.actor_name} — CRITICAL HIT!` : `${event.actor_name} attacks ${event.target_name}`, event.critical);
    await delay(180);
    if (event.hit) target.classList.add("hit");
    if (event.applied_condition_ids?.includes("prone")) target.classList.add("prone-hit");
    await delay(180);
    if (event.hp_after != null) hp(target, event.hp_after);
    statuses(target, event.applied_condition_ids || []);
    if (event.is_dead) target.classList.add("dead");
    actor.classList.remove("attacking", motion); target.classList.remove("hit", "prone-hit");
    await delay(150);
  }

  async function savingThrow(event) {
    const actor = nodes.get(event.actor_id), target = nodes.get(event.target_id);
    if (!actor || !target) return;
    const motion = motionClass(event);
    actor.classList.add("attacking", motion); callout(event.description); await delay(190);
    if (event.damage_roll?.total) target.classList.add("hit");
    if (event.hp_after != null) hp(target, event.hp_after);
    statuses(target, event.applied_condition_ids || []); await delay(210);
    actor.classList.remove("attacking", motion); target.classList.remove("hit");
  }

  async function movement(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(`${event.actor_name} closes to ${event.distance_after_ft} ft`);
    actor.classList.add("advancing"); await delay(260); actor.classList.remove("advancing");
  }

  async function feature(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return delay(80);
    const target = nodes.get(event.target_id); callout(event.description || event.feature_id || "Feature");
    if (event.feature_id === "escape-grapple" && event.check_succeeded) statuses(actor, [], ["grappled", "restrained"]);
    if (target && event.removed_condition_ids?.length) statuses(target, [], event.removed_condition_ids);
    actor.classList.add("feature-pulse"); await delay(200); actor.classList.remove("feature-pulse");
  }

  async function healing(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(event.description); actor.classList.add("healing"); hp(actor, event.hp_after);
    await delay(280); actor.classList.remove("healing");
  }

  async function deathSave(event) {
    const actor = nodes.get(event.actor_id); if (!actor) return;
    callout(event.description); actor.classList.add("death-save");
    if (event.hp_after != null) hp(actor, event.hp_after);
    if (event.is_dead) actor.classList.add("dead");
    await delay(300); actor.classList.remove("death-save");
  }

  async function playEvent(event) {
    el("pit-round").textContent = `ROUND ${event.round_number}`;
    if (event.event_type === "attack") return attack(event);
    if (event.event_type === "saving_throw") return savingThrow(event);
    if (event.event_type === "movement") return movement(event);
    if (event.event_type === "feature") return feature(event);
    if (event.event_type === "healing") return healing(event);
    if (event.event_type === "death_save") return deathSave(event);
    if (event.event_type === "victory" || event.event_type === "draw") { callout(event.description); return delay(500); }
    if (event.event_type === "initiative") { callout(event.description); return delay(110); }
    if (event.description) callout(event.description); return delay(120);
  }

  async function play(battle, onEvent = null) {
    reset(battle.setup);
    el("pit-arena").scrollIntoView({ behavior: reduced() ? "auto" : "smooth", block: "center" });
    for (const event of battle.events || []) { await playEvent(event); if (onEvent) onEvent(event); }
    return battle;
  }

  window.playIronPitBattle = play;
})();
