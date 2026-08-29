(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const G = () => window.IRON_PIT_BROWSER_RAGE;
  const NO_CONTROL = { cleanup: () => {}, shouldEscape: () => false, speedIsZero: () => false };
  const H = () => window.IRON_PIT_BROWSER_GRAPPLE || NO_CONTROL;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_DICE;
  const BRAWL_DISTANCE = 5;

  const attacks = (member) => member.state.template.attacks || [];

  function legalAttack(member, distance) {
    const profiles = attacks(member);
    const melee = profiles.find((item) => item.kind === "melee" && distance <= (item.reach || 5));
    if (melee) return melee;
    return profiles.find((item) => item.kind === "ranged" && distance <= item.long) || null;
  }

  function secondWind(sequence, round, member) {
    const state = member.state;
    const uses = state.resources["second-wind"] || 0;
    if (!uses || !state.bonus_action_available || state.current_hp <= 0 || state.current_hp > Math.floor(state.template.max_hp / 2)) return null;
    const die = D().roll(10), total = die + state.template.level, before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, state.current_hp + total);
    state.resources["second-wind"] -= 1; state.bonus_action_available = false;
    return { sequence, round_number: round, event_type: "healing", actor_id: member.combatant_id, actor_name: state.template.name,
      target_id: member.combatant_id, target_name: state.template.name, hp_before: before, hp_after: state.current_hp,
      healing_roll: { notation: `1d10+${state.template.level}`, rolls: [die], modifier: state.template.level, total },
      feature_id: "second-wind", resource_remaining: state.resources["second-wind"], animation: "second-wind",
      description: `${state.template.name} uses Second Wind and regains ${state.current_hp - before} HP.` };
  }

  function adrenaline(sequence, round, member) {
    const state = member.state;
    if (!state.template.traits?.includes("adrenaline-rush") || !state.bonus_action_available || !(state.resources["adrenaline-rush"] > 0)) return null;
    const movement = H().speedIsZero(state) ? 0 : state.template.speed_ft;
    state.resources["adrenaline-rush"] -= 1; state.bonus_action_available = false; state.movement_remaining_ft += movement;
    const pb = 2 + Math.floor((state.template.level - 1) / 4); state.temporary_hp = Math.max(state.temporary_hp, pb);
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id, actor_name: state.template.name,
      feature_id: "adrenaline-rush", resource_remaining: state.resources["adrenaline-rush"], movement_ft: movement,
      animation: "dash", description: `${state.template.name} uses Adrenaline Rush.` };
  }

  function moveEvent(sequence, round, member, target, movement) {
    return { sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, distance_before_ft: movement.before,
      distance_after_ft: movement.after, movement_ft: movement.moved, animation: "advance",
      description: `${member.state.template.name} closes ${movement.moved} feet toward melee.` };
  }

  function closeTurn(sequence, round, member, target) {
    if (S().distance(member, target) <= BRAWL_DISTANCE) return { events: [], sequence, handled: false };
    const charged = C()?.resolveClosing(sequence, round, member, target);
    if (charged?.handled) return charged;
    if (member.state.template.attack_action) return { events: [], sequence, handled: false };

    const events = [];
    const ranged = attacks(member).find((item) => item.kind === "ranged" && S().distance(member, target) <= item.long);
    if (ranged && member.state.action_available) {
      events.push(A().resolveAttack(sequence++, round, member, target, ranged, S().distance(member, target)));
    } else if (member.state.action_available) {
      member.state.action_available = false;
      if (!member.state.active_effect_ids.includes("dodge")) member.state.active_effect_ids.push("dodge");
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: member.state.template.name, feature_id: "dodge", animation: "dodge",
        description: `${member.state.template.name} Dodges while closing to melee.` });
    }
    const movement = S().moveToward(member, target, BRAWL_DISTANCE);
    if (movement) events.push(moveEvent(sequence++, round, member, target, movement));
    return { events, sequence, handled: true };
  }

  function closeAfterAction(sequence, round, member, setup) {
    const target = S().nearestTarget(member, setup);
    if (!target || S().distance(member, target) <= BRAWL_DISTANCE) return { events: [], sequence };
    const movement = S().moveToward(member, target, BRAWL_DISTANCE);
    return movement ? { events: [moveEvent(sequence++, round, member, target, movement)], sequence } : { events: [], sequence };
  }

  function deathSave(sequence, round, member) {
    const state = member.state, natural = D().roll(20); let result = "failure";
    if (natural === 20) { state.current_hp = 1; state.is_alive = true; state.is_unconscious = false; state.is_stable = false; state.death_save_successes = 0; state.death_save_failures = 0; result = "natural 20; regains 1 HP"; }
    else if (natural === 1) { state.death_save_failures = Math.min(3, state.death_save_failures + 2); result = "natural 1; two failures"; }
    else if (natural >= 10) { state.death_save_successes = Math.min(3, state.death_save_successes + 1); result = "success"; }
    else state.death_save_failures = Math.min(3, state.death_save_failures + 1);
    if (state.death_save_failures >= 3) { state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false; result = "third failure; dies"; }
    else if (state.death_save_successes >= 3) { state.is_stable = true; state.is_unconscious = true; state.death_save_successes = 0; state.death_save_failures = 0; result = "third success; becomes Stable"; }
    return { sequence, round_number: round, event_type: "death_save", actor_id: member.combatant_id, actor_name: state.template.name,
      death_save_roll: { notation: "1d20", rolls: [natural], selected_roll: natural, modifier: 0, mode: "normal", total: natural },
      hp_after: state.current_hp, death_save_successes: state.death_save_successes, death_save_failures: state.death_save_failures,
      is_stable: state.is_stable, is_dead: state.is_dead, animation: "death-save", description: `${state.template.name} makes a Death Save: ${result}.` };
  }

  function finalize(events, sequence, round, member) {
    const rage = G()?.finalize(sequence, round, member); if (rage?.event) events.push(rage.event);
    return { events, sequence: rage?.sequence ?? sequence };
  }

  function resolveTurn(sequence, round, member, setup) {
    const events = []; H().cleanup(setup); S().beginTurn(member.state);
    const rage = G()?.enter(sequence, round, member); if (rage) { events.push(rage); sequence += 1; }
    const wind = secondWind(sequence, round, member); if (wind) { events.push(wind); sequence += 1; }
    if (H().shouldEscape(member.state)) { events.push(H().escape(sequence++, round, member)); return finalize(events, sequence, round, member); }
    const rush = adrenaline(sequence, round, member); if (rush) { events.push(rush); sequence += 1; }
    const target = S().nearestTarget(member, setup); if (!target) return finalize(events, sequence, round, member);
    const closing = closeTurn(sequence, round, member, target); events.push(...closing.events); sequence = closing.sequence;
    if (closing.handled) return finalize(events, sequence, round, member);
    const distance = S().distance(member, target);
    const saveAction = member.state.template.saving_throw_actions?.find((action) => V().legalAction(action, target, distance));
    if (saveAction && member.state.action_available) { events.push(V().resolveAction(sequence++, round, member, target, saveAction, distance)); return finalize(events, sequence, round, member); }
    if (member.state.template.attack_action) {
      const multi = M().resolveAttackAction(sequence, round, member, setup); events.push(...multi.events); sequence = multi.sequence;
      const approach = closeAfterAction(sequence, round, member, setup); events.push(...approach.events);
      return finalize(events, approach.sequence, round, member);
    }
    const attack = legalAttack(member, distance);
    if (attack && member.state.action_available) {
      const pack = S().packTactics(member, setup);
      events.push(A().resolveAttack(sequence++, round, member, target, attack, distance, { advantage: pack ? 1 : 0, featureId: pack ? "pack-tactics" : null }));
    }
    return finalize(events, sequence, round, member);
  }

  window.IRON_PIT_BROWSER_TURN = { deathSave, resolveTurn };
})();
