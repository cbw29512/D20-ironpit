(() => {
  "use strict";

  // Every badge is a projection of an authoritative source-target link,
  // never an extra condition or independent fight-state buff.
  const keyFor = (link) => `${link.source_id}\u001f${link.effect_id}`;

  function applyChanges(previous, changes) {
    try {
      const next = new Map(previous);
      for (const change of changes || []) {
        if (!change?.source_id || !change?.target_id || !change?.effect_id || !change?.source_name) {
          throw Error("Malformed attachment status receipt.");
        }
        if (change.operation === "attach") next.set(keyFor(change), change);
        else if (change.operation === "detach") next.delete(keyFor(change));
        else throw Error("Unknown attachment status transition.");
      }
      return next;
    } catch (error) {
      console.error("Could not project linked attachment change", error);
      throw error;
    }
  }

  function removeCombatant(previous, combatantId) {
    try {
      const next = new Map(previous);
      for (const [key, link] of next) {
        if (link.source_id === combatantId || link.target_id === combatantId) next.delete(key);
      }
      return next;
    } catch (error) {
      console.error("Could not expire dead combatant attachment badges", error);
      throw error;
    }
  }

  function fromSetup(setup) {
    try {
      return new Map((setup?.attachments || []).map((link) => [keyFor(link), link]));
    } catch (error) {
      console.error("Could not project final attachment state", error);
      throw error;
    }
  }

  function labelsFor(links, combatantId) {
    try {
      const buffs = [], debuffs = [];
      for (const [key, link] of links) {
        if (link.source_id === combatantId) {
          buffs.push({ key, text: "FEEDING", source: link.source_name });
        }
        if (link.target_id === combatantId) {
          debuffs.push({ key, text: "ATTACHED", source: link.source_name });
        }
      }
      return { buffs, debuffs };
    } catch (error) {
      console.error("Could not resolve attached status labels", error);
      throw error;
    }
  }

  function sync(nodes, links) {
    try {
      for (const [id, node] of nodes) {
        if (!node) continue;
        const { buffs, debuffs } = labelsFor(links, id);
        for (const [selector, kind, rows] of [
          [".card-buffs", "buff", buffs], [".card-debuffs", "debuff", debuffs],
        ]) {
          const rack = node.querySelector(selector);
          if (!rack) continue;
          for (const child of [...rack.children]) {
            if (child.dataset.linkedAttachment != null) child.remove();
          }
          for (const row of rows) {
            const badge = document.createElement("span");
            badge.dataset.linkedAttachment = row.key;
            badge.className = kind === "buff" ? "buff-badge status-enter" :
              "debuff-badge condition-badge status-enter";
            badge.textContent = row.text;
            badge.title = row.source;
            badge.setAttribute("aria-label", `${kind}: ${row.text}, ${row.source}`);
            rack.appendChild(badge);
          }
        }
        node.classList.toggle("has-buff",
          Boolean(node.querySelector(".card-buffs")?.children.length) ||
          Boolean(node.querySelector(".card-concentration") && !node.querySelector(".card-concentration").hidden));
        node.classList.toggle("has-debuff", Boolean(node.querySelector(".card-debuffs")?.children.length));
        node.classList.toggle("has-condition", Boolean(node.querySelector(".card-debuffs")?.children.length));
      }
    } catch (error) {
      console.error("Could not render attachment buff/debuff projections", error);
      throw error;
    }
  }

  window.IRON_PIT_BATTLEFIELD_ATTACHMENT_STATUS = {
    keyFor, applyChanges, removeCombatant, fromSetup, labelsFor, sync,
  };
})();
