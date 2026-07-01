#!/usr/bin/env python3
"""Download section images (Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

PEXELS: dict[str, tuple[str, str]] = {
    "hero.webp": (PEX.format(id="248444"), "Pexels #248444"),
    "promotions.webp": (PEX.format(id="248444"), "Pexels #248444"),
    "dim-sum.webp": (PEX.format(id="248444"), "Pexels #248444"),
    "slideshow-dim-sum.webp": (PEX.format(id="2338407"), "Pexels #2338407"),
    "slideshow-dumplings.webp": (PEX.format(id="247117"), "Pexels #247117"),
}

SECTIONS: dict[str, str] = {
    "promotions": "promotions.webp",
}

WEIGHTS: dict[str, str] = {
    "promotions": "1",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = WEIGHTS.get(section, "1")
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip() or "TTMenus Menu System" in body:
        body = (
            "<p><strong>The New Dim Sum King</strong> — authentic dim sum at "
            "East Gates Mall, Trincity.</p>"
        )
    text = (
        "---\n"
        'title: "The New Dim Sum King"\n'
        f"image: {img('hero.webp')}\n"
        "images:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('dim-sum.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "slideshow:\n"
        f"    - image: {img('hero.webp')}\n"
        f"    - image: {img('slideshow-dim-sum.webp')}\n"
        f"    - image: {img('slideshow-dumplings.webp')}\n"
        f"    - image: {img('promotions.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    if (IMAGES_DIR / "hero.webp").exists():
        update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos (Pexels License — free to use):\n"
        + "\n".join(dict.fromkeys(credits))
        + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
