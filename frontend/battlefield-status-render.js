(() => {
  "use strict";

  function renderLane(node, selector, ids, kind, permanent = [], labels = {}) {
    try {
      const rack = node?.querySelector(selector);
      if (!rack) return;
      const cleanLabel = labels.cleanLabel;
      const conditionLabel = labels.conditionLabel;
      if (typeof cleanLabel !== "function" || typeof conditionLabel !== "function") {
        throw new Error("Battlefield status renderer requires label functions.");
      }

      const existing = new Map(
        [...rack.children].map((badge) => [badge.dataset.effect, badge]),
      );
      const badges = ids.map((id) => {
        const old = existing.get(id);
        if (old) return old;
        const badge = document.createElement("span");
        badge.className = kind === "buff"
          ? `buff-badge buff-${id} status-enter`
          : `debuff-badge condition-badge condition-${id} status-enter`;
        badge.dataset.effect = id;
        badge.textContent = kind === "debuff" ? conditionLabel(id) : cleanLabel(id);
        badge.setAttribute(
          "aria-label",
          `${kind === "buff" ? "Buff" : "Debuff"}: ${cleanLabel(id)}`,
        );
        return badge;
      });

      for (const passive of permanent) {
        const badge = existing.get(passive.id) || document.createElement("span");
        badge.className = `${kind === "debuff" ? "debuff-badge" : "buff-badge"} passive-badge${passive.active ? "" : " is-inactive"}`;
        badge.dataset.effect = passive.id;
        badge.textContent = String(passive.label || passive.id).toUpperCase();
        badge.title = `${passive.explanation} Currently ${passive.active ? "active" : "inactive"}.`;
        badge.setAttribute(
          "aria-label",
          `${kind === "buff" ? "Buff" : "Debuff"}: ${passive.label || passive.id}; ${passive.active ? "active" : "inactive"}`,
        );
        badges.push(badge);
      }

      const keep = new Set(badges);
      for (const child of [...rack.children]) {
        if (!keep.has(child)) child.remove();
      }
      for (const badge of badges) rack.appendChild(badge);
    } catch (error) {
      console.error("Failed to render combat status lane", { selector, kind, error });
      throw error;
    }
  }

  function renderStateLanes(node, state, permanent = [], labels = {}) {
    try {
      if (!node) return;
      const classify = window.IRON_PIT_BATTLEFIELD_PASSIVE_STATES?.classifyStatusLanes;
      if (!classify) throw new Error("Battlefield status classifier is not loaded.");
      const lanes = classify(state);
      const buffs = permanent.filter((item) => item.lane !== "debuff");
      const debuffs = permanent.filter((item) => item.lane === "debuff");
      renderLane(node, ".card-buffs", lanes.buffs, "buff", buffs, labels);
      renderLane(node, ".card-debuffs", lanes.debuffs, "debuff", debuffs, labels);
      node.classList.toggle(
        "has-buff",
        lanes.buffs.length > 0 || buffs.some((item) => item.active) || Boolean(state.concentration),
      );
      node.classList.toggle(
        "has-debuff",
        lanes.debuffs.length > 0 || debuffs.some((item) => item.active),
      );
      node.classList.toggle("has-condition", lanes.debuffs.length > 0);
    } catch (error) {
      console.error("Failed to render battlefield status lanes", { state, error });
      throw error;
    }
  }

  window.IRON_PIT_BATTLEFIELD_STATUS_RENDER = { renderLane, renderStateLanes };
})();
