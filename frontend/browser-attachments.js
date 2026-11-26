(() => {
  "use strict";

  // Shared fight-local relationship state; never apply Grappled or a speed penalty.
  const TYPE = new Set(["direct_hp_loss", "typed_damage"]);
  const TIMING = new Set(["source_turn_start", "target_turn_start", "target_turn_end"]);
  const error = (operation, err) => {
    console.error(`Attachment ${operation} failed:`, err);
    throw err;
  };

  function validate(row) {
    try {
      if (!row || typeof row !== "object" || !["source_id", "target_id", "effect_id", "source_name"]
        .every((key) => typeof row[key] === "string" && row[key].length > 0)) {
        throw Error("Attachment requires source, target and effect identities.");
      }
      if (row.source_id === row.target_id) throw Error("Attachment source and target must differ.");
      if (!Number.isInteger(row.damage_dice_count) || row.damage_dice_count < 0
        || !Number.isInteger(row.damage_dice_size) || row.damage_dice_size < 2) {
        throw Error("Attachment requires valid periodic dice.");
      }
      if (row.periodic_effect_kind != null && !TYPE.has(row.periodic_effect_kind)) throw Error("Unknown attachment periodic effect kind.");
      if ((row.periodic_effect_kind == null) !== (row.damage_dice_count === 0)) {
        throw Error("Only a non-periodic attachment may omit periodic dice.");
      }
      if (row.periodic_effect_kind === "direct_hp_loss" && row.damage_type != null) {
        throw Error("Direct HP loss cannot have a damage type.");
      }
      if (row.periodic_effect_kind === "typed_damage"
        && (typeof row.damage_type !== "string" || !row.damage_type)) {
        throw Error("Typed attachment damage requires a damage type.");
      }
      if (!Number.isInteger(row.damage_bonus ?? 0)) throw Error("Invalid attachment dice bonus.");
      if (!TIMING.has(row.damage_timing ?? "source_turn_start")) {
        throw Error("Invalid attachment periodic timing.");
      }
      if (row.detach_after_hp_lost != null
        && (!Number.isInteger(row.detach_after_hp_lost) || row.detach_after_hp_lost <= 0)) {
        throw Error("Invalid automatic detachment threshold.");
      }
      if (!Number.isInteger(row.actual_hp_lost ?? 0) || (row.actual_hp_lost ?? 0) < 0) {
        throw Error("Recorded actual HP loss must be nonnegative.");
      }
      return Object.freeze({ ...row, damage_bonus: row.damage_bonus ?? 0,
        damage_timing: row.damage_timing ?? "source_turn_start", actual_hp_lost: row.actual_hp_lost ?? 0 });
    } catch (err) { return error("validation", err); }
  }

  function attach(existing, entry) {
    try {
      const item = validate(entry);
      if (existing.some((row) => row.source_id === item.source_id && row.effect_id === item.effect_id)) {
        throw Error("Source already has this attachment effect active.");
      }
      return [...existing, item];
    } catch (err) { return error("attach", err); }
  }

  function detachForCombatant(existing, id) {
    try { return existing.filter((row) => row.source_id !== id && row.target_id !== id); }
    catch (err) { return error("combatant cleanup", err); }
  }

  function syncControls(setup) {
    const members = new Map([...setup.heroes, ...setup.monsters]
      .map((member) => [member.combatant_id, member]));
    for (const member of members.values()) {
      const state = member.state;
      if (!state) continue;
      const priorBlind = (state.attachment_blind_source_ids || []).length > 0;
      const blind = (setup.attachments || []).filter((row) => row.target_id === member.combatant_id && row.blinds_target).map((row) => row.source_id);
      const breath = (setup.attachments || []).filter((row) => row.target_id === member.combatant_id && row.prevents_breathing).map((row) => row.source_id);
      const speed = (setup.attachments || []).filter((row) => row.source_id === member.combatant_id && row.source_speed_zero).map((row) => row.effect_id);
      if (blind.length && !priorBlind) state.attachment_blind_preexisting = state.active_effect_ids.includes("blinded");
      state.attachment_blind_source_ids = blind; state.attachment_breathing_source_ids = breath; state.attachment_speed_zero_source_ids = speed;
      if (blind.length && !state.active_effect_ids.includes("blinded")) state.active_effect_ids.push("blinded");
      if (priorBlind && !blind.length) {
        const other = state.attachment_blind_preexisting
          || (state.grapple_sources || []).some((source) => source.blinds)
          || (state.timed_effects || []).some((effect) => effect.effect_id === "blinded")
          || (state.template?.innate_condition_ids || []).includes("blinded");
        if (!other) state.active_effect_ids = state.active_effect_ids.filter((id) => id !== "blinded");
        state.attachment_blind_preexisting = false;
      }
      if (!breath.length && !(state.grapple_sources || []).some((source) => source.prevents_breathing)) {
        window.IRON_PIT_BROWSER_BREATHING?.reset(state);
      }
    }
  }

  function detach(existing, sourceId, effectId) {
    try { return existing.filter((row) => row.source_id !== sourceId || row.effect_id !== effectId); }
    catch (err) { return error("detach", err); }
  }

  function recordHpLoss(existing, sourceId, effectId, actualHpLost) {
    try {
      if (!Number.isInteger(actualHpLost) || actualHpLost < 0) {
        throw Error("Actual HP loss must be a nonnegative integer.");
      }
      return existing.flatMap((row) => {
        if (row.source_id !== sourceId || row.effect_id !== effectId) return [row];
        const count = (row.actual_hp_lost ?? 0) + actualHpLost;
        if (row.detach_after_hp_lost != null && count >= row.detach_after_hp_lost) return [];
        return [validate({ ...row, actual_hp_lost: count })];
      });
    } catch (err) { return error("HP-loss ledger", err); }
  }

  function linkedEffects(existing) {
    try {
      return existing.flatMap((row) => [
        { owner_id: row.target_id, counterpart_id: row.source_id,
          effect_id: "attached", kind: "debuff" },
        { owner_id: row.source_id, counterpart_id: row.target_id,
          effect_id: row.effect_id, kind: "buff" },
      ]);
    } catch (err) { return error("linked status projection", err); }
  }

  function activeTarget(existing, sourceId, effectId) {
    try {
      const matches = existing.filter((row) => row.source_id === sourceId && row.effect_id === effectId);
      if (matches.length > 1) throw Error("Source has multiple targets for one attachment effect.");
      return matches.length ? matches[0].target_id : null;
    } catch (err) { return error("active target lookup", err); }
  }

  function sourceAttacksBlocked(setup, sourceId, targetId = null) {
    try {
      if (setup?.attachments?.some((row) => row.source_id === sourceId && row.blocks_source_attacks)) return true;
      const locked = (setup?.attachments || []).filter((row) => row.source_id === sourceId && row.source_target_lock);
      return Boolean(locked.length && !locked.some((row) => row.target_id === targetId));
    } catch (err) { return error("source attack restriction", err); }
  }

  function attackAdvantage(setup, sourceId, targetId) {
    return Number(Boolean((setup?.attachments || []).some((row) =>
      row.source_id === sourceId && row.target_id === targetId
      && row.source_advantage_against_target)));
  }

  function moveWithTarget(setup, targetId) {
    const members = new Map([...setup.heroes, ...setup.monsters]
      .map((member) => [member.combatant_id, member]));
    const target = members.get(targetId);
    if (!target) return;
    for (const row of setup.attachments || []) {
      if (row.target_id === targetId && row.moves_with_target && members.has(row.source_id)) {
        members.get(row.source_id).position_ft = target.position_ft;
      }
    }
  }

  function applyOnHit(setup, attacker, target, attack, attackMode = "normal") {
    try {
      const spec = attack.onHitAttachment;
      if (!spec) return false;
      if (!setup) throw Error("On-hit attachment needs encounter setup.");
      // An unconscious hero at zero HP remains alive: the source can attach.
      if (!target.state.is_alive || target.state.is_dead) return false;
      if (spec.attach_max_target_size && !window.IRON_PIT_BROWSER_STATE.sizeAtMost(target, spec.attach_max_target_size)) return false;
      const enhanced = Boolean(spec.enhanced_on_attack_advantage && attackMode === "advantage"
        && (!spec.enhanced_max_target_size || window.IRON_PIT_BROWSER_STATE.sizeAtMost(target, spec.enhanced_max_target_size)));
      if (!Array.isArray(setup.attachments)) setup.attachments = [];
      const row = {
        source_id: attacker.combatant_id, target_id: target.combatant_id,
        effect_id: spec.effect_id, source_name: spec.source_name,
        damage_dice_count: spec.dice_count ?? 0, damage_dice_size: spec.dice_size ?? 6,
        damage_bonus: spec.damage_bonus, damage_type: spec.damage_type,
        periodic_effect_kind: spec.periodic_effect_kind, damage_timing: spec.tick_timing,
        detach_after_hp_lost: spec.auto_end_after_hp_loss,
        blocks_source_attacks: spec.blocks_source_attacks,
        action_removable: spec.action_removable,
        action_removal_range_ft: spec.action_removal_range_ft,
        source_detach_movement_ft: spec.source_detach_movement_ft,
        source_target_lock: Boolean(spec.source_target_lock),
        source_advantage_against_target: Boolean(spec.source_advantage_against_target),
        source_speed_zero: Boolean(spec.source_speed_zero), moves_with_target: Boolean(spec.moves_with_target),
        blinds_target: Boolean(enhanced && spec.enhanced_blinds_target),
        prevents_breathing: Boolean(enhanced && spec.enhanced_prevents_breathing),
        action_removal_check_ability: spec.action_removal_check_ability || null,
        action_removal_check_dc: spec.action_removal_check_dc ?? null,
      };
      setup.attachments = attach(setup.attachments, row);
      syncControls(setup);
      return true;
    } catch (err) { return error("attack hit", err); }
  }

  window.IRON_PIT_BROWSER_ATTACHMENTS = {
    validate, attach, detach, detachForCombatant, recordHpLoss, linkedEffects, activeTarget, applyOnHit, sourceAttacksBlocked, attackAdvantage, moveWithTarget, syncControls,
  };
})();
