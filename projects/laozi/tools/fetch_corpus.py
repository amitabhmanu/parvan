"""Fetch the Laozi witnesses from Chinese Wikisource into a gitignored corpus/.

    uv run python tools/fetch_corpus.py

Wikisource rather than ctext.org: ctext's API requires a registered key, and its HTML is not
offered for bulk reuse. Wikisource is CC-BY-SA, has a documented API, and - the reason it is
the right source here rather than merely an available one - it keeps the witnesses as
SEPARATE PAGES rather than collapsing them into one text with an apparatus. That is the shape
this project needs, because for the Laozi the witnesses are the evidence.

Polite by construction: a descriptive User-Agent per Wikimedia's robot policy, one request at
a time, and a pause between them. Each file is written with its sha256 recorded in
corpus/MANIFEST.json so a later run can prove it is reading the same bytes.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://zh.wikisource.org/w/api.php"
UA = "parvan-research/0.1 (textual-dating research; contact via repository)"
PAUSE = 3.0

ROOT = Path(__file__).resolve().parents[1] / "corpus"

# Every witness of the Laozi that Wikisource holds as constituted text, plus the received
# vulgate. The commentaries are deliberately NOT fetched: this project dates witnesses, and a
# Tang or Ming commentator's text is a reception fact, not a witness to the early Laozi.
WITNESSES = {
    "wangbi": ("道德經 (王弼本)", "Wang Bi recension with his commentary, Wei-Jin 3rd c. CE"),
    "mawangdui": ("老子 (帛書本)", "Mawangdui silk manuscripts A and B, tomb sealed 168 BCE"),
    # The standalone page is a red link; the Laozi slips live inside the whole-tomb
    # corpus, under the heading 老子（甲乙丙）. The adapter extracts that section.
    "guodian": ("郭店楚墓竹簡", "Guodian tomb corpus incl. Laozi A/B/C, tomb closed c. 300 BCE"),
    "collated": ("老子 (帛書校勘版)", "Mawangdui A+B collated, lacunae filled by the editors"),
}


def api(**params) -> dict:
    params.setdefault("format", "json")
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as fh:
        return json.load(fh)


def wikitext(title: str) -> tuple[str, str] | None:
    """The raw wikitext of one page, or None if the page does not exist."""
    d = api(action="query", prop="revisions", rvprop="content", rvslots="main",
            titles=title, redirects=1)
    page = next(iter(d.get("query", {}).get("pages", {}).values()), {})
    if "revisions" not in page:
        return None
    return page["title"], page["revisions"][0]["slots"]["main"]["*"]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, dict] = {}

    for key, (title, note) in WITNESSES.items():
        for attempt in range(4):
            try:
                got = wikitext(title)
                break
            except urllib.error.HTTPError as exc:      # noqa: F821
                if exc.code != 429 or attempt == 3:
                    raise
                wait = PAUSE * (attempt + 2)
                print(f"  {key}: rate-limited, waiting {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
        else:
            got = None

        if got is None:
            print(f"{key:<11} MISSING on Wikisource ({title})")
            manifest[key] = {"title": title, "status": "missing", "note": note}
            time.sleep(PAUSE)
            continue

        resolved, text = got
        path = ROOT / f"{key}.wiki"
        path.write_text(text, encoding="utf-8")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        manifest[key] = {
            "title": resolved, "file": path.name, "chars": len(text),
            "sha256": digest, "note": note,
            "source": f"https://zh.wikisource.org/wiki/{urllib.parse.quote(resolved)}",
            "license": "CC BY-SA 4.0",
        }
        print(f"{key:<11} {resolved:<20} {len(text):>7} chars  {digest[:12]}")
        time.sleep(PAUSE)

    (ROOT / "MANIFEST.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest: {ROOT / 'MANIFEST.json'}")


if __name__ == "__main__":
    main()
