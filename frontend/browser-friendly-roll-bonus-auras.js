(() => {
  "use strict";
  const PREFIX = "friendly-roll-bonus-aura:";
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  function sync(setup) {
    try {
      const state = window.IRON_PIT_BROWSER_STATE;
      const modifiers = window.IRON_PIT_BROWSER_MODIFIERS;
      if (!state || !modifiers || !setup) throw new Error("Friendly roll-bonus aura dependencies unavailable.");
      for (const target of members(setup)) {
        target.state.active_modifiers = (target.state.active_modifiers || [])
          .filter((item) => !String(item.id || "").startsWith(PREFIX));
      }
      for (const side of [setup.heroes, setup.monsters]) {
        for (const source of side) {
          const s = source.state;
          if (s.is_dead || !s.is_alive || s.current_hp <= 0) continue;
          for (const action of s.template.timed_self_buff_actions || []) {
            const aura = action.friendlyRollBonusAura;
            if (!aura || !(s.timed_effects || []).some((effect) =>
              effect.source_id === source.combatant_id && effect.source_effect_id === action.id)) continue;
            for (const target of side) {
              if (target.state.is_dead || !target.state.is_alive) continue;
              if (source.combatant_id === target.combatant_id && !aura.includes_source) continue;
              const distance = state.distance(source, target);
              if (distance > aura.radius_ft) continue;
              if (aura.requires_source_sight &&
                  !window.IRON_PIT_BROWSER_CONDITION_RULES.canSee(s, target.state, distance)) continue;
              if (aura.requires_hearing &&
                  (window.IRON_PIT_BROWSER_CONDITION_RULES?.has(target.state, "deafened")
                   || target.state.active_effect_ids?.includes("deafened"))) continue;
              for (const [kind, count, size] of [
                ["attack-roll-bonus-die", aura.attack_dice_count, aura.attack_dice_size],
                ["saving-throw-bonus-die", aura.save_dice_count, aura.save_dice_size],
              ]) {
                if (!count) continue;
                const owner = aura.stack_group ? `group:${aura.stack_group}` : `${source.combatant_id}:${action.id}`;
                const id = `${PREFIX}${owner}:${target.combatant_id}:${kind}`;
                if (target.state.active_modifiers.some((item) => item.id === id)) continue;
                modifiers.add(target.state, {
                  id,
                  source_id: source.combatant_id, source_effect_id: action.id,
                  source_name: action.name, kind, dice_count: count, dice_size: size,
                });
              }
            }
          }
        }
      }
    } catch (error) {
      console.error("Failed to synchronize friendly roll-bonus auras.", { error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_FRIENDLY_ROLL_BONUS_AURAS = { sync };
})();
