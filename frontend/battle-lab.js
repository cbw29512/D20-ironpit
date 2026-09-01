(() => {
  "use strict";

  function hashText(value) {
    const text = String(value ?? "");
    let hash = 2166136261;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0).toString(16).padStart(8, "0");
  }

  function diagnosticId(heroIds, monsterIds, rolls) {
    return hashText(JSON.stringify({ hero_ids: heroIds, monster_ids: monsterIds, rolls }));
  }

  function fingerprint(battle) {
    return JSON.stringify({
      outcome: battle.outcome,
      rounds: battle.rounds,
      initiative: battle.initiative?.turn_order || [],
      final: [...(battle.setup?.heroes || []), ...(battle.setup?.monsters || [])].map((member) => ({
        id: member.combatant_id,
        hp: member.state.current_hp,
        temporary_hp: member.state.temporary_hp,
        alive: member.state.is_alive,
        dead: member.state.is_dead,
        stable: member.state.is_stable,
        death_save_successes: member.state.death_save_successes,
        death_save_failures: member.state.death_save_failures,
      })),
      events: (battle.events || []).map((event) => ({
        round: event.round_number,
        type: event.event_type,
        actor: event.actor_id,
        target: event.target_id || null,
        hit: event.hit ?? null,
        critical: event.critical ?? null,
        attack_roll: event.attack_roll ? {
          mode: event.attack_roll.mode,
          selected: event.attack_roll.selected_roll,
          total: event.attack_roll.total,
        } : null,
        damage: event.damage_roll?.total ?? null,
        hp_before: event.hp_before ?? null,
        hp_after: event.hp_after ?? null,
        feature: event.feature_id || null,
        weapon: event.weapon_id || null,
      })),
    });
  }

  function summary(battle, rolls, id) {
    const events = battle.events || [];
    const attacks = events.filter((event) => event.event_type === "attack");
    const criticals = attacks.filter((event) => event.critical).length;
    const healing = events.filter((event) => event.event_type === "healing").length;
    return `Battle ${id} · ${rolls.length} secure dice rolls · ${battle.rounds} rounds · ${attacks.length} attacks · ${criticals} criticals · ${healing} heals`;
  }

  window.IRON_PIT_BATTLE_LAB = { diagnosticId, fingerprint, hashText, summary };
})();
