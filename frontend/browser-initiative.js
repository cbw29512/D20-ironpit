(() => {
  "use strict";

  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const Q = () => window.IRON_PIT_BROWSER_CONDITION_RULES || { incapacitated: (state) => state.is_unconscious };

  function priority(group) {
    if (group.natural_roll === 20) return 2;
    if (group.natural_roll === 1) return 0;
    return 1;
  }

  function rerollExactTies(groups) {
    while (true) {
      const signatures = new Map();
      for (const group of groups) {
        const key = `${priority(group)}:${group.initiative_count}:${group.tie_break_rolls.join(",")}`;
        const tied = signatures.get(key) || [];
        tied.push(group);
        signatures.set(key, tied);
      }
      const unresolved = [...signatures.values()].filter((tied) => tied.length > 1);
      if (!unresolved.length) return;
      for (const tied of unresolved) {
        for (const group of tied) {
          const value = window.IRON_PIT_DICE.roll(20);
          group.tie_break_rolls.push(value);
          group.tie_break_roll = value;
        }
      }
    }
  }

  function compareTieHistory(left, right) {
    const length = Math.max(left.length, right.length);
    for (let index = 0; index < length; index += 1) {
      const a = left[index] || 0, b = right[index] || 0;
      if (a !== b) return b - a;
    }
    return 0;
  }

  function resolve(setup) {
    const groups = setup.heroes.map((member, index) => ({
      side: "heroes", template_id: member.state.template.id, members: [member], index,
    }));
    const byTemplate = new Map();
    setup.monsters.forEach((member, index) => {
      const key = member.state.template.id;
      if (!byTemplate.has(key)) byTemplate.set(key, {
        side: "monsters", template_id: key, members: [], index: setup.heroes.length + index,
      });
      byTemplate.get(key).members.push(member);
    });
    groups.push(...byTemplate.values());
    for (const group of groups) {
      const state = group.members[0].state;
      const advantage = Boolean(state.template.initiative_advantage), disadvantage = Q().incapacitated(state);
      const mode = advantage === disadvantage ? "normal" : advantage ? "advantage" : "disadvantage";
      const roll = R().d20(state.template.initiative_bonus, mode);
      group.initiative_roll = roll;
      group.natural_roll = roll.selected_roll;
      group.initiative_bonus = state.template.initiative_bonus;
      group.initiative_count = roll.total;
      group.tie_break_roll = null;
      group.tie_break_rolls = [];
      group.members.forEach((member) => {
        member.state.initiative_roll = roll.selected_roll;
        member.state.initiative_total = roll.total;
      });
    }
    rerollExactTies(groups);
    groups.sort((a, b) => priority(b) - priority(a)
      || b.initiative_count - a.initiative_count
      || compareTieHistory(a.tie_break_rolls, b.tie_break_rolls)
      || a.index - b.index);
    return {
      groups: groups.map((group) => ({
        side: group.side, template_id: group.template_id,
        combatant_ids: group.members.map((member) => member.combatant_id),
        initiative_roll: group.initiative_roll, natural_roll: group.natural_roll,
        initiative_bonus: group.initiative_bonus, initiative_count: group.initiative_count,
        tie_break_roll: group.tie_break_roll, tie_break_rolls: [...group.tie_break_rolls],
      })),
      turn_order: groups.flatMap((group) => group.members.map((member) => member.combatant_id)),
    };
  }

  function events(initiative, setup, startSequence = 1) {
    const members = [...setup.heroes, ...setup.monsters];
    const names = new Map(members.map((member) => [member.combatant_id, member.state.template.name]));
    let sequence = startSequence;
    return initiative.groups.map((group) => {
      const name = names.get(group.combatant_ids[0]);
      let description = `${name}${group.combatant_ids.length > 1 ? ` group (${group.combatant_ids.length})` : ""} rolls initiative ${group.initiative_count}.`;
      if (group.natural_roll === 20) description += " Natural 20: top initiative priority.";
      else if (group.natural_roll === 1) description += " Natural 1: bottom initiative priority.";
      if (group.tie_break_rolls.length) description += ` Tie reroll${group.tie_break_rolls.length > 1 ? "s" : ""}: ${group.tie_break_rolls.join(" → ")}.`;
      return {
        sequence: sequence++, round_number: 0, event_type: "initiative",
        actor_id: group.combatant_ids[0], actor_name: name,
        attack_roll: group.initiative_roll, animation: "initiative", description,
      };
    });
  }

  window.IRON_PIT_BROWSER_INITIATIVE = { events, priority, resolve };
})();
