(() => {
  "use strict";
  const O = () => window.IRON_PIT_BROWSER_ONGOING_DAMAGE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const incapacitated = (state) => state.active_effect_ids?.includes("incapacitated") || state.is_unconscious || state.is_dead;
  const immunityKey = (source, aura) => `${source.combatant_id}:${aura.id}`;

  function eligible(source, subject, aura) {
    if (source.combatant_id === subject.combatant_id) return aura.target_scope === "self" || aura.target_scope === "self-and-allies";
    return source.side === subject.side && (aura.target_scope === "allies" || aura.target_scope === "self-and-allies");
  }
  function advantageSources(subject, setup, key) {
    if (!setup) return 0;
    let total = 0;
    for (const source of members(setup)) {
      if (source.state.is_dead || !source.state.is_alive) continue;
      for (const aura of source.state.template.roll_advantage_auras || []) {
        if (!aura[key] || !eligible(source, subject, aura)) continue;
        if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
        if (S().distance(source, subject) <= aura.radius_ft) total += 1;
      }
    }
    return total;
  }
  const attackAdvantageSources = (subject, setup) => advantageSources(subject, setup, "attack_roll_advantage");
  const savingThrowAdvantageSources = (subject, setup) => advantageSources(subject, setup, "saving_throw_advantage");

  function turnStart(sequence, round, target, setup) {
    const events = [];
    for (const source of members(setup)) {
      if (source.combatant_id === target.combatant_id || source.state.is_dead || !source.state.is_alive) continue;
      for (const aura of source.state.template.start_turn_save_condition_auras || []) {
        if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
        const immunity = immunityKey(source, aura);
        if ((target.state.source_effect_immunities || []).includes(immunity)) continue;
        if (S().distance(source, target) > aura.radius_ft) continue;
        if (aura.requires_source_reaction) {
          if (!E()?.available(source.state, "reaction")) continue;
          E().spend(source.state, "reaction");
        }
        const save = V().resolveSavingThrow(
          target.state, aura.save_ability, aura.dc, Boolean(aura.magical_effect), savingThrowAdvantageSources(target, setup),
        );
        const applied = [];
        if (save.succeeded && aura.success_grants_source_immunity) {
          target.state.source_effect_immunities.push(immunity);
        } else if (!save.succeeded) {
          const condition = T().apply(target.state, aura.condition, source.combatant_id, {
            sourceEffectId: aura.id, appliedRound: round, expiryTiming: aura.expiry_timing,
          });
          if (condition) applied.push(condition);
        }
        events.push({
          sequence: sequence++, round_number: round, event_type: "saving_throw",
          actor_id: source.combatant_id, actor_name: source.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          saving_throw_roll: save.roll, save_ability: aura.save_ability, save_dc: aura.dc,
          save_succeeded: save.succeeded, applied_condition_ids: applied, feature_id: aura.id,
          animation: "aura-condition", description: `${target.state.template.name} ${save.succeeded ? "SUCCEEDS" : "FAILS"} a DC ${aura.dc} ${aura.save_ability} save against ${source.state.template.name}'s ${aura.name}.`,
        });
      }
    }
    return { events, sequence };
  }

  function grappleTurnStart(sequence, round, source, setup) {
    try {
      const events = [], profile = source.state.template.start_turn_grapple_contact_damage;
      if (!profile || source.state.is_dead || !source.state.is_alive) return { events, sequence };
      const all = members(setup), byId = new Map(all.map((member) => [member.combatant_id, member]));
      const ids = new Set((source.state.grapple_sources || []).map((item) => item.source_id).filter((id) => byId.has(id)));
      for (const member of all) {
        if (member.combatant_id === source.combatant_id) continue;
        if ((member.state.grapple_sources || []).some((item) => item.source_id === source.combatant_id)) ids.add(member.combatant_id);
      }
      for (const id of [...ids].sort()) {
        const target = byId.get(id);
        if (!target || target.state.is_dead || !target.state.is_alive) continue;
        events.push(O().resolve(sequence++, round, source, target, setup, {
          featureId: profile.id, featureName: profile.name,
          diceCount: profile.damage_dice_count, diceSize: profile.damage_dice_size,
          damageBonus: profile.damage_bonus || 0, damageType: profile.damage_type,
          animation: "grapple-contact-damage",
        }));
      }
      return { events, sequence };
    } catch (error) {
      console.error("Failed browser grapple-contact damage resolution.", { source: source?.combatant_id, error });
      throw error;
    }
  }

  function turnEnd(sequence, round, source, setup) {
    const events = [];
    if (source.state.is_dead || !source.state.is_alive) return { events, sequence };
    for (const aura of source.state.template.end_turn_damage_auras || []) {
      if (aura.disabled_while_incapacitated && incapacitated(source.state)) continue;
      const targets = members(setup).filter((member) =>
        member.side !== source.side && member.state.is_alive && !member.state.is_dead && S().distance(source, member) <= aura.radius_ft
      );
      for (const target of targets) {
        const event = O().resolve(sequence++, round, source, target, setup, {
          featureId: aura.id, featureName: aura.name, diceCount: aura.damage_dice_count,
          diceSize: aura.damage_dice_size, damageBonus: aura.damage_bonus || 0,
          damageType: aura.damage_type, animation: "aura-damage",
        });
        if (aura.applies_burning && target.state.is_alive && !target.state.is_dead) {
          const effectId = "burn" + "ing";
          const exists = (target.state.timed_effects || []).some((effect) => effect.effect_id === effectId);
          const applied = exists ? effectId : T().apply(target.state, effectId, source.combatant_id, {
            sourceEffectId: aura.id, appliedRound: round,
            periodicDamage: { timing: "target_turn_end", diceCount: 1, diceSize: 6, damageBonus: 0, damageType: "fire" },
          });
          if (applied && !(event.applied_condition_ids || []).includes(applied)) {
            event.applied_condition_ids ||= [];
            event.applied_condition_ids.push(applied);
          }
        }
        events.push(event);
      }
    }
    return { events, sequence };
  }

  window.IRON_PIT_BROWSER_AURAS = { attackAdvantageSources, grappleTurnStart, savingThrowAdvantageSources, turnEnd, turnStart };
})();
