(() => {
  "use strict";

  const PREFIX = "friendly-save-aura:";
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

  function clear(setup) {
    for (const member of members(setup)) {
      member.state.active_modifiers = (member.state.active_modifiers || [])
        .filter((item) => !String(item.id || "").startsWith(PREFIX));
    }
  }

  function sync(setup) {
    try {
      if (!setup || !S() || !M()) return;
      clear(setup);
      for (const source of members(setup)) {
        const actions = (source.state.template.timed_self_buff_actions || [])
          .filter((action) => action.friendlySaveAdvantageAura && active(source, action));
        if (!actions.length) continue;
        const allies = source.side === "heroes" ? setup.heroes : setup.monsters;
        for (const action of actions) {
          const aura = action.friendlySaveAdvantageAura;
          for (const target of allies) {
            if (target.state.is_dead || !target.state.is_alive) continue;
            if (S().distance(source, target) > aura.radius_ft) continue;
            if (aura.requires_hearing && Q().has(target.state, "deafened")) continue;
            for (const ability of ABILITIES) {
              for (const tag of aura.required_effect_tags || []) {
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
        }
      }
    } catch (error) {
      console.error("Failed browser friendly save-aura synchronization.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FRIENDLY_SAVE_AURAS = { active, sync };
})();
