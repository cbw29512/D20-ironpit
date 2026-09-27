(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_CONCENTRATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const SC = () => window.IRON_PIT_BROWSER_SPELLCASTING;

  const members = (setup) => [...(setup?.heroes || []), ...(setup?.monsters || [])];
  const memberById = (setup, id) => members(setup).find((item) => item.combatant_id === id) || null;

  function durationRounds(action, slotLevel) {
    const rows = Object.entries(action.durationRoundsBySlot || {})
      .map(([level, rounds]) => [Number(level), Number(rounds)])
      .filter(([level, rounds]) => Number.isInteger(level) && level <= slotLevel && Number.isInteger(rounds) && rounds > 0);
    if (!rows.length) throw new Error(`${action.name} has no duration rule for slot level ${slotLevel}.`);
    rows.sort((a, b) => b[0] - a[0]);
    return rows[0][1];
  }

  function activeTarget(member, action, setup) {
    const modifier = (member.state.active_modifiers || []).find((item) =>
      item.source_id === member.combatant_id
      && item.source_effect_id === action.id
      && item.concentration_required);
    return memberById(setup, modifier?.target_id || null);
  }

  function legalTarget(member, action, setup) {
    return (F()?.targetOrder(member, setup) || []).find((target) =>
      S().distance(member, target) <= action.range) || null;
  }

  function slot(member, action, turnKey) {
    if (!SC().slotSpellAvailable(member.state, turnKey)) return null;
    const candidates = [];
    for (let level = action.level; level <= 9; level += 1) {
      const id = `spell-slot-${level}`;
      if ((member.state.resources?.[id] || 0) > 0) candidates.push([level, id]);
    }
    return candidates.length ? candidates[0] : null;
  }

  function resolve(sequence, round, member, setup, turnKey) {
    if (!E().available(member.state, "bonus_action")) return null;
    for (const action of member.state.template.targeted_concentration_damage_actions || []) {
      const active = member.state.concentration;
      if (active && active.effect_id !== action.id) continue;

      const prior = active ? activeTarget(member, action, setup) : null;
      if (prior && prior.state.current_hp > 0 && !prior.state.is_dead) continue;
      if (active && !action.retargetAfterTargetZero) continue;

      const target = legalTarget(member, action, setup);
      if (!target) continue;

      const allStates = members(setup).map((item) => item.state);
      let resourceRemaining = null;
      let verb = "moves";
      if (!active) {
        const selected = slot(member, action, turnKey);
        if (!selected) continue;
        const [slotLevel, resourceId] = selected;
        SC().markSlotSpellCast(member.state, turnKey);
        member.state.resources[resourceId] -= 1;
        resourceRemaining = member.state.resources[resourceId];
        C().start(
          member.state, member.combatant_id, action.id, round, allStates,
          round + durationRounds(action, slotLevel), slotLevel,
        );
        verb = "casts";
      } else {
        M().removeSource([member.state], member.combatant_id, action.id, true);
      }

      M().add(member.state, {
        id: `${member.combatant_id}:${action.id}:${target.combatant_id}:0`,
        source_id: member.combatant_id,
        source_effect_id: action.id,
        source_name: action.name,
        source_is_magical: true,
        kind: "bonus-damage",
        flat_bonus: 0,
        minimum_value: 0,
        dice_count: action.diceCount,
        dice_size: action.diceSize,
        damage_type: action.damageType,
        target_id: target.combatant_id,
        concentration_required: true,
      });
      E().spend(member.state, "bonus_action");
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: member.combatant_id,
        actor_name: member.state.template.name,
        target_id: target.combatant_id,
        target_name: target.state.template.name,
        feature_id: action.id,
        resource_remaining: resourceRemaining,
        animation: action.animation || "targeted-concentration",
        description: `${member.state.template.name} ${verb} ${action.name} on ${target.state.template.name}.`,
      };
    }
    return null;
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Targeted concentration damage requires browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "targeted-concentration-damage")) return;
    hooks.registerAbility(phase, {
      id: "targeted-concentration-damage",
      priority: 35,
      rulesets: ["2014", "2024"],
      appliesTo: (member, ctx) =>
        ["afterEscape", "postAction"].includes(ctx.bonusActionCheckpoint)
        && (member.state.template.targeted_concentration_damage_actions || []).length > 0,
      resolve: ({ sequence, round, member, setup, turnKey }) => {
        const event = resolve(sequence, round, member, setup, turnKey);
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TARGETED_CONCENTRATION_DAMAGE = { durationRounds, installAbilityHooks, resolve };
})();
