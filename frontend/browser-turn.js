(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const C = () => window.IRON_PIT_BROWSER_CHARGE;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const G = () => window.IRON_PIT_BROWSER_RAGE;
  const J = () => window.IRON_PIT_BROWSER_ACTION_SURGE;
  const P = () => window.IRON_PIT_BROWSER_SUPPORT;
  const T = () => window.IRON_PIT_BROWSER_TACTICAL_SHIFT;
  const O = () => window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL;
  const L = () => window.IRON_PIT_BROWSER_SPELL_OFFENSE;
  const U = () => window.IRON_PIT_BROWSER_STANDARD_ATTACK_ACTION;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || {
    available: (s, c) => c === "action" ? s.action_available : s.bonus_action_available,
    spend: (s, c) => { if (c === "action") s.action_available = false; else s.bonus_action_available = false; },
  };
  const NO_CONTROL = { cleanup: () => {}, shouldEscape: () => false, speedIsZero: () => false };
  const H = () => window.IRON_PIT_BROWSER_GRAPPLE || NO_CONTROL;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const D = () => window.IRON_PIT_DICE;
  const W = () => window.IRON_PIT_BROWSER_REACTION_MOVEMENT || {
    moveToward: (q, r, m, t, _s, d) => ({ events: [], sequence: q, movement: S().moveToward(m, t, d) }),
  };
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const BRAWL_DISTANCE = 5;
  const attacks = (member) => member.state.template.attacks || [];
  function legalAttack(member, distance) {
    const profiles = attacks(member), melee = profiles.find((a) => a.kind === "melee" && distance <= (a.reach || 5));
    return melee || profiles.find((a) => a.kind === "ranged" && distance <= a.long) || null;
  }
  function reachableMelee(member, distance) {
    if (!(member.state.movement_remaining_ft > 0)) return null;
    return attacks(member).find((a) => a.kind === "melee" && distance > (a.reach || 5) && distance - (a.reach || 5) <= member.state.movement_remaining_ft) || null;
  }
  function moveEvent(sequence, round, member, target, movement) {
    return { sequence, round_number: round, event_type: "movement", actor_id: member.combatant_id, actor_name: member.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name, distance_before_ft: movement.before,
      distance_after_ft: movement.after, movement_ft: movement.moved, animation: "advance",
      description: `${member.state.template.name} closes ${movement.moved} feet toward melee.` };
  }
  function applyMove(sequence, round, member, target, setup, desired, turnKey = null) {
    const moved = W().moveToward(sequence, round, member, target, setup, desired, "speed", { turnKey }), events = [...moved.events];
    sequence = moved.sequence; if (moved.movement) events.push(moveEvent(sequence++, round, member, target, moved.movement));
    return { events, sequence, movement: moved.movement };
  }
  function holdBackline(sequence, round, member, target, setup, turnKey) {
    if (!F()?.backlineHoldsPosition(member, setup)) return null;
    const distance = S().distance(member, target), ranged = attacks(member).find((a) => a.kind === "ranged" && distance <= a.long);
    if (ranged && E().available(member.state, "action")) {
      return { events: [A().resolveAttack(sequence++, round, member, target, ranged, distance, { setup, allowReckless: true, turnKey })], sequence, handled: true };
    }
    if (E().available(member.state, "action")) {
      E().spend(member.state, "action"); if (!member.state.active_effect_ids.includes("dodge")) member.state.active_effect_ids.push("dodge");
      return { events: [{ sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: member.state.template.name, feature_id: "dodge", animation: "dodge",
        description: `${member.state.template.name} Dodges while holding the backline.` }], sequence, handled: true };
    }
    return { events: [], sequence, handled: true };
  }
  function closeTurn(sequence, round, member, target, setup, turnKey) {
    let distance = S().distance(member, target);
    const charged = C()?.resolveClosing(sequence, round, member, target, setup); if (charged?.handled) return charged;
    if (distance <= BRAWL_DISTANCE) return { events: [], sequence, handled: false };
    const held = holdBackline(sequence, round, member, target, setup, turnKey); if (held) return held;
    if (member.state.template.attack_action) return { events: [], sequence, handled: false };
    const melee = reachableMelee(member, distance);
    if (melee) {
      const move = applyMove(sequence, round, member, target, setup, melee.reach || 5, turnKey);
      if (member.state.is_dead || member.state.is_unconscious) return { events: move.events, sequence: move.sequence, handled: true };
      if (move.movement && S().distance(member, target) <= (melee.reach || 5)) return { events: move.events, sequence: move.sequence, handled: false };
    }
    const events = [], canAct = E().available(member.state, "action"); distance = S().distance(member, target);
    const ranged = attacks(member).find((a) => a.kind === "ranged" && distance <= a.long);
    if (ranged && canAct) events.push(A().resolveAttack(sequence++, round, member, target, ranged, distance, { setup, allowReckless: true, turnKey }));
    else if (canAct) {
      E().spend(member.state, "action"); if (!member.state.active_effect_ids.includes("dodge")) member.state.active_effect_ids.push("dodge");
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: member.combatant_id,
        actor_name: member.state.template.name, feature_id: "dodge", animation: "dodge",
        description: `${member.state.template.name} Dodges while closing to melee.` });
    }
    const move = applyMove(sequence, round, member, target, setup, BRAWL_DISTANCE, turnKey); events.push(...move.events);
    return { events, sequence: move.sequence, handled: true };
  }
  function closeAfterAction(sequence, round, member, setup, turnKey) {
    if (F()?.backlineHoldsPosition(member, setup)) return { events: [], sequence };
    const target = S().nearestTarget(member, setup);
    if (!target || S().distance(member, target) <= BRAWL_DISTANCE) return { events: [], sequence };
    const moved = applyMove(sequence, round, member, target, setup, BRAWL_DISTANCE, turnKey);
    return { events: moved.events, sequence: moved.sequence };
  }
  function deathSave(sequence, round, member) {
    const state = member.state, natural = D().roll(20);
    const successesBefore = state.death_save_successes, failuresBefore = state.death_save_failures;
    let result = "failure";
    if (natural === 20) { state.current_hp = 1; state.is_alive = true; state.is_unconscious = false; state.is_stable = false; state.death_save_successes = 0; state.death_save_failures = 0; result = "natural 20; regains 1 HP"; }
    else if (natural === 1) { state.death_save_failures = Math.min(3, state.death_save_failures + 2); result = "natural 1; two failures"; }
    else if (natural >= 10) { state.death_save_successes = Math.min(3, state.death_save_successes + 1); result = "success"; }
    else state.death_save_failures = Math.min(3, state.death_save_failures + 1);
    if (state.death_save_failures >= 3) result += "; dies";
    if (state.death_save_failures >= 3) { state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false; }
    else if (state.death_save_successes >= 3) { state.is_stable = true; state.is_unconscious = true; state.death_save_successes = 0; state.death_save_failures = 0; result = "third success; becomes Stable"; }
    return { sequence, round_number: round, event_type: "death_save", actor_id: member.combatant_id, actor_name: state.template.name,
      death_save_roll: { notation: "1d20", rolls: [natural], selected_roll: natural, modifier: 0, mode: "normal", total: natural },
      hp_after: state.current_hp, death_save_successes_before: successesBefore, death_save_failures_before: failuresBefore,
      death_save_successes: state.death_save_successes, death_save_failures: state.death_save_failures,
      is_stable: state.is_stable, is_dead: state.is_dead, animation: "death-save", description: `${state.template.name} makes a Death Save: ${result}.` };
  }
  function finalize(events, sequence, round, member, setup, turnKey, allowSurge = true) {
    const surge = allowSurge ? J()?.resolveAttack(sequence, round, member, setup, turnKey) : null;
    if (surge) { events.push(...surge.events); sequence = surge.sequence; }
    const rage = G()?.finalize(sequence, round, member); if (rage?.event) events.push(rage.event);
    return { events, sequence: rage?.sequence ?? sequence };
  }
  function resolveTurn(sequence, round, member, setup) {
    const events = []; H().cleanup(setup); S().beginTurn(member.state);
    const turnKey = `${round}:${member.combatant_id}`;
    if (O()?.forcedRetreatActive(member.state)) { events.push(O().event(sequence++, round, member)); return finalize(events, sequence, round, member, setup, turnKey, false); }
    const support = P()?.resolve(sequence, round, member, setup, turnKey); if (support) { events.push(...support.events); sequence = support.sequence; }
    const rage = G()?.enter(sequence, round, member); if (rage) { events.push(rage); sequence += 1; }
    const wind = P()?.secondWind(sequence, round, member);
    if (wind) {
      events.push(wind); sequence += 1;
      const shift = T()?.resolve(sequence, round, member, setup); if (shift) { events.push(shift); sequence += 1; }
    }
    if (H().shouldEscape(member.state)) { events.push(H().escape(sequence++, round, member)); return finalize(events, sequence, round, member, setup, turnKey); }
    const rush = P()?.adrenaline(sequence, round, member); if (rush) { events.push(rush); sequence += 1; }
    const spell = L()?.resolve(sequence, round, member, setup, turnKey); if (spell) { events.push(...spell.events); sequence = spell.sequence; }
    if (!E().available(member.state, "action")) return finalize(events, sequence, round, member, setup, turnKey);
    const target = S().nearestTarget(member, setup); if (!target) return finalize(events, sequence, round, member, setup, turnKey);
    const closing = closeTurn(sequence, round, member, target, setup, turnKey); events.push(...closing.events); sequence = closing.sequence;
    if (member.state.is_dead || member.state.is_unconscious || closing.handled) return finalize(events, sequence, round, member, setup, turnKey);
    const distance = S().distance(member, target);
    if (member.state.template.attack_action) {
      const multi = M().resolveAttackAction(sequence, round, member, setup); events.push(...multi.events); sequence = multi.sequence;
      const approach = closeAfterAction(sequence, round, member, setup, turnKey); events.push(...approach.events);
      return finalize(events, approach.sequence, round, member, setup, turnKey);
    }
    const saveAction = member.state.template.saving_throw_actions?.find((a) => V().legalAction(a, target, distance));
    if (saveAction && E().available(member.state, "action")) { events.push(V().resolveAction(sequence++, round, member, target, saveAction, distance)); return finalize(events, sequence, round, member, setup, turnKey); }
    const attack = legalAttack(member, distance);
    if (attack && E().available(member.state, "action")) {
      const pack = S().packTactics(member, setup), opener = C()?.openingFeature?.(round, member, setup) || null;
      const standard = U().resolve(sequence, round, member, target, attack, distance, setup, turnKey, {
        advantage: pack ? 1 : 0, featureId: opener || (pack ? "pack-tactics" : null),
      });
      events.push(...standard.events); sequence = standard.sequence;
    }
    return finalize(events, sequence, round, member, setup, turnKey);
  }
  window.IRON_PIT_BROWSER_TURN = { deathSave, resolveTurn };
})();
