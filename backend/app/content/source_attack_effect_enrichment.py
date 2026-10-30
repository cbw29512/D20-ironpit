from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def merge_attack_effects(
    existing: list,
    source: list,
    *,
    charge_profile: object | None = None,
) -> list:
    """Merge source-derived attack effects without duplicating semantic effect families."""
    try:
        known_kinds = {effect.kind for effect in existing}
        source_by_kind = {effect.kind: effect for effect in source}
        charge_owns_prone = bool(
            charge_profile is not None
            and getattr(charge_profile, "prone_max_target_size", None) is not None
        )
        merged_existing = [
            effect.model_copy(update={"escape_check_disadvantage": True})
            if (
                effect.kind == "grapple"
                and getattr(source_by_kind.get("grapple"), "escape_check_disadvantage", False)
                and not getattr(effect, "escape_check_disadvantage", False)
            )
            else effect
            for effect in existing
        ]
        additions = [
            effect
            for effect in source
            if effect.kind not in known_kinds
            and not (effect.kind == "prone" and charge_owns_prone)
        ]
        return [*merged_existing, *additions]
    except Exception as exc:
        logger.exception("Failed to merge source-derived attack effects.")
        raise RuntimeError("Source attack effects could not be enriched.") from exc
