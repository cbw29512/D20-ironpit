from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT_DIR / "frontend" / "config.js"


def get_api_base() -> str:
    """Return a validated public API base URL, or blank for static preview mode."""
    try:
        api_base = os.getenv("IRON_PIT_API_BASE", "").strip().rstrip("/")
        if not api_base:
            logger.warning("IRON_PIT_API_BASE is unset; building Netlify static preview mode.")
            return ""
        if not api_base.startswith(("http://", "https://")):
            raise ValueError("IRON_PIT_API_BASE must begin with http:// or https://.")
        return api_base
    except Exception:
        logger.exception("Frontend API configuration validation failed.")
        raise


def write_config(api_base: str) -> None:
    """Write browser-safe deployment configuration using JSON string encoding."""
    try:
        CONFIG_PATH.write_text(
            f"window.IRON_PIT_API_BASE = {json.dumps(api_base)};\n",
            encoding="utf-8",
        )
        logger.info("Wrote frontend configuration to %s", CONFIG_PATH)
    except Exception:
        logger.exception("Failed to write frontend configuration.")
        raise


def main() -> None:
    try:
        write_config(get_api_base())
    except Exception as exc:
        logger.error("Frontend configuration generation failed: %s", exc)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
