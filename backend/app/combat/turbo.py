from __future__ import annotations

import hashlib
import logging
import secrets

from app.combat.dice import SeededDiceProvider
from app.combat.encounter_engine import MAX_ENCOUNTER_ROUNDS, run_encounter
from app.domain.encounters import EncounterBattleResult, EncounterCombatant, EncounterSelection
from app.domain.turbo import (
    MAX_REPLAY_SEED,
    TurboBatchRequest,
    TurboBatchResult,
    TurboFightError,
    TurboFightSummary,
)

logger = logging.getLogger(__name__)


def _derive_fight_seed(batch_seed: int, fight_number: int) -> int:
    payload = f"{batch_seed}:{fight_number}".encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, "big") & MAX_REPLAY_SEED


def _survivors(combatants: list[EncounterCombatant]) -> int:
    return sum(
        1
        for member in combatants
        if member.state.is_alive and not member.state.is_dead and member.state.current_hp > 0
    )


def run_seeded_encounter(selection: EncounterSelection, seed: int) -> EncounterBattleResult:
    """Run the canonical encounter engine with reproducible dice."""
    try:
        if not 0 <= seed <= MAX_REPLAY_SEED:
            raise ValueError("Replay seed is outside the supported range.")
        return run_encounter(selection, SeededDiceProvider(seed))
    except ValueError:
        raise
    except Exception as exc:
        logger.exception("Seeded encounter failed for seed %s.", seed)
        raise RuntimeError("Seeded encounter could not be completed.") from exc


def _summarize_fight(
    fight_number: int,
    seed: int,
    result: EncounterBattleResult,
) -> TurboFightSummary:
    return TurboFightSummary(
        fight_number=fight_number,
        seed=seed,
        outcome=result.outcome,
        rounds=result.rounds,
        hero_survivors=_survivors(result.setup.heroes),
        monster_survivors=_survivors(result.setup.monsters),
        safety_stop=result.outcome == "draw" and result.rounds >= MAX_ENCOUNTER_ROUNDS,
    )


def _rate(value: int, total: int) -> float:
    return round((value / total) * 100, 2) if total else 0.0


def run_turbo_batch(request: TurboBatchRequest) -> TurboBatchResult:
    """Run X independent canonical fights and retain only replayable summaries."""
    batch_seed = request.batch_seed if request.batch_seed is not None else secrets.randbits(63)
    summaries: list[TurboFightSummary] = []
    errors: list[TurboFightError] = []

    for fight_number in range(1, request.fights + 1):
        seed = _derive_fight_seed(batch_seed, fight_number)
        try:
            result = run_seeded_encounter(request.selection, seed)
            summaries.append(_summarize_fight(fight_number, seed, result))
        except Exception as exc:
            logger.exception("Turbo fight %s failed for seed %s.", fight_number, seed)
            errors.append(TurboFightError(
                fight_number=fight_number,
                seed=seed,
                error_type=type(exc).__name__,
                message=str(exc),
            ))

    valid = len(summaries)
    heroes_wins = sum(item.outcome == "heroes_win" for item in summaries)
    monsters_wins = sum(item.outcome == "monsters_win" for item in summaries)
    draws = sum(item.outcome == "draw" for item in summaries)
    fastest = min(summaries, key=lambda item: item.rounds, default=None)
    longest = max(summaries, key=lambda item: item.rounds, default=None)
    average_rounds = round(sum(item.rounds for item in summaries) / valid, 2) if valid else 0.0

    return TurboBatchResult(
        batch_seed=batch_seed,
        requested_fights=request.fights,
        valid_fights=valid,
        engine_errors=len(errors),
        heroes_wins=heroes_wins,
        monsters_wins=monsters_wins,
        draws=draws,
        heroes_win_rate=_rate(heroes_wins, valid),
        monsters_win_rate=_rate(monsters_wins, valid),
        draw_rate=_rate(draws, valid),
        average_rounds=average_rounds,
        fastest_fight_number=fastest.fight_number if fastest else None,
        longest_fight_number=longest.fight_number if longest else None,
        fights=summaries,
        errors=errors,
    )