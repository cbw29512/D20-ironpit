from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path

from app.content.capability_compiler import compile_combatant
from app.content.json_hero_compile import compile_hero_definition
from app.content.json_hero_fold import fold_hero_level
from app.content.json_hero_io import load_hero_bundle
from app.domain.models import CombatantTemplate

LOGGER = logging.getLogger(__name__)
REPO_ROOT = Path(__file__).resolve().parents[3]
TemplateLevelBuilder = Callable[[int], CombatantTemplate]


def compile_json_hero_template(edition: str, slug: str, level: int) -> CombatantTemplate:
    try:
        identity, class_prog, subclass, species, track, build = load_hero_bundle(
            REPO_ROOT, edition, slug,
        )
        folded = fold_hero_level(class_prog, subclass, species, track, level)
        definition = compile_hero_definition(identity.id, identity.name, folded, build)
        unsupported = list(definition.unsupported_capabilities)
        if unsupported:
            raise ValueError(
                f"{edition} {slug} level {level} is blocked by unsupported capabilities: {unsupported}"
            )
        return compile_combatant(definition)
    except Exception:
        LOGGER.exception("JSON hero runtime compile failed edition=%s slug=%s level=%s", edition, slug, level)
        raise


def json_template_builder(edition: str, slug: str) -> TemplateLevelBuilder:
    try:
        def build(level: int) -> CombatantTemplate:
            return compile_json_hero_template(edition, slug, level)

        build.__name__ = f"json_{edition}_{slug.replace('-', '_')}"
        build.__qualname__ = build.__name__
        return build
    except Exception:
        LOGGER.exception("Unable to bind JSON template builder edition=%s slug=%s", edition, slug)
        raise
