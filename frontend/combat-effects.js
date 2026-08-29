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

  async function showMoment(event, kind) {
    const card = actorCard(event.actor_id);
    const screen = overlay();
    const label = document.getElementById("combat-fx-text");
    const actor = event.actor_name || "Combatant";
    const critical = kind === "critical";
    label.textContent = critical
      ? `${actor} — CRITICAL HIT!`
      : `${actor} — NATURAL 1 · MISS!`;
    screen.setAttribute("aria-hidden", "false");
    screen.className = critical ? "critical-screen" : "fumble-screen";
    card?.classList.add(critical ? "critical-hit" : "critical-fumble");
    const duration = prefersReducedMotion() ? 900 : (critical ? 1250 : 1100);
    await sleep(duration);
    card?.classList.remove("critical-hit", "critical-fumble");
    screen.className = "";
    screen.setAttribute("aria-hidden", "true");
    await sleep(120);
  }

  function isNaturalOne(event) {
    return event.event_type === "attack" && event.attack_roll?.selected_roll === 1;
  }

  async function playCriticalEffects(battle) {
    try {
      let played = 0;
      for (const event of battle.events || []) {
        if (event.event_type !== "attack") continue;
        if (event.critical) {
          await showMoment(event, "critical");
          played += 1;
        } else if (isNaturalOne(event)) {
          await showMoment(event, "fumble");
          played += 1;
        }
      }
      return played;
    } catch (error) {
      console.error("Combat visual effect failed", error);
      return 0;
    }
  }

  window.playIronPitCriticalEffects = playCriticalEffects;
})();
