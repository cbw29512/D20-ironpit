(() => {
  "use strict";

  function seedNumber(value) {
    const text = String(value ?? "");
    let hash = 2166136261;
    for (let index = 0; index < text.length; index += 1) {
      hash ^= text.charCodeAt(index);
      hash = Math.imul(hash, 16777619);
    }
    return (hash >>> 0) || 0x9e3779b9;
  }

  function createSeededDice(seed) {
    const label = String(seed ?? "");
    let state = seedNumber(label);
    function roll(sides) {
      if (!Number.isInteger(sides) || sides < 2) throw new RangeError("Die sides must be an integer >= 2.");
      state = (Math.imul(1664525, state) + 1013904223) >>> 0;
      return (state % sides) + 1;
    }
    return {
      seed: label,
      roll,
      rollMany: (count, sides) => {
        if (!Number.isInteger(count) || count < 1) throw new RangeError("Dice count must be positive.");
        return Array.from({ length: count }, () => roll(sides));
      },
    };
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

  function summary(battle, seed, replayStatus = "") {
    const events = battle.events || [];
    const attacks = events.filter((event) => event.event_type === "attack");
    const criticals = attacks.filter((event) => event.critical).length;
    const healing = events.filter((event) => event.event_type === "healing").length;
    const seedText = seed ? `Seed ${seed}` : "Secure random";
    const replayText = replayStatus ? ` · ${replayStatus}` : "";
    return `${seedText} · ${battle.rounds} rounds · ${attacks.length} attacks · ${criticals} criticals · ${healing} heals${replayText}`;
  }

  window.IRON_PIT_BATTLE_LAB = { createSeededDice, fingerprint, seedNumber, summary };
})();
