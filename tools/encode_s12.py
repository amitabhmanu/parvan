"""Encode the Ramayana inventory from docs/dating-sanskrit-epics.md section 12.

The store is one file per record so that disagreement is a diff (D-4). The *encoding* is a
table so that it is reviewable as an argument rather than as sixty files. Run:

    uv run python tools/encode_s12.py

Provenance discipline: anchors and horizons are `attested` and name the artefact or material
record they rest on. Every interpretive claim is `asserted` against the source synthesis,
because that document summarises scholarship rather than citing loci. This split is what
makes falsifier F-6 meaningful - strip the asserted tier and see what survives.

Years are signed integers, astronomical numbering (D-6).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "store"
DOC = "docs/dating-sanskrit-epics.md"


def src(row: str) -> dict:
    return {"tier": "asserted", "source": f"{DOC} section 12, row: {row}"}


def att(locus: str) -> dict:
    return {"tier": "attested", "locus": locus}


# --------------------------------------------------------------------------------------
# ANCHORS - dated by non-textual means. These are the only nodes that fix absolute time.
# Literary works are NOT anchors: their dates are themselves textually derived, so they are
# encoded as work-states below. The distinction is the whole point of the anchor concept.
# --------------------------------------------------------------------------------------

ANCHORS = [
    ("anc.veal-kantel", "Veal Kantel inscription, Cambodia", 590, 610, "epigraphic-citation",
     ["internal-linguistic", "internal-structural", "internal-doctrinal"], True,
     "Veal Kantel stele, Cambodia; endows recitation of the Ramayana"),
    ("anc.cham-valmiki", "Cham inscription dedicating a temple to Valmiki", 600, 700,
     "epigraphic-citation", ["internal-linguistic", "internal-structural"], True,
     "Cham inscription, temple dedication to Valmiki"),
    ("anc.liudu-jijing", "Liudu jijing, tr. Kang Senghui", 251, 251, "foreign-catalogue",
     ["internal-linguistic", "internal-structural", "internal-doctrinal", "documentary"], True,
     "Chinese Buddhist translation catalogues, Kang Senghui, 251 CE"),
    ("anc.deogarh", "Gupta Ramayana panels, Deogarh", 400, 550, "art-historical",
     ["internal-linguistic", "internal-structural"], True,
     "Dasavatara temple reliefs, Deogarh"),
    ("anc.nagarjunakonda", "Ramayana terracottas, Nagarjunakonda", 200, 400, "art-historical",
     ["internal-linguistic", "internal-structural"], True,
     "Nagarjunakonda site reliefs and terracottas"),
    ("anc.baroda-archetype", "Baroda critical edition archetype", 320, 600, "palaeography",
     ["internal-doctrinal"], False,
     "Baroda critical edition apparatus; archetype of the surviving manuscripts"),
]

# Material horizons. Wide, contested intervals of their own, which must propagate rather
# than collapse to a point.
HORIZONS = [
    ("hor.horse-chariot", "Domestic horse and spoked-wheel chariot in South Asia",
     -2100, -1900, "archaeological-horizon",
     "Sintashta chariot burials; Pontic-Caspian domestic lineage; absence in Harappan faunal assemblages"),
    ("hor.iron-india", "Iron metallurgy in South Asia", -1300, -1200, "archaeological-horizon",
     "Earliest iron-bearing levels, South Asian excavation record"),
    ("hor.ayodhya-urban", "Substantial urban occupation at Ayodhya", -700, -600,
     "archaeological-horizon", "Ayodhya excavation levels; no substantial occupation earlier"),
    ("hor.kosala-power", "Kosala as a major political power", -750, -650,
     "archaeological-horizon", "Mahajanapada-period settlement and fortification record"),
    ("hor.roman-denarius", "Roman denarius in circulation reaching India", 1, 100,
     "numismatic", "Roman coin finds in South Asian hoards; denarius issue chronology"),
    ("hor.yavana-presence", "Greek presence in the northwest", -330, -300,
     "archaeological-horizon", "Alexander's campaign and successor settlement; Indo-Greek horizon"),
    ("hor.deccan-contact", "Sustained northern contact with the Deccan", -450, -350,
     "archaeological-horizon", "Pre-Mauryan and Mauryan-era southern material contact"),
    ("hor.mauryan-capital", "Pataliputra as the imperial centre", -320, -180,
     "archaeological-horizon", "Pataliputra excavation; Nanda-Mauryan imperial phase"),
]

# Other literary works, as work-states. Their intervals are asserted, not anchored.
WORK_STATES = [
    ("ws.asvaghosa", "Asvaghosa, naming Valmiki as a metrical innovator", 50, 200,
     "Asvaghosa naming Valmiki as a metrical innovator"),
    ("ws.kalidasa", "Kalidasa, Raghuvamsa", 380, 460, "Kalidasa's Raghuvamsa"),
    ("ws.bhatti", "Bhatti, Bhattikavya", 600, 700,
     "Bhatti's Bhattikavya, later source of the Old Javanese poem"),
    ("ws.paumacariyam", "Vimalasuri, Paumacariyam", 1, 500,
     "Vimalasuri's Paumacariyam arguing against Valmiki"),
    ("ws.bhasa", "Bhasa, Pratimanataka and Abhisekanataka", 100, 400,
     "Bhasa's Pratimanataka, Abhisekanataka"),
    ("ws.dasaratha-jataka", "Dasaratha Jataka (verses)", -300, -100, "Dasaratha Jataka"),
    ("ws.mbh.ramopakhyana", "Ramopakhyana within the Mahabharata", None, None,
     "Ramopakhyana in the Mahabharata apparently depending on Valmiki"),
    ("ws.ram.251ce", "The Rama narrative as it stood when translated into Chinese", None, None,
     "Liudu jijing: Rama narrative in Chinese"),
    ("ws.ram.600ce", "The Ramayana as endowed for recitation at Veal Kantel", None, None,
     "Veal Kantel: Ramayana endowed for recitation in Cambodia"),
    # --- second sources for concept referents ----------------------------------------
    # D-2 refused these referents at degree 1 on the first encoding pass. That refusal is
    # correct and is a finding in its own right: a concept referent touched by one text
    # cannot propagate. The document names the other sources, so they are encoded here.
    # Intervals are left open where the only available date would be a conclusion of
    # section 11 - importing that would make V-1 circular.
    ("ws.brhadaranyaka", "Brhadaranyaka and Chandogya Upanisads", -700, -500,
     "Karma, rebirth, moksa - emerging in the Brhadaranyaka and Chandogya c. 700-500 BCE"),
    ("ws.manusmrti", "Manusmrti", -200, 200,
     "Sambuka episode's hardened caste orthodoxy - floor alongside Manusmrti material"),
    ("ws.mbh.carvaka", "Carvaka's cameo in the Mahabharata", None, None,
     "Materialism as a named opponent - Carvaka's hostile cameo in the Mahabharata"),
    ("ws.mbh.core", "The Bharata war narrative", None, None,
     "Ramayana never mentions the Pandavas or the Bharata war"),
]

# Ramayana strata. Extents follow the critical edition's kanda.sarga.sloka addressing where
# section 12 localises a claim, and are left open where it does not.
STRATA = [
    ("ram.core", "Core, books 2-6 (Ayodhya through Yuddha) - the adikavya", ["Ram.2", "Ram.6"]),
    ("ram.bala", "Balakanda (book 1)", ["Ram.1"]),
    ("ram.uttara", "Uttarakanda (book 7)", ["Ram.7"]),
    ("ram.kiskindha-geog", "Kiskindhakanda geography, with Yavana and Saka lists", ["Ram.4"]),
    ("ram.yuddha-ending", "Yuddhakanda divine-assembly ending", ["Ram.6"]),
    ("ram.jabali", "Jabali's Lokayata speech", ["Ram.2"]),
    ("ram.sambuka", "Sambuka episode", ["Ram.7"]),
    ("ram.dinara", "Passages using dinara", []),  # section 12 does not localise these
]

# Referents. `text_derived` is not a judgement about importance - it records that the
# referent's date comes from texts, which bars it from anchoring the strata it constrains (G-4).
REFERENTS = [
    # id, label, class, emergence(floor, ceiling), text_derived, provenance
    ("ref.horse-chariot", "Horse-and-chariot warfare", "technology", -2100, -1900, False,
     att("Sintashta chariot burials; domestic horse lineage; Harappan faunal absence")),
    ("ref.iron-weaponry", "Iron weaponry (krsna-ayas)", "technology", -1300, -1200, False,
     att("Earliest iron-bearing levels, South Asian excavation record")),
    ("ref.fortified-ayodhya", "Ayodhya as a great fortified metropolis", "institution",
     -700, -600, False, att("Ayodhya excavation levels")),
    ("ref.kosala-power", "Kosala as a major power", "institution", -750, -650, False,
     att("Mahajanapada settlement and fortification record")),
    ("ref.dinara", "Dinara, the Roman denarius", "technology", 1, 100, False,
     att("Roman coin finds in South Asian hoards")),
    ("ref.yavana-saka", "Yavanas and Sakas as known peoples", "institution", -330, -300, False,
     att("Indo-Greek and Saka horizon in the northwest")),
    ("ref.deccan-knowledge", "Southern flora, fauna and place-knowledge", "institution",
     -450, -350, False, att("Material record of northern contact with the Deccan")),
    # Text-derived: dated from literature, so barred from anchoring (G-4).
    ("ref.post-vedic-grammar", "Post-Vedic, non-Paninian grammar", "concept", None, None, True,
     src("Post-Vedic grammar: no accent, collapsed tenses, absolutive chaining")),
    ("ref.karma-rebirth-moksa", "Karma, rebirth and moksa as an assumed framework", "concept",
     None, None, True, src("Karma, rebirth, moksa as assumed framework")),
    ("ref.lokayata-school", "Lokayata as a named school worth refuting", "concept",
     None, None, True, src("Jabali's Lokayata speech")),
    ("ref.avatara-theology", "Avatara theology", "concept", None, None, True,
     src("Avatara theology in Bala and Uttara")),
    ("ref.caste-hardening", "Birth-fixed caste orthodoxy", "concept", None, None, True,
     src("Sambuka episode's hardened caste orthodoxy")),
    ("ref.valmiki-as-author", "Valmiki as a named author", "concept", None, None, False,
     src("Asvaghosa naming Valmiki as a metrical innovator")),
    ("ref.classical-kavya-style", "Mature classical kavya style (long compounds)", "concept",
     None, None, True, src("Short compounds; no mature kavya style")),
    ("ref.bharata-war-narrative", "The Bharata war narrative in circulation", "concept",
     None, None, True, src("Ramayana never mentions the Pandavas or the Bharata war")),
    ("ref.pataliputra-imperial", "Pataliputra as the recognised imperial capital",
     "institution", -320, -300, False,
     att("Pataliputra excavation record; Nanda-Mauryan imperial phase")),
]

# Edges. Each row: id, type, from, to, method, section-12 row, extras.
EDGES = [
    # --- floors: the strata presuppose these referents -------------------------------
    ("e.001", "presupposes", "ram.core", "ref.horse-chariot", "realia-floor",
     "Horses and chariots throughout", {}),
    ("e.002", "presupposes", "ram.core", "ref.iron-weaponry", "realia-floor",
     "Iron weaponry", {}),
    ("e.003", "presupposes", "ram.core", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    ("e.004", "presupposes", "ram.bala", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    ("e.005", "presupposes", "ram.uttara", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    ("e.006", "presupposes", "ram.dinara", "ref.dinara", "realia-floor",
     "Dinara, the Roman denarius", {}),
    ("e.007", "presupposes", "ram.core", "ref.fortified-ayodhya", "realia-floor",
     "Ayodhya as a great fortified metropolis", {}),
    ("e.008", "presupposes", "ram.core", "ref.karma-rebirth-moksa", "doctrinal-discontinuity",
     "Karma, rebirth, moksa as assumed framework", {}),
    ("e.009", "presupposes", "ram.core", "ref.kosala-power", "realia-floor",
     "Kosala as a major power", {}),
    ("e.010", "presupposes", "ram.kiskindha-geog", "ref.yavana-saka", "realia-floor",
     "Yavanas and Sakas in the Kiskindha geography", {}),
    ("e.011", "presupposes", "ram.jabali", "ref.lokayata-school", "doctrinal-discontinuity",
     "Jabali's Lokayata speech", {}),
    ("e.012", "presupposes", "ram.bala", "ref.avatara-theology", "doctrinal-discontinuity",
     "Avatara theology in Bala and Uttara", {}),
    ("e.013", "presupposes", "ram.uttara", "ref.avatara-theology", "doctrinal-discontinuity",
     "Avatara theology in Bala and Uttara", {}),
    ("e.014", "presupposes", "ram.sambuka", "ref.caste-hardening", "doctrinal-discontinuity",
     "Sambuka episode's hardened caste orthodoxy", {}),
    ("e.015", "presupposes", "ram.kiskindha-geog", "ref.deccan-knowledge", "realia-floor",
     "Southern flora, fauna, place-knowledge", {}),

    # --- referents attested by the material record ------------------------------------
    ("e.020", "attests", "hor.horse-chariot", "ref.horse-chariot", "archaeological-horizon",
     "Horses and chariots throughout", {}),
    ("e.021", "attests", "hor.iron-india", "ref.iron-weaponry", "archaeological-horizon",
     "Iron weaponry", {}),
    ("e.022", "attests", "hor.ayodhya-urban", "ref.fortified-ayodhya", "archaeological-horizon",
     "Ayodhya as a great fortified metropolis", {}),
    ("e.023", "attests", "hor.kosala-power", "ref.kosala-power", "archaeological-horizon",
     "Kosala as a major power", {}),
    ("e.024", "attests", "hor.roman-denarius", "ref.dinara", "numismatic",
     "Dinara, the Roman denarius", {}),
    ("e.025", "attests", "hor.yavana-presence", "ref.yavana-saka", "archaeological-horizon",
     "Yavanas and Sakas in the Kiskindha geography", {}),
    ("e.026", "attests", "hor.deccan-contact", "ref.deccan-knowledge", "archaeological-horizon",
     "Southern flora, fauna, place-knowledge", {}),
    ("e.027", "attests", "ws.asvaghosa", "ref.valmiki-as-author", "literary-citation",
     "Asvaghosa naming Valmiki as a metrical innovator", {}),
    ("e.028", "attests", "anc.cham-valmiki", "ref.valmiki-as-author", "epigraphic-citation",
     "Cham inscription dedicating a temple to Valmiki", {}),
    ("e.029", "attests", "ws.paumacariyam", "ref.valmiki-as-author", "literary-citation",
     "Vimalasuri's Paumacariyam arguing against Valmiki", {}),
    ("e.030", "attests", "ws.kalidasa", "ref.classical-kavya-style", "metrical-statistics",
     "Short compounds; no mature kavya style", {}),
    ("e.031", "attests", "ws.bhatti", "ref.classical-kavya-style", "metrical-statistics",
     "Bhatti's Bhattikavya", {}),
    # Second sources that lift the concept referents above D-2's degree threshold.
    ("e.032", "attests", "ws.brhadaranyaka", "ref.karma-rebirth-moksa",
     "doctrinal-discontinuity", "Karma, rebirth, moksa as assumed framework", {}),
    ("e.033", "attests", "ws.manusmrti", "ref.caste-hardening", "doctrinal-discontinuity",
     "Sambuka episode's hardened caste orthodoxy", {}),
    ("e.034", "attests", "ws.mbh.carvaka", "ref.lokayata-school", "doctrinal-discontinuity",
     "Materialism as a named opponent", {}),
    ("e.035", "attests", "ws.mbh.core", "ref.bharata-war-narrative", "literary-citation",
     "Ramayana never mentions the Pandavas or the Bharata war", {}),

    # --- ceilings from absence: the core lacks what later works have -------------------
    ("e.040", "absent-from", "ram.core", "ref.classical-kavya-style", "absence",
     "Short compounds; no mature kavya style", {"lag_min_years": 0}),
    ("e.041", "absent-from", "ram.core", "ref.avatara-theology", "doctrinal-discontinuity",
     "Books 1 and 7 divinize Rama; books 2-6 do not", {"lag_min_years": 0}),
    # The only pre-CE ceiling anywhere in section 12's table, and it is scored 2.
    ("e.043", "absent-from", "ram.core", "ref.pataliputra-imperial", "absence",
     "Pataliputra absent as imperial capital - soft ceiling c. 300 BCE on the geographic frame",
     {"lag_min_years": 0, "confidence": 0.4}),
    ("e.044", "attests", "hor.mauryan-capital", "ref.pataliputra-imperial",
     "archaeological-horizon", "Pataliputra absent as imperial capital", {}),
    ("e.042", "absent-from", "ram.core", "ref.bharata-war-narrative", "absence",
     "Ramayana never mentions the Pandavas or the Bharata war", {"lag_min_years": 0,
                                                                "confidence": 0.5}),

    # --- ceilings from external attestation of the work ------------------------------
    ("e.050", "contains", "ws.ram.600ce", "ram.core", "epigraphic-citation",
     "Veal Kantel: Ramayana endowed for recitation in Cambodia", {"confidence": 0.95}),
    ("e.051", "contains", "ws.ram.600ce", "ram.bala", "epigraphic-citation",
     "Veal Kantel: Ramayana endowed for recitation in Cambodia", {"confidence": 0.9}),
    ("e.052", "contains", "ws.ram.600ce", "ram.uttara", "epigraphic-citation",
     "Veal Kantel: Ramayana endowed for recitation in Cambodia", {"confidence": 0.9}),
    ("e.053", "attests", "anc.veal-kantel", "ref.valmiki-as-author", "epigraphic-citation",
     "Veal Kantel: Ramayana endowed for recitation in Cambodia", {}),
    ("e.054", "contains", "ws.ram.251ce", "ram.core", "foreign-catalogue",
     "Liudu jijing: Rama narrative in Chinese (lean, Jataka-like)", {"confidence": 0.6}),
    ("e.055", "cites", "anc.veal-kantel", "ws.ram.600ce", "epigraphic-citation",
     "Veal Kantel: Ramayana endowed for recitation in Cambodia", {"lag_min_years": 1}),
    ("e.056", "cites", "anc.liudu-jijing", "ws.ram.251ce", "foreign-catalogue",
     "Liudu jijing: Rama narrative in Chinese", {"lag_min_years": 1}),
    ("e.057", "cites", "ws.kalidasa", "ram.core", "literary-citation",
     "Kalidasa's Raghuvamsa", {}),
    ("e.058", "cites", "ws.bhatti", "ram.core", "literary-citation",
     "Bhatti's Bhattikavya, later source of the Old Javanese poem", {}),
    ("e.059", "cites", "ws.bhasa", "ram.core", "literary-citation",
     "Bhasa's Pratimanataka, Abhisekanataka (attribution contested)", {"confidence": 0.4}),
    ("e.060", "cites", "ws.mbh.ramopakhyana", "ram.core", "literary-citation",
     "Ramopakhyana in the Mahabharata apparently depending on Valmiki",
     {"direction_uncertain": True, "confidence": 0.7}),
    ("e.061", "cites", "anc.deogarh", "ram.core", "art-historical",
     "Nagarjunakonda and Deogarh Ramayana panels", {"lag_min_years": 1}),
    ("e.062", "cites", "anc.nagarjunakonda", "ram.core", "art-historical",
     "Nagarjunakonda and Deogarh Ramayana panels", {"lag_min_years": 1}),
    ("e.063", "cites", "anc.baroda-archetype", "ram.core", "palaeography",
     "Baroda critical edition archetype", {"lag_min_years": 1}),

    # --- internal ordering: two independent methods, same conclusion ------------------
    # This is the path-disjointness case. Same endpoints, different method lineage, so the
    # two edges genuinely multiply rather than merely repeat.
    ("e.070", "frames", "ram.uttara", "ram.core", "structural-seam",
     "Uttarakanda frame where Valmiki appears and the twins recite the poem", {}),
    ("e.071", "frames", "ram.uttara", "ram.core", "metrical-statistics",
     "Vipula ratios separating books statistically", {}),
    ("e.072", "frames", "ram.bala", "ram.core", "doctrinal-discontinuity",
     "Books 1 and 7 divinize Rama; books 2-6 do not", {}),
    ("e.073", "frames", "ram.bala", "ram.core", "metrical-statistics",
     "Vipula ratios separating books statistically", {}),
    ("e.074", "frames", "ram.yuddha-ending", "ram.core", "structural-seam",
     "Yuddhakanda divine-assembly ending", {}),
    ("e.075", "frames", "ram.sambuka", "ram.core", "structural-seam",
     "Sambuka episode within the Uttarakanda", {}),
    ("e.076", "frames", "ram.dinara", "ram.core", "structural-seam",
     "Dinara passages as later insertions", {"confidence": 0.6}),
]


def emit() -> None:
    for sub in ("nodes/anchors", "nodes/horizons", "nodes/referents", "nodes/strata",
                "nodes/work-states", "edges"):
        d = STORE / sub
        if d.exists():
            for f in d.glob("*.yaml"):
                f.unlink()
        d.mkdir(parents=True, exist_ok=True)

    def dump(path: Path, data: dict) -> None:
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, allow_unicode=True, sort_keys=False, width=100)

    for nid, label, lo, hi, method, indep, holdout, locus in ANCHORS:
        dump(STORE / "nodes/anchors" / f"{nid}.yaml", {
            "id": nid, "kind": "anchor", "label": label,
            "interval": {"floor": lo, "ceiling": hi},
            "dating_method": method, "independent_of": indep,
            "holdout_eligible": holdout, "provenance": att(locus),
        })

    for nid, label, lo, hi, method, locus in HORIZONS:
        dump(STORE / "nodes/horizons" / f"{nid}.yaml", {
            "id": nid, "kind": "horizon", "label": label,
            "interval": {"floor": lo, "ceiling": hi},
            "dating_method": method, "provenance": att(locus),
        })

    for nid, label, lo, hi, row in WORK_STATES:
        rec = {"id": nid, "kind": "work-state", "label": label}
        if lo is not None:
            rec["interval"] = {"floor": lo, "ceiling": hi}
        rec["provenance"] = src(row)
        dump(STORE / "nodes/work-states" / f"{nid}.yaml", rec)

    for nid, label, extent in STRATA:
        dump(STORE / "nodes/strata" / f"{nid}.yaml", {
            "id": nid, "kind": "stratum", "label": label,
            "work": "ramayana", "extent": extent,
        })

    for nid, label, cls, lo, hi, derived, prov in REFERENTS:
        rec = {"id": nid, "kind": "referent", "label": label, "class": cls}
        if lo is not None:
            rec["emergence"] = {"floor": lo, "ceiling": hi}
        rec["text_derived"] = derived
        rec["provenance"] = prov
        dump(STORE / "nodes/referents" / f"{nid}.yaml", rec)

    for eid, etype, frm, to, method, row, extras in EDGES:
        rec = {"id": eid, "type": etype, "from": frm, "to": to, "method": method}
        rec.update(extras)
        rec["provenance"] = src(row)
        dump(STORE / "edges" / f"{eid}.yaml", rec)

    n = len(ANCHORS) + len(HORIZONS) + len(WORK_STATES) + len(STRATA) + len(REFERENTS)
    print(f"emitted {n} nodes, {len(EDGES)} edges into {STORE}")


if __name__ == "__main__":
    if not STORE.exists():
        raise SystemExit(f"no store at {STORE}")
    del shutil
    emit()
