(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const D = () => window.IRON_PIT_DICE;
  const CHANNEL = "channel-divinity", TURN = "turn-undead", TURNED = "turned-undead", SPARK = "divine-spark";
  const distance = (a, b) => Math.abs(a.position_ft - b.position_ft);
  const living = (m) => m.state.is_alive && !m.state.is_dead;
  const side = (m, setup, allies) => allies === (m.side === "heroes") ? setup.heroes : setup.monsters;
  const baseType = (m) => String(m.state.template.creature_type || "").split(" (")[0].toLowerCase();

  function saveDc(cleric) {
    const dcs = [...new Set((cleric.state.template.spell_save_actions || []).map((a) => a.dc))];
    if (dcs.length !== 1) throw new Error("Channel Divinity requires one certified Cleric spell save DC.");
    return dcs[0];
  }

  function wisdomModifier(cleric) {
    const proficiency = 2 + Math.floor((cleric.state.template.level - 1) / 4);
    return saveDc(cleric) - 8 - proficiency;
  }

  function slotsRemain(cleric) {
    return Object.entries(cleric.state.resources).some(([id, uses]) => id.startsWith("spell-slot-") && uses > 0);
  }

  function choose(cleric, setup) {
    if (!E().available(cleric.state, "action") || !(cleric.state.resources[CHANNEL] > 0)) return null;
    const allies = side(cleric, setup, true).filter(living);
    const downed = allies.filter((m) => m.combatant_id !== cleric.combatant_id && m.state.current_hp === 0 && distance(cleric, m) <= 30)
      .sort((a, b) => b.state.death_save_failures - a.state.death_save_failures || a.combatant_id.localeCompare(b.combatant_id));
    if (downed.length && !slotsRemain(cleric)) return { kind: "divine-spark-heal", targets: [downed[0]] };
    const enemies = side(cleric, setup, false).filter((m) => living(m) && m.state.current_hp > 0 && distance(cleric, m) <= 30);
    const undead = enemies.filter((m) => baseType(m) === "undead").sort((a, b) => distance(cleric, a) - distance(cleric, b) || a.combatant_id.localeCompare(b.combatant_id));
    if (undead.length) return { kind: "turn-undead", targets: undead };
    if (slotsRemain(cleric)) return null;
    enemies.sort((a, b) => distance(cleric, a) - distance(cleric, b) || a.combatant_id.localeCompare(b.combatant_id));
    return enemies.length ? { kind: "divine-spark-damage", targets: [enemies[0]] } : null;
  }

  function spend(cleric) {
    if (!E().available(cleric.state, "action") || !(cleric.state.resources[CHANNEL] > 0)) throw new Error("Channel Divinity is unavailable.");
    E().spend(cleric.state, "action"); cleric.state.resources[CHANNEL] -= 1;
    return cleric.state.resources[CHANNEL];
  }

  function turnEffects(cleric, target, round) {
    const common = { sourceEffectId: TURN, appliedRound: round, expiresRound: round + 10, expiryTiming: "source_turn_start",
      endsOnDamage: true, endsIfSourceIncapacitated: true, endsIfSourceDead: true };
    const applied = [T().apply(target.state, TURNED, cleric.combatant_id, { ...common, turnBehavior: "forced_retreat" })];
    for (const condition of ["frightened", "incapacitated"]) if (!I().immune(target.state, condition)) applied.push(T().apply(target.state, condition, cleric.combatant_id, common));
    return applied.filter(Boolean);
  }

  function resolveTurnUndead(sequence, round, cleric, setup, targets) {
    if (!targets.length || targets.some((t) => distance(cleric, t) > 30 || baseType(t) !== "undead")) throw new Error("Turn Undead requires Undead targets within 30 feet.");
    const dc = saveDc(cleric), remaining = spend(cleric), events = [];
    for (const target of targets) {
      const save = V().resolveSavingThrow(target.state, "wisdom", dc);
      const applied = save.succeeded ? [] : turnEffects(cleric, target, round);
      events.push({ sequence: sequence++, round_number: round, event_type: "saving_throw", actor_id: cleric.combatant_id,
        actor_name: cleric.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "wisdom", save_dc: dc, save_succeeded: save.succeeded,
        applied_condition_ids: applied, feature_id: TURN, resource_remaining: remaining, animation: TURN,
        description: `${target.state.template.name} ${save.succeeded ? "resists" : "fails"} ${cleric.state.template.name}'s Turn Undead.` });
    }
    return { events, sequence };
  }

  function resolveSpark(sequence, round, cleric, setup, choice) {
    const target = choice.targets[0]; if (!target || target.combatant_id === cleric.combatant_id || distance(cleric, target) > 30) throw new Error("Divine Spark requires another creature within 30 feet.");
    const remaining = spend(cleric), die = D().roll(8), mod = wisdomModifier(cleric), total = die + mod, notation = `1d8+${mod}`;
    if (choice.kind === "divine-spark-heal") {
      const before = target.state.current_hp, healed = H().restore(target.state, total);
      return { events: [{ sequence, round_number: round, event_type: "healing", actor_id: cleric.combatant_id, actor_name: cleric.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name, healing_roll: { notation, rolls: [die], modifier: mod, total },
        hp_before: before, hp_after: target.state.current_hp, feature_id: SPARK, resource_remaining: remaining, animation: SPARK,
        description: `${cleric.state.template.name} restores ${healed} HP with Divine Spark.` }], sequence: sequence + 1 };
    }
    const dc = saveDc(cleric), save = V().resolveSavingThrow(target.state, "constitution", dc);
    const type = A().adjustedDamage(target.state, 2, "radiant") >= A().adjustedDamage(target.state, 2, "necrotic") ? "radiant" : "necrotic";
    const raw = save.succeeded ? Math.floor(total / 2) : total, applied = A().adjustedDamage(target.state, raw, type), before = target.state.current_hp;
    if (applied) A().applyDamage(target.state, applied, false, [type], [...setup.heroes, ...setup.monsters].map((m) => m.state));
    return { events: [{ sequence, round_number: round, event_type: "saving_throw", actor_id: cleric.combatant_id, actor_name: cleric.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, saving_throw_roll: save.roll, save_ability: "constitution", save_dc: dc,
      save_succeeded: save.succeeded, damage_roll: { notation, rolls: [die], modifier: mod, total: applied },
      damage_components: [{ source: "Divine Spark", notation, rolls: [die], modifier: mod, damage_type: type, total: raw, applied_total: applied }],
      hp_before: before, hp_after: target.state.current_hp, feature_id: SPARK, resource_remaining: remaining, animation: SPARK,
      description: `${target.state.template.name} takes ${applied} ${type} damage from Divine Spark.` }], sequence: sequence + 1 };
  }

  function resolve(sequence, round, cleric, setup) {
    const choice = choose(cleric, setup); if (!choice) return { events: [], sequence };
    return choice.kind === "turn-undead" ? resolveTurnUndead(sequence, round, cleric, setup, choice.targets) : resolveSpark(sequence, round, cleric, setup, choice);
  }

  window.IRON_PIT_BROWSER_CLERIC_CHANNEL = { choose, resolve, saveDc, wisdomModifier };
})();
