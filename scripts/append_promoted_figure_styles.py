from __future__ import annotations

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSS_PATH = Path("frontend/figure-archetypes.css")
MARKER = "/* Promoted RAW-ready identities: tree, gargoyle, grimlock, guard captain, violet fungus. */"
STYLES = r'''

/* Promoted RAW-ready identities: tree, gargoyle, grimlock, guard captain, violet fungus. */
.stick-figure[data-form="plant"][data-detail="tree"] .head{width:34px;height:28px;left:13px;top:19px;border:6px solid currentColor;border-radius:45%;background:transparent}
.stick-figure[data-form="plant"][data-detail="tree"] .body{width:12px;height:49px;left:24px;top:44px;border-radius:35% 35% 10% 10%}
.stick-figure[data-form="plant"][data-detail="tree"] .arms{width:58px;height:7px;left:1px;top:48px;transform:rotate(-7deg)}
.stick-figure[data-form="plant"][data-detail="tree"] .legs{width:8px;height:18px;left:21px;top:87px;transform:rotate(24deg);box-shadow:17px 0 0 currentColor}
.stick-figure[data-form="plant"][data-detail="tree"] .feature-one,.stick-figure[data-form="plant"][data-detail="tree"] .feature-two{display:block;width:21px;height:21px;top:16px;border:5px solid currentColor;border-radius:50%;background:transparent}
.stick-figure[data-form="plant"][data-detail="tree"] .feature-one{left:5px}.stick-figure[data-form="plant"][data-detail="tree"] .feature-two{right:5px}

.stick-figure[data-form="gargoyle"] .head{width:23px;height:20px;left:18px;top:27px;border:5px solid currentColor;border-radius:35% 35% 50% 50%;background:transparent}
.stick-figure[data-form="gargoyle"] .body{width:13px;height:39px;left:23px;top:46px;border-radius:35%}
.stick-figure[data-form="gargoyle"] .arms{width:54px;height:6px;left:3px;top:53px;transform:rotate(-9deg)}
.stick-figure[data-form="gargoyle"] .legs{width:5px;height:26px;left:20px;top:80px;transform:rotate(20deg);box-shadow:19px 0 0 currentColor}
.stick-figure[data-form="gargoyle"] .feature-one,.stick-figure[data-form="gargoyle"] .feature-two{display:block;width:29px;height:31px;top:42px;background:transparent;border-top:5px solid currentColor}
.stick-figure[data-form="gargoyle"] .feature-one{left:-4px;border-left:4px solid currentColor;transform:skewY(-25deg)}
.stick-figure[data-form="gargoyle"] .feature-two{right:-4px;border-right:4px solid currentColor;transform:skewY(25deg)}
.stick-figure[data-form="gargoyle"] .tail{display:block;width:31px;height:5px;right:-19px;top:74px;transform:rotate(-33deg);border-radius:999px}

.stick-figure[data-form="humanoid"][data-detail="grimlock"] .head{width:25px;height:22px;left:17px;top:27px;border-radius:45%}
.stick-figure[data-form="humanoid"][data-detail="grimlock"] .feature-one{display:block;width:28px;height:5px;left:15px;top:35px;background:currentColor;border-radius:999px}
.stick-figure[data-form="humanoid"][data-detail="grimlock"] .body{width:11px;left:24px}
.stick-figure[data-form="humanoid"][data-detail="grimlock"] .arms{width:55px;left:2px;height:7px}

.stick-figure[data-form="humanoid"][data-detail="guard-captain"] .head{border-radius:18% 18% 45% 45%}
.stick-figure[data-form="humanoid"][data-detail="guard-captain"] .feature-one{display:block;width:28px;height:10px;left:15px;top:24px;background:transparent;border-top:5px solid currentColor;border-left:4px solid currentColor;border-right:4px solid currentColor}
.stick-figure[data-form="humanoid"][data-detail="guard-captain"] .body{width:16px;left:22px;border-radius:20%}
.stick-figure[data-form="humanoid"][data-detail="guard-captain"] .arms{width:54px;left:3px;height:7px}

.stick-figure[data-form="plant"][data-detail="violet-fungus"] .head{width:46px;height:18px;left:7px;top:28px;border:5px solid currentColor;border-radius:70% 70% 30% 30%;background:transparent}
.stick-figure[data-form="plant"][data-detail="violet-fungus"] .body{width:12px;height:43px;left:24px;top:45px;border-radius:35%}
.stick-figure[data-form="plant"][data-detail="violet-fungus"] .arms{width:50px;height:4px;left:5px;top:64px;transform:rotate(13deg);box-shadow:0 10px 0 currentColor}
.stick-figure[data-form="plant"][data-detail="violet-fungus"] .legs{display:none}
.stick-figure[data-form="plant"][data-detail="violet-fungus"] .feature-one{display:block;width:35px;height:5px;left:12px;top:89px;background:currentColor;border-radius:50%}
'''


def main() -> None:
    try:
        text = CSS_PATH.read_text(encoding="utf-8")
        if MARKER in text:
            logger.info("Promoted monster figure styles already present.")
            return
        CSS_PATH.write_text(text.rstrip() + STYLES + "\n", encoding="utf-8")
        logger.info("Appended reviewed figure styles for five promoted monsters.")
    except Exception as exc:
        logger.exception("Failed to append promoted monster figure styles.")
        raise RuntimeError("Promoted monster figure style generation failed.") from exc


if __name__ == "__main__":
    main()
