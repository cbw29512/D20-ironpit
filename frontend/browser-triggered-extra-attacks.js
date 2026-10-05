(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const X = () => window.IRON_PIT_BROWSER_EXHAUSTION;

  const bloodied = (member) => member.state.current_hp > 0
    && member.state.current_hp * 2 <= member.state.template.max_hp;

  function maybeAddStack(member, rule) {
    const state = member.state;
    state.triggered_extra_attack_stack_counts ||= {};
    state.source_owned_exhaustion_levels ||= {};
    state.feature_use_counts ||= {};
    const stacks = state.triggered_extra_attack_stack_counts[rule.sourceId] || 0;
    const uses = state.feature_use_counts[rule.sourceId] || 0;
    if (stacks >= rule.maxStacks || uses >= rule.maxUses) return false;
    if (rule.requiresBloodied && !bloodied(member)) return false;
    const taken = state.damage_taken_this_turn_by_type?.[rule.triggerDamageType] || 0;
    if (taken < rule.triggerDamageMinimum) return false;
    state.triggered_extra_attack_stack_counts[rule.sourceId] = stacks + 1;
    state.feature_use_counts[rule.sourceId] = uses + 1;
    if (rule.exhaustionPerStack) {
      if (!X()) throw new Error("Triggered extra attacks require browser-exhaustion.js.");
      X().gain(state, rule.exhaustionPerStack);
      state.source_owned_exhaustion_levels[rule.sourceId] =
        (state.source_owned_exhaustion_levels[rule.sourceId] || 0) + rule.exhaustionPerStack;
    }
    return true;
  }

  function target(member, setup, attack) {
    const candidate = S().nearestTarget(member, setup);
    if (!candidate) return null;
    const distance = S().distance(member, candidate);
    if (attack.kind === "melee" && distance > (attack.reach || 5)) return null;
    if (attack.kind === "ranged" && distance > (attack.long || attack.normal || 0)) return null;
    return { candidate, distance };
  }

  function resolveAfterTurn(sequence, round, justActed, setup) {
    try {
      const events = [];
      const combatants = [...(setup.heroes || []), ...(setup.monsters || [])];
      for (const owner of combatants) {
        for (const rule of owner.state.template.triggered_extra_attack_stacks || []) {
          if (!maybeAddStack(owner, rule)) continue;
          const stacks = owner.state.triggered_extra_attack_stack_counts?.[rule.sourceId] || 0;
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: owner.combatant_id, actor_name: owner.state.template.name,
            feature_id: rule.sourceId, animation: "feature",
            description: `${owner.state.template.name} gains one ${rule.sourceName} stack (${stacks}/${rule.maxStacks}).`,
          });
        }
      }
      for (const rule of justActed.state.template.triggered_extra_attack_stacks || []) {
        const stacks = justActed.state.triggered_extra_attack_stack_counts?.[rule.sourceId] || 0;
        for (let i = 0; i < stacks; i += 1) {
          if (justActed.state.is_dead) break;
          const chosen = target(justActed, setup, rule.attack);
          if (!chosen) break;
          if (!A()?.resolveAttack) throw new Error("Triggered extra attacks require browser-attack.js.");
          const event = A().resolveAttack(
            sequence++, round, justActed, chosen.candidate, rule.attack, chosen.distance,
            {
              spendAction: false,
              offTurn: true,
              setup,
              turnKey: `${round}:${justActed.combatant_id}:post-turn`,
            },
          );
          event.feature_id = rule.sourceId;
          event.description += ` ${rule.sourceName} makes its attached extra attack.`;
          events.push(event);
        }
      }
      return { events, sequence };
    } catch (error) {
      console.error("Triggered post-turn extra attacks failed.", { combatant: justActed?.combatant_id, error });
      throw error;
    }
  }

  function clearTurnDamage(setup) {
    try {
      for (const member of [...(setup.heroes || []), ...(setup.monsters || [])]) {
        member.state.damage_taken_this_turn_by_type = {};
      }
    } catch (error) {
      console.error("Failed to clear browser per-turn typed damage state.", { error });
      throw error;
    }
  }

  function clearRegenerationOwnedStacks(state) {
    const cleared = [];
    for (const rule of state.template.triggered_extra_attack_stacks || []) {
      if (!rule.clearsOnRegenerationHeal) continue;
      const stacks = state.triggered_extra_attack_stack_counts?.[rule.sourceId] || 0;
      const owned = state.source_owned_exhaustion_levels?.[rule.sourceId] || 0;
      if (state.triggered_extra_attack_stack_counts) delete state.triggered_extra_attack_stack_counts[rule.sourceId];
      if (state.source_owned_exhaustion_levels) delete state.source_owned_exhaustion_levels[rule.sourceId];
      if (owned) {
        if (!X()) throw new Error("Triggered extra attacks require browser-exhaustion.js.");
        X().reduce(state, owned);
      }
      if (stacks) cleared.push({ sourceName: rule.sourceName, stacks });
    }
    return cleared;
  }

  window.IRON_PIT_BROWSER_TRIGGERED_EXTRA_ATTACKS = { clearRegenerationOwnedStacks, clearTurnDamage, resolveAfterTurn };
})();
