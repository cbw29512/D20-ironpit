(() => {
  "use strict";

  const D = () => window.IRON_PIT_BROWSER_DODGE;
  const Dice = () => window.IRON_PIT_DICE;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const O = () => window.IRON_PIT_BROWSER_OFFENSIVE_RANGES;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function grants(member) {
    try {
      const declared = [...(member.state.template.bonusTacticalActionGrants || [])];
      if (member.state.template.cunning_action
          && !declared.some((item) => item.id === "cunning-action-dash")) {
        declared.push({
          id: "cunning-action-dash",
          name: "Cunning Action",
          effects: ["dash"],
          resourceId: null,
          resourceCost: 1,
          priority: 50,
          usePolicy: "enable-offense",
          jumpDistanceMultiplier: 1,
        });
      }
      return declared;
    } catch (error) {
      console.error("Failed browser tactical grant discovery", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function resourceAvailable(state, grant) {
    return R().available(state, grant.resourceId || null, grant.resourceCost || 1);
  }

  function chooseOffensiveDashGrant(member, setup, turnKey) {
    try {
      if (!E().available(member.state, "action") || !E().available(member.state, "bonus_action")) return null;
      const candidates = grants(member).filter((item) =>
        item.usePolicy === "enable-offense"
        && (item.effects || []).includes("dash")
        && resourceAvailable(member.state, item));
      if (!candidates.length) return null;
      const speed = M().effectiveSpeed(member.state);
      if (!(speed > 0)) return null;
      const normalMove = member.state.movement_remaining_ft;
      let dashWouldHelp = false;
      for (const target of F().targetOrder(member, setup)) {
        const distance = S().distance(member, target);
        for (const option of O().rangesForTarget(member, target, turnKey)) {
          if (distance <= option.range + normalMove) return null;
          if (distance <= option.range + normalMove + speed) dashWouldHelp = true;
        }
      }
      if (!dashWouldHelp) return null;
      candidates.sort((a, b) =>
        Number(Boolean(a.resourceId)) - Number(Boolean(b.resourceId))
        || (a.priority ?? 100) - (b.priority ?? 100)
        || String(a.id).localeCompare(String(b.id)));
      return candidates[0];
    } catch (error) {
      console.error("Failed browser tactical Dash choice", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, grant) {
    try {
      if (!grant) throw new Error("Tactical Bonus Action requires a grant.");
      if (!E().available(member.state, "bonus_action")) throw new Error("Bonus Action is not available.");
      if (!resourceAvailable(member.state, grant)) throw new Error(`Resource is unavailable for ${grant.name}.`);
      E().spend(member.state, "bonus_action");
      const remaining = R().spend(member.state, grant.resourceId || null, grant.resourceCost || 1);
      const effects = grant.effects || [];
      let movement = 0;
      if (effects.includes("dash")) {
        movement = M().effectiveSpeed(member.state);
        member.state.movement_remaining_ft += movement;
        member.state.dash_uses_this_turn = (member.state.dash_uses_this_turn || 0) + 1;
      }
      if (effects.includes("disengage")) member.state.disengaged_this_turn = true;
      if (effects.includes("dodge")) {
        if (typeof D()?.applyEffect !== "function") throw new Error("Tactical Dodge requires browser-dodge.js.");
        D().applyEffect(member.state);
      }
      const temporaryHpBefore = member.state.temporary_hp || 0;
      let temporaryHpAfter = temporaryHpBefore;
      if ((grant.temporaryHpDiceCount || 0) > 0) {
        if (!Dice()?.roll) throw new Error("Tactical Temporary HP requires the browser dice API.");
        if (!S()?.grantTemporaryHp) throw new Error("Tactical Temporary HP requires browser-state.js.");
        let amount = 0;
        for (let index = 0; index < grant.temporaryHpDiceCount; index += 1) {
          amount += Dice().roll(grant.temporaryHpDiceSize);
        }
        temporaryHpAfter = S().grantTemporaryHp(member.state, amount);
      }
      return {
        sequence,
        round_number: round,
        event_type: "feature",
        actor_id: member.combatant_id,
        actor_name: member.state.template.name,
        feature_id: grant.id,
        resource_remaining: remaining,
        movement_ft: movement,
        ...((grant.temporaryHpDiceCount || 0) > 0 ? {
          temporary_hp_before: temporaryHpBefore,
          temporary_hp_after: temporaryHpAfter,
        } : {}),
        applied_condition_ids: effects.includes("dodge") ? ["dodge"] : [],
        animation: effects.includes("dash") ? "movement" : "dodge",
        description: `${member.state.template.name} uses ${grant.name}: ${effects.map((item) => item[0].toUpperCase() + item.slice(1)).join(", ")}.`,
      };
    } catch (error) {
      console.error("Failed browser tactical Bonus Action", { member: member?.combatant_id, grant: grant?.id, error });
      throw error;
    }
  }

  function useOffensiveDash(sequence, round, member, setup, turnKey) {
    const grant = chooseOffensiveDashGrant(member, setup, turnKey);
    return grant ? resolve(sequence, round, member, grant) : null;
  }

  function resolveDefensive(sequence, round, member) {
    try {
      if (!E().available(member.state, "bonus_action")) return null;
      if ((member.state.active_effect_ids || []).includes("dodge")) return null;
      if (!(M().effectiveSpeed(member.state) > 0)) return null;
      const candidates = grants(member).filter((item) =>
        item.usePolicy === "defensive-fallback"
        && (item.effects || []).includes("dodge")
        && resourceAvailable(member.state, item));
      if (!candidates.length) return null;
      candidates.sort((a, b) => (a.priority ?? 100) - (b.priority ?? 100)
        || String(a.id).localeCompare(String(b.id)));
      return resolve(sequence, round, member, candidates[0]);
    } catch (error) {
      console.error("Failed browser defensive tactical action", { member: member?.combatant_id, error });
      throw error;
    }
  }

  function installAbilityHooks() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Tactical actions require browser-ability-hooks.js.");
    const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
    if (hooks.abilitiesFor(phase).some((item) => item.id === "bonus-tactical-defense")) return;
    hooks.registerAbility(phase, {
      id: "bonus-tactical-defense",
      priority: 100,
      rulesets: ["2014", "2024"],
      appliesTo: (member, ctx) => ctx.bonusActionCheckpoint === "postAction"
        && grants(member).some((item) => item.usePolicy === "defensive-fallback"),
      resolve: ({ sequence, round, member }) => {
        const event = resolveDefensive(sequence, round, member);
        return event ? { events: [event], sequence: sequence + 1, claimed: true } : null;
      },
    });
  }

  window.IRON_PIT_BROWSER_TACTICAL_ACTIONS = {
    chooseOffensiveDashGrant, grants, installAbilityHooks, resolve, resolveDefensive, useOffensiveDash,
  };
})();