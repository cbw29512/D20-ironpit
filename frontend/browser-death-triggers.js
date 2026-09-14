(() => {
  "use strict";

  const G = () => window.IRON_PIT_BROWSER_GRID_GEOMETRY;
  const S = () => window.IRON_PIT_BROWSER_SAVES;

  function action(effect) {
    try {
      return {
        id: effect.id,
        name: effect.name,
        saveAbility: effect.save_ability,
        dc: effect.dc,
        range: effect.radius_ft,
        damageDiceCount: effect.damage_dice_count,
        damageDiceSize: effect.damage_dice_size,
        damageBonus: effect.damage_bonus || 0,
        damageType: effect.damage_type,
        successDamage: effect.half_damage_on_success ? "half" : "none",
        animation: "death-trigger",
      };
    } catch (error) {
      console.error("Failed to compile browser death trigger", { effect, error });
      throw error;
    }
  }

  function distance(source, target) {
    try {
      if (!source.state.position || !target.state.position) {
        throw new Error("Death-trigger resolution requires authoritative grid positions.");
      }
      return G().footprintDistanceFt(
        source.state.position, source.state.template.size,
        target.state.position, target.state.template.size,
      );
    } catch (error) {
      console.error("Failed browser death-trigger distance check", { source: source.combatant_id, target: target.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, source, setup, resolved = new Set()) {
    try {
      if (!source.state.is_dead) return { events: [], sequence };
      const events = [], members = [...setup.heroes, ...setup.monsters];
      for (const effect of source.state.template.death_trigger_effects || []) {
        const key = `${source.combatant_id}:${effect.id}`;
        if (resolved.has(key)) continue;
        resolved.add(key);
        const saveAction = action(effect);
        const targets = members.filter((target) => target.combatant_id !== source.combatant_id
          && !target.state.is_dead && distance(source, target) <= effect.radius_ft);
        const shared = [], newlyDead = [];
        for (let index = 0; index < targets.length; index += 1) {
          const target = targets[index], wasDead = target.state.is_dead;
          const event = S().resolveAction(sequence, round, source, target, saveAction, distance(source, target), {
            spendAction: false,
            spendResourceCost: false,
            sharedDamageRolls: shared.length ? shared : null,
            captureSharedDamageRolls: index === 0 ? shared : null,
            setup,
          });
          events.push(event); sequence += 1;
          if (!wasDead && target.state.is_dead && (target.state.template.death_trigger_effects || []).length) newlyDead.push(target);
        }
        for (const deadTarget of newlyDead) {
          const chained = resolve(sequence, round, deadTarget, setup, resolved);
          events.push(...chained.events); sequence = chained.sequence;
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser death-trigger resolution failed", { source: source.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_DEATH_TRIGGERS = { resolve };
})();
