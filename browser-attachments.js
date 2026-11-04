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
      if (!Number.isInteger(row.damage_dice_count) || row.damage_dice_count <= 0
        || !Number.isInteger(row.damage_dice_size) || row.damage_dice_size < 2) {
        throw Error("Attachment requires valid periodic dice.");
      }
      if (!TYPE.has(row.periodic_effect_kind)) throw Error("Unknown attachment periodic effect kind.");
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

  function sourceAttacksBlocked(setup, sourceId) {
    try {
      return Boolean(setup?.attachments?.some((row) =>
        row.source_id === sourceId && row.blocks_source_attacks));
    } catch (err) { return error("source attack restriction", err); }
  }

  function applyOnHit(setup, attacker, target, attack) {
    try {
      const spec = attack.onHitAttachment;
      if (!spec) return false;
      if (!setup) throw Error("On-hit attachment needs encounter setup.");
      if (!target.state.is_alive || target.state.is_dead || target.state.current_hp <= 0) return false;
      if (!Array.isArray(setup.attachments)) setup.attachments = [];
      const row = {
        source_id: attacker.combatant_id, target_id: target.combatant_id,
        effect_id: spec.effect_id, source_name: spec.source_name,
        damage_dice_count: spec.dice_count, damage_dice_size: spec.dice_size,
        damage_bonus: spec.damage_bonus, damage_type: spec.damage_type,
        periodic_effect_kind: spec.periodic_effect_kind, damage_timing: spec.tick_timing,
        detach_after_hp_lost: spec.auto_end_after_hp_loss,
        blocks_source_attacks: spec.blocks_source_attacks,
        action_removable: spec.action_removable,
        action_removal_range_ft: spec.action_removal_range_ft,
        source_detach_movement_ft: spec.source_detach_movement_ft,
      };
      setup.attachments = attach(setup.attachments, row);
      return true;
    } catch (err) { return error("attack hit", err); }
  }

  window.IRON_PIT_BROWSER_ATTACHMENTS = {
    validate, attach, detach, detachForCombatant, recordHpLoss, linkedEffects, activeTarget, applyOnHit, sourceAttacksBlocked,
  };
})();
