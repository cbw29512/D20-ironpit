(() => {
  "use strict";

  const H = () => window.IRON_PIT_BROWSER_HEALING;
  const C = () => window.IRON_PIT_BROWSER_CONDITION_REMOVAL;
  const K = () => window.IRON_PIT_BROWSER_CLERIC_CHANNEL;
  const AT = () => window.IRON_PIT_BROWSER_ATTACHMENTS;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const D = () => window.IRON_PIT_DICE;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;

  function resolve(sequence, round, member, setup, turnKey) {
    const events = [];
    const detach = AT()?.detachAction(sequence, round, member, setup);
    if (detach) { events.push(detach); sequence += 1; return { events, sequence }; }
    let healing = H()?.chooseAction(member, setup, turnKey);
    if (healing?.target.state.current_hp === 0) events.push(H().resolve(sequence++, round, member, healing.target, healing.action, turnKey));
    const removal = C()?.chooseAction(member, setup, turnKey);
    if (removal) events.push(C().resolve(sequence++, round, member, removal.target, removal.action, removal.conditions, turnKey));
    healing = H()?.chooseAction(member, setup, turnKey);
    if (healing) events.push(H().resolve(sequence++, round, member, healing.target, healing.action, turnKey));
    const channel = K()?.resolve(sequence, round, member, setup);
    if (channel) { events.push(...channel.events); sequence = channel.sequence; }
    return { events, sequence };
  }

  function combatSupport(sequence, round, member) {
    try {
      const action = (member.state.template.support_actions || []).find((item) =>
        E().available(member.state, item.actionCost || "action")
        && R().available(member.state, item.resourceId, item.resourceCost || 1)
      );
      if (!action) return null;
      const target = member, before = target.state.temporary_hp;
      const rolls = Array.from(
        { length: action.temporaryHpDiceCount || 0 },
        () => D().roll(action.temporaryHpDiceSize || 6),
      );
      const amount = Math.max(
        0,
        rolls.reduce((sum, value) => sum + value, 0) + (action.temporaryHpBonus || 0),
      );
      S().grantTemporaryHp(target.state, amount);
      if (action.attackRollAdvantageUntilSourceTurnStart) {
        M().add(target.state, {
          id: `${member.combatant_id}:${action.id}:${target.combatant_id}:attack-advantage`,
          source_id: member.combatant_id,
          source_effect_id: action.id,
          kind: "attack-roll-advantage",
          flat_bonus: 0,
          dice_count: 0,
          dice_size: 0,
          damage_type: null,
          target_id: target.combatant_id,
          concentration_required: false,
          consume_on_attack_against: false,
          expires_at_start_of_source_turn: true,
          expires_at_end_of_target_turn: false,
          expires_source_turn_end_round: null,
          expires_current_turn_end_owner_id: null,
          expires_current_turn_end_round: null,
        });
      }
      E().spend(member.state, action.actionCost || "action");
      const remaining = R().spend(member.state, action.resourceId, action.resourceCost || 1);
      return {
        sequence, round_number: round, event_type: "feature",
        actor_id: member.combatant_id, actor_name: member.state.template.name,
        target_id: target.combatant_id, target_name: target.state.template.name,
        temporary_hp_before: before, temporary_hp_after: target.state.temporary_hp,
        feature_id: action.id, resource_remaining: remaining,
        animation: action.animation || "support",
        description: `${member.state.template.name} uses ${action.name}; ${target.state.template.name} has ${target.state.temporary_hp} Temporary HP and Advantage on attack rolls until the source's next turn.`,
      };
    } catch (error) {
      console.error("Browser combat support action failed.", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function secondWind(sequence, round, member) {
    const state = member.state, uses = state.resources["second-wind"] || 0;
    if (!uses || !E().available(state, "bonus_action") || state.current_hp <= 0 || state.current_hp > Math.floor(state.template.max_hp / 2)) return null;
    const die = D().roll(10), total = die + state.template.level, before = state.current_hp;
    state.current_hp = Math.min(state.template.max_hp, state.current_hp + total);
    state.resources["second-wind"] -= 1; E().spend(state, "bonus_action");
    return { sequence, round_number: round, event_type: "healing", actor_id: member.combatant_id, actor_name: state.template.name,
      target_id: member.combatant_id, target_name: state.template.name, hp_before: before, hp_after: state.current_hp,
      healing_roll: { notation: `1d10+${state.template.level}`, rolls: [die], modifier: state.template.level, total },
      feature_id: "second-wind", resource_remaining: state.resources["second-wind"], animation: "second-wind",
      description: `${state.template.name} uses Second Wind and regains ${state.current_hp - before} HP.` };
  }

  function adrenaline(sequence, round, member) {
    const state = member.state, pb = 2 + Math.floor((state.template.level - 1) / 4);
    if (!state.template.traits?.includes("adrenaline-rush") || !E().available(state, "bonus_action") || !(state.resources["adrenaline-rush"] > 0) || state.temporary_hp >= pb) return null;
    state.resources["adrenaline-rush"] -= 1; E().spend(state, "bonus_action"); S().grantTemporaryHp(state, pb);
    return { sequence, round_number: round, event_type: "feature", actor_id: member.combatant_id, actor_name: state.template.name,
      feature_id: "adrenaline-rush", resource_remaining: state.resources["adrenaline-rush"], movement_ft: 0,
      animation: "dash", description: `${state.template.name} uses Adrenaline Rush; Dash movement is abstracted by fixed Pit formation.` };
  }

  window.IRON_PIT_BROWSER_SUPPORT = { adrenaline, combatSupport, resolve, secondWind };
})();