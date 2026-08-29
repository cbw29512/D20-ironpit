(() => {
  "use strict";

  const sleep = (ms) => new Promise((resolve) => window.setTimeout(resolve, ms));

  function prefersReducedMotion() {
    return window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  }

  function actorCard(actorId) {
    const match = /^(hero|monster)-(\d+):/.exec(String(actorId || ""));
    if (!match) return null;
    const rootId = match[1] === "hero" ? "hero-cards" : "monster-cards";
    const cards = document.querySelectorAll(`#${rootId} .combat-card`);
    return cards[Number(match[2]) - 1] || null;
  }

  function overlay() {
    let node = document.getElementById("combat-fx-overlay");
    if (node) return node;
    node = document.createElement("div");
    node.id = "combat-fx-overlay";
    node.setAttribute("aria-hidden", "true");
    const text = document.createElement("strong");
    text.id = "combat-fx-text";
    node.append(text);
    document.body.append(node);
    return node;
  }

  async function flashCritical(event) {
    const card = actorCard(event.actor_id);
    const screen = overlay();
    const label = document.getElementById("combat-fx-text");
    label.textContent = "CRITICAL HIT!";
    screen.className = "critical-screen";
    card?.classList.add("critical-hit");
    await sleep(prefersReducedMotion() ? 120 : 650);
    card?.classList.remove("critical-hit");
    screen.className = "";
  }

  async function flashFumble(event) {
    const card = actorCard(event.actor_id);
    const screen = overlay();
    const label = document.getElementById("combat-fx-text");
    label.textContent = "NATURAL 1 · MISS";
    screen.className = "fumble-screen";
    card?.classList.add("critical-fumble");
    await sleep(prefersReducedMotion() ? 120 : 700);
    card?.classList.remove("critical-fumble");
    screen.className = "";
  }

  function isNaturalOne(event) {
    return event.event_type === "attack" && event.attack_roll?.selected_roll === 1;
  }

  async function playCriticalEffects(battle) {
    try {
      for (const event of battle.events || []) {
        if (event.event_type !== "attack") continue;
        if (event.critical) await flashCritical(event);
        else if (isNaturalOne(event)) await flashFumble(event);
      }
    } catch (error) {
      console.error("Combat visual effect failed", error);
    }
  }

  window.playIronPitCriticalEffects = playCriticalEffects;
})();
