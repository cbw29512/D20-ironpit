(() => {
  "use strict";
  const S = () => window.IRON_PIT_BROWSER_STATE, C = () => window.IRON_PIT_BROWSER_CHARGE;
  const MA = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const AH = () => window.IRON_PIT_BROWSER_ABILITY_HOOKS;
  const J = () => window.IRON_PIT_BROWSER_ACTION_SURGE, P = () => window.IRON_PIT_BROWSER_SUPPORT;
  const PA = () => window.IRON_PIT_BROWSER_PALADIN_AURAS_2014;
  const O = () => window.IRON_PIT_BROWSER_ONGOING_SPELL_CONTROL;
  const F = () => window.IRON_PIT_BROWSER_FORMATION, OM = () => window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT;
  const E = () => window.IRON_PIT_ACTION_ECONOMY || { available: (s, c) => c === "action" ? s.action_available : s.bonus_action_available };
  const NO_CONTROL = { cleanup: () => {}, shouldEscape: () => false };
  const H = () => window.IRON_PIT_BROWSER_GRAPPLE || NO_CONTROL;

  function enablePitRangePolicy() {
    const rolls = window.IRON_PIT_BROWSER_ROLLS;
    if (!rolls || rolls.fixedFormationActive) return;
    const rawAttackMode = rolls.attackMode;
    rolls.attackMode = (attack, distance, advantage = 0, disadvantage = 0) => rawAttackMode(attack, distance, advantage, disadvantage, false);
    rolls.fixedFormationActive = true;
  }

  function deathSave(sequence, round, member, setup = null) {
    const state = member.state;
    const advantage = Boolean(state.template.death_save_advantage)
      || Boolean(window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.deathSaveAdvantage(state));
    const deathRoll = window.IRON_PIT_BROWSER_ROLLS.d20(0, advantage ? "advantage" : "normal"), natural = deathRoll.selected_roll;
    const recoveryMinimum = state.template.death_save_recovery_minimum || 20;
    const successesBefore = state.death_save_successes, failuresBefore = state.death_save_failures;
    let result = "failure";
    if (natural >= recoveryMinimum) { state.current_hp = 1; state.is_alive = true; state.is_unconscious = false; state.is_stable = false; state.death_save_successes = 0; state.death_save_failures = 0; result = `${natural} triggers death-save recovery; regains 1 HP`; }
    else if (natural === 1) { state.death_save_failures = Math.min(3, state.death_save_failures + 2); result = "natural 1; two failures"; }
    else {
      let succeeded = deathRoll.total >= 10, resolvedRoll = deathRoll;
      if (window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS && setup) {
        const adjusted = window.IRON_PIT_BROWSER_D20_OUTCOME_ADJUSTMENTS.adjust(resolvedRoll, succeeded, 10, member, setup);
        resolvedRoll = adjusted.roll; succeeded = adjusted.succeeded;
      }
      Object.assign(deathRoll, resolvedRoll);
      if (succeeded) { state.death_save_successes = Math.min(3, state.death_save_successes + 1); result = "success"; }
      else state.death_save_failures = Math.min(3, state.death_save_failures + 1);
    }
    if (state.death_save_failures >= 3) result += "; dies";
    if (state.death_save_failures >= 3) { state.is_alive = false; state.is_dead = true; state.is_unconscious = false; state.is_stable = false; }
    else if (state.death_save_successes >= 3) { state.is_stable = true; state.is_unconscious = true; state.death_save_successes = 0; state.death_save_failures = 0; result = "third success; becomes Stable"; }
    return { sequence, round_number: round, event_type: "death_save", actor_id: member.combatant_id, actor_name: state.template.name,
      death_save_roll: deathRoll, hp_after: state.current_hp,
      death_save_successes_before: successesBefore, death_save_failures_before: failuresBefore, death_save_successes: state.death_save_successes,
      death_save_failures: state.death_save_failures, is_stable: state.is_stable, is_dead: state.is_dead, animation: "death-save",
      description: `${state.template.name} makes a Death Save: ${result}.` };
  }

  function finalize(events, sequence, round, member, setup, turnKey, allowSurge = true) {
    const surge = allowSurge ? J()?.resolveAttack(sequence, round, member, setup, turnKey) : null;
    if (surge) { events.push(...surge.events); sequence = surge.sequence; }
    const bonus = resolveBonusActionCheckpoint(sequence, round, member, setup, turnKey, "postAction", events);
    events.push(...bonus.events); sequence = bonus.sequence;
    const hooks = AH();
    const cleanup = hooks.runPhase(hooks.PHASES.TURN_FINALIZE, {
      sequence, round, member, setup, turnKey, turnEvents: [...events], events: [],
    });
    events.push(...cleanup.events); sequence = cleanup.sequence;
    return { events, sequence };
  }

  function resolveBonusActionCheckpoint(sequence, round, member, setup, turnKey, bonusActionCheckpoint, turnEvents = []) {
    const hooks = AH();
    if (!hooks) throw new Error("Browser ability-hook runtime is not loaded.");
    return hooks.runPhase(hooks.PHASES.BONUS_ACTION_WINDOW, {
      sequence, round, member, setup, turnKey, bonusActionCheckpoint, turnEvents, events: [],
    });
  }

  function resolveMainActionOpportunity(profileId, sequence, round, member, setup, turnKey) {
    const selector = MA();
    if (!selector) throw new Error("Browser Main Action selector is not loaded.");
    const context = { sequence, round, member, setup, turnKey };
    const candidates = selector.discoverCandidates(profileId, context);
    const selected = selector.selectCandidate(profileId, candidates);
    return selected ? selector.resolveCandidate(profileId, selected, context) : { events: [], sequence };
  }

  function resolveTurn(sequence, round, member, setup) {
    try {
      enablePitRangePolicy();
      const events = []; H().cleanup(setup); PA()?.sync(setup); S().beginTurn(member.state);
      const turnKey = `${round}:${member.combatant_id}`;
      const hooks = AH();
      if (!hooks) throw new Error("Browser ability-hook runtime is not loaded.");
      const start = hooks.runPhase(hooks.PHASES.TURN_START, {
        sequence, round, member, setup, turnKey, events: [],
      });
      events.push(...start.events); sequence = start.sequence;
      if (O()?.forcedRetreatActive(member.state)) { events.push(O().event(sequence++, round, member)); return finalize(events, sequence, round, member, setup, turnKey, false); }
      const support = P()?.resolve(sequence, round, member, setup, turnKey); if (support) { events.push(...support.events); sequence = support.sequence; }
      let bonus = resolveBonusActionCheckpoint(sequence, round, member, setup, turnKey, "beforeEscape");
      events.push(...bonus.events); sequence = bonus.sequence;
      if (H().shouldEscape(member.state)) { events.push(H().escape(sequence++, round, member, setup)); return finalize(events, sequence, round, member, setup, turnKey); }
      bonus = resolveBonusActionCheckpoint(sequence, round, member, setup, turnKey, "afterEscape");
      events.push(...bonus.events); sequence = bonus.sequence;
      const preMove = resolveMainActionOpportunity("normalPreMove", sequence, round, member, setup, turnKey);
      events.push(...preMove.events); sequence = preMove.sequence;
      if (!E().available(member.state, "action")) return finalize(events, sequence, round, member, setup, turnKey);
      const targets = F().targetOrder(member, setup); if (!targets.length) return finalize(events, sequence, round, member, setup, turnKey);
      const charged = C()?.resolveClosing(sequence, round, member, targets[0], setup);
      if (charged?.handled) { events.push(...charged.events); PA()?.sync(setup); return finalize(events, charged.sequence, round, member, setup, turnKey); }
      const movement = OM()?.move(sequence, round, member, setup, turnKey);
      if (movement) { events.push(...movement.events); sequence = movement.sequence; PA()?.sync(setup); }
      if (!E().available(member.state, "action")) return finalize(events, sequence, round, member, setup, turnKey);
      const postMove = resolveMainActionOpportunity("normalPostMove", sequence, round, member, setup, turnKey);
      events.push(...postMove.events); sequence = postMove.sequence;
      return finalize(events, sequence, round, member, setup, turnKey);
    } catch (error) {
      console.error("Browser turn resolution failed", { combatant: member?.combatant_id, round, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TURN = { deathSave, resolveTurn };
})();
