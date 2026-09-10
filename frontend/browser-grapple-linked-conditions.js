(() => {
  "use strict";

  function install() {
    try {
      const engine = window.IRON_PIT_BROWSER_ATTACK;
      if (!engine?.resolveAttack || engine.__grappleLinkedConditionHookInstalled) return;
      const base = engine.resolveAttack.bind(engine);
      engine.resolveAttack = function resolveAttackWithGrappleConditions(
        sequence, round, attacker, target, attack, distance, extra = {},
      ) {
        const event = base(sequence, round, attacker, target, attack, distance, extra);
        const linked = attack?.controlEffect?.conditionsWhileGrappled || [];
        if (!event.hit || !linked.length) return event;
        const members = extra.setup ? [...extra.setup.heroes, ...extra.setup.monsters] : [target];
        const actual = members.find((member) => member.combatant_id === event.target_id) || target;
        const grapple = (actual.state.grapple_sources || []).find((source) => source.source_id === attacker.combatant_id);
        if (!grapple) return event;
        grapple.linked_conditions = [...new Set([...(grapple.linked_conditions || []), ...linked])];
        for (const condition of linked) {
          if (window.IRON_PIT_BROWSER_CONDITION_IMMUNITY?.immune(actual.state, condition)) continue;
          if (!actual.state.active_effect_ids.includes(condition)) actual.state.active_effect_ids.push(condition);
          if (!event.applied_condition_ids.includes(condition)) event.applied_condition_ids.push(condition);
        }
        return event;
      };
      engine.__grappleLinkedConditionHookInstalled = true;
    } catch (error) {
      console.error("Failed to install grapple-linked condition hook", error);
      throw error;
    }
  }

  install();
})();
