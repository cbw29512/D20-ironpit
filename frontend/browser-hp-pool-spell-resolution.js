(() => {
  "use strict";
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const SC = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const A = () => window.IRON_PIT_BROWSER_SPELL_AREA;
  const P = () => window.IRON_PIT_BROWSER_HP_POOL_SPELL_POLICY;
  const HP = () => window.IRON_PIT_BROWSER_HIT_POINT_POOL;
  const T = () => window.IRON_PIT_BROWSER_TIMED;

  function resolve(sequence, round, caster, setup, choice, turnKey) {
    try {
      const action = choice.action;
      if (!(caster.state.template.hit_point_pool_spell_actions || []).includes(action)) {
        throw new Error("HP-pool spell is not declared on caster template.");
      }
      if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) {
        throw new Error(`${action.name} requires an available casting Action.`);
      }
      if (window.IRON_PIT_BROWSER_SUPPRESSION_ZONES?.verbalBlocked(caster, setup)) {
        throw new Error(`${action.name} is blocked by Silence.`);
      }
      if (!Number.isInteger(choice.slotLevel) || choice.slotLevel < action.level || choice.slotLevel > 9) {
        throw new Error("Illegal HP-pool spell slot level.");
      }
      const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
      const eligibleIds = enemies.filter(target => P().eligible(caster, target, action, setup))
        .map(target => target.combatant_id);
      const selected = A().bestPlacement(caster, setup, action.areaRadius, action.range,
        [], null, eligibleIds);
      if (!selected || JSON.stringify(selected) !== JSON.stringify(choice.placement)) {
        throw new Error("HP-pool spell placement is no longer legal.");
      }
      const members = [...setup.heroes, ...setup.monsters];
      const byId = new Map(members.map(m => [m.combatant_id, m]));
      const candidates = choice.placement.enemyIds.map(id => {
        const target = byId.get(id);
        if (!target) throw new Error("HP-pool area contains an unknown target.");
        return { combatantId: id, currentHp: target.state.current_hp,
          eligible: P().eligible(caster, target, action, setup) };
      });
      if (!candidates.some(x => x.eligible)) throw new Error("HP-pool area has no eligible target.");

      let remaining = null;
      if (choice.alternateCast) {
        const grant = choice.alternateCast;
        if (grant.spell_id !== action.id || grant.cast_level !== choice.slotLevel) {
          throw new Error("Invalid alternate cast grant for HP-pool spell.");
        }
        if (grant.resource_id) {
          const cost = grant.resource_cost || 1;
          const current = caster.state.resources?.[grant.resource_id] || 0;
          if (current < cost) throw new Error("Insufficient innate spell uses.");
          caster.state.resources[grant.resource_id] = current - cost;
          remaining = caster.state.resources[grant.resource_id];
        }
      } else {
        if (!SC().slotSpellAvailable(caster.state, turnKey)) {
          throw new Error("A spell slot was already expended this turn.");
        }
        const id = `spell-slot-${choice.slotLevel}`;
        if (!(caster.state.resources?.[id] > 0)) throw new Error("No spell slot remains.");
        SC().markSlotSpellCast(caster.state, turnKey);
        caster.state.resources[id] -= 1;
        remaining = caster.state.resources[id];
      }
      if ((caster.state.timed_effects || []).some(e => e.ends_on_owner_spell_cast)) {
        if (!T()?.expireOnOwnerEvent) throw new Error("Spell owner-expiry runtime missing.");
        T().expireOnOwnerEvent(caster.state, "spell_cast", members.map(m => m.state));
      }
      E().spend(caster.state, action.actionCost);
      window.IRON_PIT_BROWSER_DEFENSIVE_MODIFIERS?.removeOwnerAttackEnding(caster.state);
      const count = action.poolDiceCount + (choice.slotLevel - action.level) * action.extraDicePerUpcastLevel;
      const rolls = window.IRON_PIT_DICE.rollMany(count, action.poolDiceSize);
      const total = rolls.reduce((sum, value) => sum + value, 0);
      const { affected, remaining: leftover } = HP().allocateHitPointPool(total, candidates);
      const slotText = choice.alternateCast?.source_name || `level ${choice.slotLevel} slot`;
      const events = [{
        sequence: sequence++, round_number: round, event_type: "feature",
        actor_id: caster.combatant_id, actor_name: caster.state.template.name,
        feature_id: action.id, resource_remaining: remaining,
        feature_roll: { notation: `${count}d${action.poolDiceSize}`, rolls, modifier: 0, total },
        animation: action.animation,
        description: `${caster.state.template.name} casts ${action.name} using ${slotText}: ${total} HP in the pool; ${leftover} HP unused.`,
      }];
      for (const id of affected) {
        const target = byId.get(id);
        const applied = T().apply(target.state, action.conditionId, caster.combatant_id, {
          sourceEffectId: action.id, sourceTemplate: caster.state.template,
          sourceIsMagical: true, targetActor: target, setup,
          affectedStates: members.map(m => m.state),
          appliedRound: round, expiresRound: round + action.durationRounds,
          expiryTiming: action.expiryTiming, endsOnDamage: action.endsOnDamage,
          allowedRemovalActionIds: [...(action.allowedRemovalActionIds || [])],
          useDefaultPoisonRecovery: false,
        });
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: caster.combatant_id, actor_name: caster.state.template.name,
          target_id: id, target_name: target.state.template.name,
          feature_id: action.id, applied_condition_ids: applied ? [applied] : [],
          animation: action.animation,
          description: applied
            ? `${target.state.template.name} is affected by ${action.name} and becomes ${action.conditionId}.`
            : `${target.state.template.name} resists ${action.name}.`,
        });
      }
      return { events, sequence };
    } catch (error) {
      console.error("Browser HP-pool spell casting failed", {
        caster: caster?.combatant_id, action: choice?.action?.id, error,
      });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_HP_POOL_SPELL = { resolve };
})();
