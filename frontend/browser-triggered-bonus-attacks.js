(() => {
  "use strict";
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const H = () => window.IRON_PIT_BROWSER_MAX_HP_REDUCTION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function attackById(member, id) {
    try {
      const attacks = member.state.template.attacks || [];
      const matches = attacks.filter((attack) => attack.id === id);
      if (matches.length !== 1) throw new Error("Expected one triggered attack " + id + "; found " + matches.length + ".");
      return matches[0];
    } catch (error) {
      console.error("Failed browser triggered attack lookup.", { member: member?.combatant_id, id, error });
      throw error;
    }
  }

  function inRange(attack, distance) {
    try {
      if ((attack.kind === "melee" || attack.kind === "melee_or_ranged") && distance <= (attack.reach || 5)) return true;
      if (attack.kind === "ranged" || attack.kind === "melee_or_ranged") return distance <= (attack.longRange || attack.normalRange || 0);
      return false;
    } catch (error) {
      console.error("Failed browser triggered attack range check.", { attack: attack?.id, error });
      throw error;
    }
  }

  function qualifying(member, setup, events) {
    try {
      const byId = new Map([...setup.heroes, ...setup.monsters].map((item) => [item.combatant_id, item]));
      for (const event of [...events].reverse()) {
        if (event.actor_id !== member.combatant_id || event.event_type !== "attack") continue;
        if (!event.damage_roll || event.damage_roll.total <= 0 || event.hp_before == null) continue;
        const target = byId.get(event.target_id);
        if (!target) continue;
        const maxBefore = event.max_hp_before || H().effectiveMaxHp(target.state);
        if (event.hp_before * 2 <= maxBefore) return event;
      }
      return null;
    } catch (error) {
      console.error("Failed browser triggered Bonus Action event scan.", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, events, turnKey) {
    try {
      if (!E().available(member.state, "bonus_action")) return { events: [], sequence };
      const trigger = qualifying(member, setup, events);
      if (!trigger) return { events: [], sequence };
      const members = [...setup.heroes, ...setup.monsters];
      const byId = new Map(members.map((item) => [item.combatant_id, item]));
      for (const feature of member.state.template.triggered_bonus_attacks || []) {
        if (feature.trigger !== "damage_target_already_bloodied") throw new Error("Unsupported trigger: " + feature.trigger);
        if (!R().available(member.state, feature.resourceId, feature.resourceCost || 1)) continue;
        const attack = attackById(member, feature.attackId);
        const original = byId.get(trigger.target_id);
        const candidates = [original, ...members.filter((item) => item.side !== member.side && item !== original)].filter(Boolean);
        const target = candidates.find((item) => item.state.is_alive && !item.state.is_dead && inRange(attack, S().distance(member, item)));
        if (!target) return { events: [], sequence };
        E().spend(member.state, "bonus_action");
        const remaining = R().spend(member.state, feature.resourceId, feature.resourceCost || 1);
        const event = A().resolveAttack(sequence++, round, member, target, attack, S().distance(member, target), {
          spendAction: false, featureId: feature.id, setup, turnKey,
        });
        event.resource_remaining = remaining;
        return { events: [event], sequence };
      }
      return { events: [], sequence };
    } catch (error) {
      console.error("Failed browser triggered Bonus Action attack.", { member: member?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_TRIGGERED_BONUS_ATTACKS = { resolve };
})();
