"""Fill site/assets/ with the pictures the landing page shows.

    python scripts/make_site.py

The page shows the Calculator run recorded by make_hero.py and nothing else, so this
only copies that run's captures next to the page. It drives nothing and is safe to run.
"""

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAPTURE = ROOT / "docs" / "assets" / "capture"
ASSETS = ROOT / "site" / "assets"

if __name__ == "__main__":
    ASSETS.mkdir(parents=True, exist_ok=True)
    pictures = sorted(CAPTURE.glob("*.png"))
    for picture in pictures:
        shutil.copyfile(picture, ASSETS / picture.name)
    print(f"copied {len(pictures)} captures to site/assets")
