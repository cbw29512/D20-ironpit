(() => {
  "use strict";

  const D = () => window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS;
  const V = () => window.IRON_PIT_BROWSER_SAVES;

  function check(attacker, target) {
    D().removeOwnerAttackEnding(attacker.state);
    const gate = D().targetingGate(target.state);
    if (!gate) return null;
    const save = V().resolveSavingThrow(attacker.state, gate.save_ability || "wisdom", gate.save_dc || 1);
    return { gate, roll: save.roll, succeeded: save.succeeded };
  }

  function blocked(sequence, round, attacker, target, actionName, ward) {
    return {
      sequence, round_number: round, event_type: "saving_throw",
      actor_id: attacker.combatant_id, actor_name: attacker.state.template.name,
      target_id: target.combatant_id, target_name: target.state.template.name,
      attack_name: actionName, saving_throw_roll: ward.roll,
      save_ability: ward.gate.save_ability, save_dc: ward.gate.save_dc,
      save_succeeded: false, hit: false, feature_id: ward.gate.source_effect_id,
      animation: ward.gate.source_effect_id,
      description: attacker.state.template.name + " fails the " + ward.gate.save_ability
        + " save against " + ward.gate.source_effect_id + "; the attack or spell targeting "
        + target.state.template.name + " is lost.",
    };
  }

  function annotate(event, ward, attackerName) {
    if (!ward) return event;
    if (!event.saving_throw_roll) {
      event.saving_throw_roll = ward.roll;
      event.save_ability = ward.gate.save_ability;
      event.save_dc = ward.gate.save_dc;
      event.save_succeeded = true;
    }
    event.description += " " + attackerName + " succeeds against " + ward.gate.source_effect_id + ".";
    return event;
  }

  window.IRON_PIT_BROWSER_TARGETING_WARDS = { annotate, blocked, check };
})();