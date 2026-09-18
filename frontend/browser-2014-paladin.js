(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TURN_CREATURE_EFFECTS;
  const D = () => window.IRON_PIT_DICE;
  const CHANNEL = "channel-divinity", SACRED = "sacred-weapon", TURN = "turn-the-unholy", TURNED = "turned-unholy";

  const baseType = (state) => String(state.template.creature_type || "").split(" (")[0].toLowerCase();
  const proficiency = (level) => 2 + Math.floor((level - 1) / 4);
  const modifier = (score) => Math.floor((score - 10) / 2);
  const saveDc = (member) => 8 + proficiency(member.state.template.level)
    + modifier(member.state.template.ability_scores.charisma);

  function primaryAttack(member) {
    const id = member.state.template.primary_attack_id;
    const attack = (member.state.template.attacks || []).find((item) => item.id === id)
      || (member.state.template.attacks || [])[0];
    if (!attack) throw new Error("Sacred Weapon requires a primary weapon attack.");
    return attack;
  }

  function sacredActive(member) {
    return (member.state.active_modifiers || []).some((item) => item.source_effect_id === SACRED);
  }

  function resolveSacredWeapon(sequence, round, member) {
    const bonus = member.state.template.sacred_weapon_2014_bonus || 0;
    if (!bonus || sacredActive(member) || !E().available(member.state, "action")
        || !(member.state.resources[CHANNEL] > 0)) return null;
    const attack = primaryAttack(member), weaponId = attack.weaponId || attack.id;
    E().spend(member.state, "action"); member.state.resources[CHANNEL] -= 1;
    M().add(member.state, {
      id: `${member.combatant_id}:${SACRED}`, source_id: member.combatant_id, source_effect_id: SACRED,
      kind: "attack-roll-flat", flat_bonus: bonus, weapon_id: weaponId,
      expires_source_turn_end_round: round + 10,
    });
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id,
      actor_name: member.state.template.name, feature_id: SACRED, resource_remaining: member.state.resources[CHANNEL],
      animation: "bless", description: `${member.state.template.name} uses Sacred Weapon, gaining +${bonus} to ${attack.name} attack rolls.` };
  }

  function unholyTargets(member, setup) {
    const enemies = member.side === "heroes" ? setup.monsters : setup.heroes;
    return enemies.filter((target) => target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0
      && S().distance(member, target) <= 30 && ["fiend", "undead"].includes(baseType(target.state)));
  }

  function resolveTurnUnholy(sequence, round, member, setup, targets) {
    if (!targets.length || !E().available(member.state, "action") || !(member.state.resources[CHANNEL] > 0)) {
      return { events: [], sequence };
    }
    const legal = new Set(unholyTargets(member, setup).map((target) => target.combatant_id));
    if (targets.some((target) => !legal.has(target.combatant_id))) throw new Error("Turn the Unholy received an illegal target.");
    E().spend(member.state, "action"); member.state.resources[CHANNEL] -= 1;
    return T().resolve(
      sequence, round, member, targets, saveDc(member), TURN, TURNED,
      member.state.resources[CHANNEL], "Turn the Unholy",
    );
  }

  function resolveChannel(sequence, round, member, setup) {
    if (!member.state.template.turn_unholy_2014) return { events: [], sequence };
    const targets = unholyTargets(member, setup);
    if (targets.length) return resolveTurnUnholy(sequence, round, member, setup, targets);
    const sacred = resolveSacredWeapon(sequence, round, member);
    return sacred ? { events: [sacred], sequence: sequence + 1 } : { events: [], sequence };
  }

  function divineSmiteComponent(attacker, defender, attack, critical) {
    if (!attacker.template.divine_smite_2014 || attack.kind !== "melee") return null;
    const levels = Object.entries(attacker.resources || {})
      .filter(([id, uses]) => id.startsWith("spell-slot-") && uses > 0)
      .map(([id]) => Number.parseInt(id.slice("spell-slot-".length), 10))
      .filter(Number.isInteger);
    if (!levels.length) return null;
    const slot = Math.max(...levels); attacker.resources[`spell-slot-${slot}`] -= 1;
    let diceCount = Math.min(5, slot + 1);
    if (["undead", "fiend"].includes(baseType(defender))) diceCount += 1;
    const count = diceCount * (critical ? 2 : 1), rolls = D().rollMany(count, 8);
    return { source: "Divine Smite", damage_type: "radiant", notation: `${count}d8+0`, rolls, modifier: 0,
      total: rolls.reduce((sum, roll) => sum + roll, 0) };
  }

  window.IRON_PIT_BROWSER_PALADIN_2014 = {
    divineSmiteComponent, resolveChannel, resolveSacredWeapon, resolveTurnUnholy, saveDc, unholyTargets,
  };
})();
