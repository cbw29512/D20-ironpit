(() => {
  "use strict";

  const PREFIX = "friendly-weapon-damage-aura:";
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || {
    incapacitated: (state) => state.is_unconscious || state.active_effect_ids?.includes("incapacitated"),
  };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];

  function active(source, actionId) {
    try {
      const state = source.state;
      if (state.is_dead || !state.is_alive || state.current_hp <= 0 || Q().incapacitated(state)) return false;
      return (state.timed_effects || []).some((effect) =>
        effect.source_id === source.combatant_id && effect.source_effect_id === actionId);
    } catch (error) {
      console.error("Failed weapon-damage aura source check.", { combatant: source?.combatant_id, error });
      throw error;
    }
  }

  function sync(setup) {
    try {
      if (!setup || !S() || !M()) return;
      for (const member of members(setup)) {
        member.state.active_modifiers = (member.state.active_modifiers || [])
          .filter((item) => !String(item.id || "").startsWith(PREFIX));
      }
      for (const source of members(setup)) {
        const actions = (source.state.template.timed_self_buff_actions || [])
          .filter((action) => action.friendlyWeaponDamageAura && active(source, action.id));
        const allies = source.side === "heroes" ? setup.heroes : setup.monsters;
        for (const action of actions) {
          const aura = action.friendlyWeaponDamageAura;
          for (const target of allies) {
            if (target.state.is_dead || !target.state.is_alive) continue;
            if (S().distance(source, target) > aura.radius_ft) continue;
            M().add(target.state, {
              id: `${PREFIX}${source.combatant_id}:${action.id}:${target.combatant_id}`,
              source_id: source.combatant_id,
              source_effect_id: action.id,
              source_name: action.name,
              kind: "bonus-damage",
              dice_count: aura.dice_count,
              dice_size: aura.dice_size,
              damage_type: aura.damage_type,
            });
          }
        }
      }
    } catch (error) {
      console.error("Failed to synchronize friendly weapon-damage auras.", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_FRIENDLY_WEAPON_DAMAGE_AURAS = { active, sync };
})();
