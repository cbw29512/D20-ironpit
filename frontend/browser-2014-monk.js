(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const D = () => window.IRON_PIT_DICE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const I = () => window.IRON_PIT_BROWSER_CONDITION_IMMUNITY || { immune: () => false };
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const T = () => window.IRON_PIT_BROWSER_TIMED;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const mod = (score) => Math.floor((score - 10) / 2);
  const proficiency = (level) => 2 + Math.floor((level - 1) / 4);
  const monkDc = (state) => 8 + proficiency(state.template.level) + mod(state.template.ability_scores.wisdom);

  function applyDeflectMissiles(defender, attack, components) {
    try {
      if (!defender.template.deflect_missiles || attack.kind !== "ranged" || !E().available(defender, "reaction") || defender.current_hp <= 0) {
        return { components, used: false, reduction: 0 };
      }
      const reduction = D().roll(10) + mod(defender.template.ability_scores.dexterity) + defender.template.level;
      E().spend(defender, "reaction");
      let remaining = reduction;
      const reduced = components.map((part) => {
        const amount = Math.min(part.total, remaining); remaining -= amount;
        return { ...part, total: part.total - amount };
      });
      return { components: reduced, used: true, reduction };
    } catch (error) {
      console.error("Browser Deflect Missiles failed", { defender: defender?.template?.name, error });
      throw error;
    }
  }

  function resolveStunning(sequence, round, actor, target, attack) {
    try {
      const state = actor.state, ki = state.resources.ki || 0;
      if (state.template.ruleset !== "2014" || !state.template.stunning_strike || attack.kind !== "melee"
          || target.state.current_hp <= 0 || target.state.active_effect_ids.includes("stunned") || ki <= 0) return null;
      state.resources.ki -= 1;
      const dc = monkDc(state), save = V().resolveSavingThrow(target.state, "constitution", dc);
      const applied = [];
      if (!save.succeeded) {
        const condition = T().apply(target.state, "stunned", actor.combatant_id, {
          sourceEffectId: "stunning-strike", appliedRound: round, expiresRound: round + 1,
          expiryTiming: "source_turn_end", useDefaultPoisonRecovery: false,
        });
        if (condition) applied.push(condition);
      }
      return { sequence, round_number: round, event_type: "feature", actor_id: actor.combatant_id,
        actor_name: state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "constitution", save_dc: dc, save_succeeded: save.succeeded,
        applied_condition_ids: applied, feature_id: "stunning-strike", resource_remaining: state.resources.ki,
        animation: "stun", description: `${state.template.name} spends 1 Ki on Stunning Strike; ${target.state.template.name} ${save.succeeded ? "resists" : "is Stunned"}.` };
    } catch (error) { console.error("Browser Stunning Strike failed", { actor: actor?.combatant_id, error }); throw error; }
  }

  function resolveOpenHand(sequence, round, actor, target) {
    try {
      if (!actor.state.template.open_hand_technique || target.state.current_hp <= 0
          || target.state.active_effect_ids.includes("prone") || I().immune(target.state, "prone")) return null;
      const dc = monkDc(actor.state), save = V().resolveSavingThrow(target.state, "dexterity", dc), applied = [];
      if (!save.succeeded) { target.state.active_effect_ids.push("prone"); applied.push("prone"); }
      return { sequence, round_number: round, event_type: "feature", actor_id: actor.combatant_id,
        actor_name: actor.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        saving_throw_roll: save.roll, save_ability: "dexterity", save_dc: dc, save_succeeded: save.succeeded,
        applied_condition_ids: applied, feature_id: "open-hand-technique", animation: "prone",
        description: `${actor.state.template.name} uses Open Hand Technique; ${target.state.template.name} ${save.succeeded ? "keeps footing" : "falls Prone"}.` };
    } catch (error) { console.error("Browser Open Hand Technique failed", { actor: actor?.combatant_id, error }); throw error; }
  }

  function resolveBonus(sequence, round, actor, setup, turnKey, turnEvents) {
    try {
      const state = actor.state, template = state.template;
      const qualified = turnEvents.some((event) => event.event_type === "attack" && event.actor_id === actor.combatant_id
        && ["unarmed-strike", "shortsword"].includes(event.weapon_id));
      if (template.ruleset !== "2014" || !template.martial_arts_bonus_attack || !qualified || !E().available(state, "bonus_action")) return null;
      const attack = template.attacks.find((item) => item.weaponId === "unarmed-strike");
      if (!attack) throw new Error("Certified Monk lacks an unarmed strike.");
      const targets = () => F().targetOrder(actor, setup).filter((target) => S().distance(actor, target) <= attack.reach);
      if (!targets().length) return null;
      const flurry = template.flurry_of_blows && (state.resources.ki || 0) > 0;
      if (flurry) state.resources.ki -= 1;
      E().spend(state, "bonus_action");
      const events = [], strikes = flurry ? 2 : 1, featureId = flurry ? "flurry-of-blows" : "martial-arts";
      for (let index = 0; index < strikes && targets().length && !state.turn_terminated; index += 1) {
        const target = targets()[0];
        const event = A().resolveAttack(sequence++, round, actor, target, attack, S().distance(actor, target),
          { spendAction: false, setup, featureId, turnKey, ignoreCloseThreat: true });
        events.push(event); if (!event.hit) continue;
        const stun = resolveStunning(sequence, round, actor, target, attack); if (stun) { events.push(stun); sequence += 1; }
        if (flurry) { const open = resolveOpenHand(sequence, round, actor, target); if (open) { events.push(open); sequence += 1; } }
      }
      return { events, sequence };
    } catch (error) { console.error("Browser Monk bonus attacks failed", { actor: actor?.combatant_id, error }); throw error; }
  }

  window.IRON_PIT_BROWSER_MONK_2014 = { applyDeflectMissiles, monkDc, resolveBonus, resolveOpenHand, resolveStunning };
})();
