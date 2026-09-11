(() => {
  "use strict";
  const O = () => window.IRON_PIT_BROWSER_ONGOING_DAMAGE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const incapacitated = (state) => state.active_effect_ids?.includes("incapacitated") || state.is_unconscious || state.is_dead;

  function turnEnd(sequence, round, source, setup) {
    const events = [];
    if (source.state.is_dead || !source.state.is_alive) return { events, sequence };
    for (const aura of source.state.template.end_turn_damage_auras || []) {
      if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
      const targets = members(setup).filter((member) =>
        member.side !== source.side && member.state.is_alive && !member.state.is_dead && S().distance(source, member) <= aura.radius_ft
      );
      for (const target of targets) {
        events.push(O().resolve(sequence++, round, source, target, setup, {
          featureId: aura.id, featureName: aura.name, diceCount: aura.damage_dice_count,
          diceSize: aura.damage_dice_size, damageBonus: aura.damage_bonus || 0,
          damageType: aura.damage_type, animation: "aura-damage",
        }));
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_AURAS = { turnEnd };
})();
