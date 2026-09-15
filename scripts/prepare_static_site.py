from __future__ import annotations

import logging

from export_browser_heroes_2014_playtest import main as export_browser_heroes
from export_browser_monsters_2014 import main as export_browser_monsters
from export_browser_spell_effects import main as export_browser_spell_effects
from export_figure_profiles import main as export_figure_profiles

logger = logging.getLogger(__name__)


def main() -> None:
    try:
        export_browser_heroes()
        export_browser_monsters()
        export_browser_spell_effects()
        export_figure_profiles()
        logger.info("Static Iron Pit 2014 playtest content preparation completed.")
    except Exception:
        logger.exception("Static Iron Pit 2014 playtest content preparation failed.")
        raise


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
