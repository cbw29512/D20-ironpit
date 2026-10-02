(() => {
  "use strict";

  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function active(member, action) {
    return (member.state.timed_effects || []).some(
      (effect) => effect.source_id === member.combatant_id
        && effect.source_effect_id === action.id,
    );
  }

  function resolve(sequence, round, member) {
    try {
      for (const action of member.state.template.attack_action_weapon_buffs || []) {
        if (active(member, action)) continue;
        if (!R().available(member.state, action.resourceId, action.resourceCost || 1)) continue;
        const attacks = member.state.template.attacks || [];
        if (!attacks.some((attack) => (attack.weaponId || attack.id) === action.weaponId)) {
          throw new Error(action.name + " weapon is absent from the combat loadout.");
        }

        const remaining = R().spend(member.state, action.resourceId, action.resourceCost || 1);
        T().apply(member.state, action.id, member.combatant_id, {
          sourceEffectId: action.id,
          sourceTemplate: member.state.template,
          sourceIsMagical: Boolean(action.sourceIsMagical),
          appliedRound: round,
          expiresRound: round + action.durationRounds,
          expiryTiming: "source_turn_start",
          useDefaultPoisonRecovery: false,
        });

        if (action.attackRollBonus) {
          M().add(member.state, {
            id: member.combatant_id + ":" + action.id + ":attack",
            source_id: member.combatant_id,
            source_effect_id: action.id,
            source_name: action.name,
            source_is_magical: Boolean(action.sourceIsMagical),
            kind: "attack-roll-flat",
            flat_bonus: action.attackRollBonus,
            weapon_id: action.weaponId,
            expires_source_turn_end_round: round + action.durationRounds,
          });
        }
        if (action.damageTypeChoice) {
          M().add(member.state, {
            id: member.combatant_id + ":" + action.id + ":damage-type",
            source_id: member.combatant_id,
            source_effect_id: action.id,
            source_name: action.name,
            source_is_magical: Boolean(action.sourceIsMagical),
            kind: "weapon-damage-type-choice",
            damage_type: action.damageTypeChoice,
            weapon_id: action.weaponId,
            expires_source_turn_end_round: round + action.durationRounds,
          });
        }

        return {
          sequence,
          round_number: round,
          event_type: "feature",
          actor_id: member.combatant_id,
          actor_name: member.state.template.name,
          target_id: member.combatant_id,
          target_name: member.state.template.name,
          feature_id: action.id,
          resource_remaining: remaining,
          animation: action.animation || "buff",
          description: member.state.template.name + " uses " + action.name + " on " + action.weaponId + ".",
        };
      }
      return null;
    } catch (error) {
      console.error("Browser Attack-action weapon buff failed.", {
        combatant: member?.combatant_id,
        error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACK_ACTION_WEAPON_BUFFS = { active, resolve };
})();
