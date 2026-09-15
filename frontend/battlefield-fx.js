(() => {
  "use strict";

  const TRANSIENT = ["fx-move", "fx-melee", "fx-ranged", "fx-cast", "fx-hit"];
  const reduced = () => window.matchMedia?.("(prefers-reduced-motion: reduce)")?.matches === true;
  const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, reduced() ? Math.min(ms, 70) : ms));

  function clear(...nodes) {
    for (const node of nodes) if (node) TRANSIENT.forEach((name) => node.classList.remove(name));
  }

  function ranged(event) {
    const animation = String(event.animation || "").toLowerCase();
    return Boolean(event.projectile) || /projectile|arrow|bolt|ray|ranged|shot/.test(animation);
  }

  function syncConditionPose(node, ids) {
    if (!node) return;
    const set = ids instanceof Set ? ids : new Set(ids || []);
    node.classList.toggle("condition-prone", set.has("prone"));
    node.classList.toggle("condition-restrained", set.has("restrained") || set.has("grappled"));
    node.classList.toggle("condition-stunned", set.has("stunned") || set.has("paralyzed"));
  }

  async function combat(event, actor, target) {
    if (reduced()) return;
    clear(actor, target);
    if (event.event_type === "movement" && actor) actor.classList.add("fx-move");
    else if (event.event_type === "attack" && actor) {
      actor.classList.add(ranged(event) ? "fx-ranged" : "fx-melee");
      if (target && event.hit) target.classList.add("fx-hit");
    } else if (["saving_throw", "spell", "healing"].includes(event.event_type) && actor) {
      actor.classList.add("fx-cast");
      const damaged = target && event.hp_before != null && event.hp_after != null && Number(event.hp_after) < Number(event.hp_before);
      if (damaged) target.classList.add("fx-hit");
    }
    await sleep(event.event_type === "movement" ? 130 : 190);
    clear(actor, target);
  }

  window.IRON_PIT_BATTLEFIELD_FX = { combat, ranged, syncConditionPose };
})();
