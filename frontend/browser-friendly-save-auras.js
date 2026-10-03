(() => {
  "use strict";

  const PREFIX = "friendly-save-aura:";
  const COVER_PREFIX = "friendly-cover-aura:";
  const CONDITION_PREFIX = "friendly-condition-aura:";
  const ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"];
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    has: (state, id) => state.active_effect_ids?.includes(id) || false,
    incapacitated: (state) => state.is_unconscious || state.active_effect_ids?.includes("incapacitated"),
  };

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function active(source, action) {
    try {
      const state = source.state;
      if (state.is_dead || !state.is_alive || state.current_hp <= 0 || Q().incapacitated(state)) return false;
      return (state.timed_effects || []).some((effect) =>
        effect.source_id === source.combatant_id && effect.source_effect_id === action.id);
    } catch (error) {
      console.error("Failed browser friendly save-aura source check.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function passiveActive(source, aura) {
    try {
      const state = source.state;
      if (state.is_dead || !state.is_alive || state.current_hp <= 0) return false;
      if (aura.inactive_while_incapacitated && Q().incapacitated(state)) return false;
      if (aura.inactive_while_unconscious
          && (state.is_unconscious || Q().has(state, "unconscious"))) return false;
      return true;
    } catch (error) {
      console.error("Failed browser passive friendly save-aura source check.", {
        combatant: source?.combatant_id, error,
      });
      throw error;
    }
  }

  function clear(setup) {
    for (const member of members(setup)) {
      member.state.active_modifiers = (member.state.active_modifiers || [])
        .filter((item) => !String(item.id || "").startsWith(PREFIX)
          && !String(item.id || "").startsWith(COVER_PREFIX)
          && !String(item.id || "").startsWith(CONDITION_PREFIX));
    }
  }

  function sync(setup) {
    try {
      if (!setup || !S() || !M()) return;
      clear(setup);
      const allMembers = members(setup);
      for (const source of allMembers) {
        const actions = (source.state.template.timed_self_buff_actions || [])
          .filter((action) => (action.friendlySaveAdvantageAura || action.friendlyCoverAura) && active(source, action));
        if (!actions.length) continue;
        const allies = source.side === "heroes" ? setup.heroes : setup.monsters;
        for (const action of actions) {
          const saveAura = action.friendlySaveAdvantageAura;
          const coverAura = action.friendlyCoverAura;
          for (const target of allies) {
            if (target.state.is_dead || !target.state.is_alive) continue;
            if (saveAura && S().distance(source, target) <= saveAura.radius_ft
                && !(saveAura.requires_hearing && Q().has(target.state, "deafened"))) {
              for (const ability of ABILITIES) {
                for (const tag of saveAura.required_effect_tags || []) {
                  M().add(target.state, {
                    id: `${PREFIX}${source.combatant_id}:${action.id}:${target.combatant_id}:${ability}:${tag}`,
                    source_id: source.combatant_id,
                    source_effect_id: action.id,
                    source_name: action.name,
                    kind: "saving-throw-advantage",
                    save_ability: ability,
                    required_effect_tags: [tag],
                  });
                }
              }
            }
            if (coverAura && S().distance(source, target) <= coverAura.radius_ft) {
              M().add(target.state, {
                id: `${COVER_PREFIX}${source.combatant_id}:${action.id}:${target.combatant_id}:ac`,
                source_id: source.combatant_id, source_effect_id: action.id, source_name: action.name,
                kind: "cover-armor-class", flat_bonus: coverAura.cover_bonus,
              });
              M().add(target.state, {
                id: `${COVER_PREFIX}${source.combatant_id}:${action.id}:${target.combatant_id}:dex`,
                source_id: source.combatant_id, source_effect_id: action.id, source_name: action.name,
                kind: "cover-saving-throw-flat", flat_bonus: coverAura.cover_bonus, save_ability: "dexterity",
              });
            }
          }
        }
      }

      for (const target of allMembers) {
        const allies = target.side === "heroes" ? setup.heroes : setup.monsters;
        const candidates = [];
        for (const source of allies) {
          const aura = source.state.template.friendly_saving_throw_aura;
          if (!aura || !passiveActive(source, aura)) continue;
          if (S().distance(source, target) > aura.radius_ft) continue;
          candidates.push([aura.flat_bonus, source.combatant_id, source, aura]);
        }
        candidates.sort((a, b) => b[0] - a[0] || b[1].localeCompare(a[1]));
        if (candidates.length) {
          const [, , source, aura] = candidates[0];
          M().add(target.state, {
            id: `${PREFIX}flat:${source.combatant_id}:${aura.source_id}:${target.combatant_id}`,
            source_id: source.combatant_id,
            source_effect_id: aura.source_id,
            source_name: aura.source_name,
            kind: "saving-throw-flat",
            flat_bonus: aura.flat_bonus,
          });
        }

        for (const source of allies) {
          for (const aura of source.state.template.friendly_condition_immunity_auras || []) {
            if (!passiveActive(source, aura)) continue;
            if (S().distance(source, target) > aura.radius_ft) continue;
            if ((target.state.template.condition_immunities || []).includes(aura.condition_id)) continue;
            M().add(target.state, {
              id: `${CONDITION_PREFIX}${source.combatant_id}:${aura.source_id}:${target.combatant_id}:${aura.condition_id}`,
              source_id: source.combatant_id,
              source_effect_id: aura.source_id,
              source_name: aura.source_name,
              kind: "condition-immunity",
              condition_id: aura.condition_id,
            });
          }
        }
      }
    } catch (error) {
      console.error("Failed browser friendly save-aura synchronization.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS = { active, sync };
})();
