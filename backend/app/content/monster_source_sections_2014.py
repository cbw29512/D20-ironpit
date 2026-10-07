from __future__ import annotations
from html import unescape
import logging
import re
logger = logging.getLogger(__name__)

def source_sections_2014(source: str | None) -> dict[str, str]:
    try:
        sections = {}
        for paragraph in re.findall(r"<p>(.*?)</p>", source or "", re.S):
            heading = re.search(r"<strong>(.*?)</strong>", paragraph, re.S)
            if heading:
                name = unescape(re.sub(r"<[^>]*>", "", heading[1])).rstrip(".")
                body = re.sub(r"<[^>]*>", "", paragraph[heading.end():])
                sections[name] = " ".join(unescape(body).split())
        return sections
    except Exception:
        logger.exception("Failed to read 2014 source sections.")
        raise


