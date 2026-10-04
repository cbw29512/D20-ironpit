(() => {
  "use strict";

  const RESOURCE_ID = "legendary-actions";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const C = () => window.IRON_PIT_BROWSER_ABILITY_CHECK_ESCAPE;
  const P = () => window.IRON_PIT_BROWSER_LEGENDARY_ACTION_CHOICE;

  function restoreHp(state, amount) {
    if (H()?.restore) return H().restore(state, amount);
    if (state.is_dead || amount <= 0) return 0;
    const before = state.current_hp;
    const maximum = S()?.effectiveMaxHp ? S().effectiveMaxHp(state) : state.template.max_hp;
    state.current_hp = Math.min(maximum, before + amount);
    return state.current_hp - before;
  }

  function choose(actor, setup) {
    return P().choose(actor, setup);
  }

  function resolveAfterTurn(sequence, round, justActed, setup) {
    try {
      const events = [];
      const others = [...(setup.heroes || []), ...(setup.monsters || [])]
        .filter((item) => item.combatant_id !== justActed.combatant_id);
      for (const actor of others) {
        const choice = choose(actor, setup);
        if (!choice) continue;
        actor.state.resources[RESOURCE_ID] = (actor.state.resources[RESOURCE_ID] || 0) - (choice.option.cost || 1);
        const prefix = `${actor.state.template.name} uses Legendary Action: ${choice.option.name}.`;
        if (choice.kind === "attack") {
          const event = A().resolveAttack(
            sequence, round, actor, choice.target, choice.attack,
            S().distance(actor, choice.target),
            { spendAction: false, setup, featureId: choice.option.id },
          );
          events.push({ ...event, description: `${prefix} ${event.description || ""}`.trim() });
          sequence += 1;
          continue;
        }
        if (choice.kind === "save") {
          const shared = choice.action.damageDiceCount
            ? window.IRON_PIT_DICE.rollMany(choice.action.damageDiceCount, choice.action.damageDiceSize)
            : null;
          for (const id of choice.targetIds) {
            const target = [...(setup.heroes || []), ...(setup.monsters || [])]
              .find((item) => item.combatant_id === id);
            if (!target) throw new Error(`Unknown legendary save target ${id}.`);
            const event = V().resolveAction(sequence, round, actor, target, choice.action, 0, {
              spendAction: false, checkResource: false, spendResource: false,
              sharedDamageRolls: shared, setup,
            });
            events.push({
              ...event, feature_id: choice.option.id,
              description: `${prefix} ${event.description || ""}`.trim(),
            });
            sequence += 1;
          }
          continue;
        }
        if (choice.kind === "heal") {
          const spec = choice.spec;
          const count = spec.dice_count ?? spec.diceCount ?? 0;
          const size = spec.dice_size ?? spec.diceSize ?? 8;
          const bonus = spec.healing_bonus ?? spec.healingBonus ?? 0;
          const rolls = count ? window.IRON_PIT_DICE.rollMany(count, size) : [];
          const total = rolls.reduce((sum, value) => sum + value, 0) + bonus;
          const before = actor.state.current_hp;
          const healed = restoreHp(actor.state, total);
          events.push({
            sequence, round_number: round, event_type: "healing",
            actor_id: actor.combatant_id, actor_name: actor.state.template.name,
            target_id: actor.combatant_id, target_name: actor.state.template.name,
            healing_roll: { notation: `${count}d${size}+${bonus}`, rolls, modifier: bonus, total },
            hp_before: before, hp_after: actor.state.current_hp,
            feature_id: choice.option.id, animation: "healing",
            description: `${prefix} ${actor.state.template.name} regains ${healed} HP.`,
          });
          sequence += 1;
          continue;
        }
        if (choice.kind === "ac_buff") {
          const bonus = choice.spec.ac_bonus ?? choice.spec.acBonus;
          if (!M()) throw new Error("Legendary AC buff requires browser-modifiers.js.");
          M().add(choice.target.state, {
            id: `${actor.combatant_id}:${choice.option.id}:${choice.target.combatant_id}`,
            source_id: actor.combatant_id, source_effect_id: choice.option.id,
            source_name: choice.option.name, source_is_magical: true,
            kind: "armor-class", flat_bonus: bonus, expires_source_turn_end_round: round,
          });
          events.push({
            sequence, round_number: round, event_type: "feature",
            actor_id: actor.combatant_id, actor_name: actor.state.template.name,
            target_id: choice.target.combatant_id, target_name: choice.target.state.template.name,
            feature_id: choice.option.id, animation: "buff",
            description: `${prefix} ${choice.target.state.template.name} gains +${bonus} AC until the end of ${actor.state.template.name}'s next turn.`,
          });
          sequence += 1;
          continue;
        }
        if (choice.kind === "check") {
          const ability = choice.ability;
          const bonus = C()?.abilityCheckBonus ? C().abilityCheckBonus(actor.state, ability) : 0;
          events.push({
            sequence, round_number: round, event_type: "feature",
            actor_id: actor.combatant_id, actor_name: actor.state.template.name,
            ability_check_roll: window.IRON_PIT_BROWSER_ROLLS.d20(bonus, "normal"),
            check_ability: ability, feature_id: choice.option.id, animation: "check",
            description: `${prefix} ${actor.state.template.name} makes a ${ability} check.`,
          });
          sequence += 1;
          continue;
        }
        throw new Error(`${actor.state.template.name} legendary action ${choice.option.id} uses unsupported kind ${choice.kind}.`);
      }
      return { events, sequence };
    } catch (error) {
      console.error("Legendary actions after turn failed.", { combatant: justActed?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_LEGENDARY_ACTIONS = { choose, resolveAfterTurn };
})();
