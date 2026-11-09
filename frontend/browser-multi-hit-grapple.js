(() => {
  "use strict";
  const SIZES = ["tiny", "small", "medium", "large", "huge", "gargantuan"];

  function resolve(sequence, round, member, setup, attackEvents) {
    try {
      const rules = member.state.template.multiHitGrappleEffects || [];
      if (!rules.length || member.state.is_dead || !member.state.is_alive) {
        return {events: [], sequence};
      }
      const grapple = window.IRON_PIT_BROWSER_GRAPPLE;
      if (!grapple?.apply) throw new Error("Multi-hit grapple requires universal grapple runtime.");
      const members = [...setup.heroes, ...setup.monsters];
      const byId = new Map(members.map(item => [item.combatant_id, item]));
      const events = [];
      for (const rule of rules) {
        const counts = new Map();
        for (const hit of attackEvents) {
          if (hit.event_type !== "attack" || hit.attack_id !== rule.attackId
            || !hit.hit || !hit.target_id) continue;
          const n = (counts.get(hit.target_id) || 0) + 1;
          counts.set(hit.target_id, n);
          if (n !== rule.hitsRequired) continue;
          const target = byId.get(hit.target_id);
          if (!target || target.side === member.side) {
            throw new Error("Repeated-hit grapple must target an opponent.");
          }
          if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) continue;
          const maxSize = SIZES.indexOf(rule.maxTargetSize);
          const actualSize = SIZES.indexOf(target.state.template.size);
          if (maxSize < 0 || actualSize < 0) throw new Error("Source size bounds are invalid.");
          if (actualSize > maxSize) continue;
          if (window.IRON_PIT_BROWSER_STATE.distance(member, target) > rule.rangeFt) continue;
          const held = members.filter(item => item !== member &&
            (item.state.grapple_sources || []).some(source =>
              source.source_id === member.combatant_id
              && source.linked_effect_id === rule.effectId)).length;
          // Capacity limits the linked Engulf effect, not the ordinary
          // Grappled condition caused by the required successful hits.
          if ((target.state.grapple_sources || []).some(source =>
              source.source_id === member.combatant_id
              && source.linked_effect_id === rule.effectId)) continue;
          const atCapacity = held >= rule.maxActiveGrapples;
          const applied = grapple.apply(
            target.state, member.combatant_id, rule.escapeDc, rule.rangeFt,
            !atCapacity && rule.restrains, false, null,
            {blinds: !atCapacity && rule.blinds,
             preventsBreathing: !atCapacity && rule.preventsBreathing,
             effectId: atCapacity ? null : rule.effectId},
          );
          if (!applied.length) continue;
          const conditions = [...applied];
          if (!atCapacity && rule.blinds && target.state.active_effect_ids.includes("blinded")) {
            conditions.push("blinded");
          }
          events.push({
            sequence: sequence++, round_number: round, event_type: "feature",
            actor_id: member.combatant_id, actor_name: member.state.template.name,
            target_id: target.combatant_id, target_name: target.state.template.name,
            feature_id: rule.sourceName, animation: "feature",
            applied_condition_ids: [...new Set(conditions)],
            description: member.state.template.name + ": " + rule.sourceName
              + " after " + rule.hitsRequired + " hits on " + target.state.template.name
              + "; Grappled (escape DC " + rule.escapeDc + ")"
              + (atCapacity ? "; " + rule.sourceName + " capacity reached"
                : (rule.blinds ? ", Blinded" : "")
                  + (rule.restrains ? ", Restrained" : "")
                  + (rule.preventsBreathing ? ", unable to breathe" : "")) + ".",
          });
        }
      }
      return {events, sequence};
    } catch (error) {
      console.error("Browser repeated-hit grapple resolution failed.", {
        attacker: member?.combatant_id, error,
      });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_MULTI_HIT_GRAPPLE = {resolve};
})();
