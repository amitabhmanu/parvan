"""Encode the scored inventories from docs/dating-sanskrit-epics.md, sections 11 and 12.

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

# REMOVED, see docs/mbh-promotion.md: section 11's "Greek-derived astrological vocabulary"
# row, scored 4. The row names no terms; section 3 supplies hora, kendra and drekkana as the
# Greek loans into Sanskrit jyotisa. None of the three occurs anywhere in the Mahabharata,
# archetypal or apparatus, under any spelling. All 363 raw hora hits are ghora ("terrible"),
# ahoratra ("day-and-night") or kathora ("harsh"); the three word-initial ones are elided
# ahoratra. All four kendr hits are sandhi artefacts - janaka+indra, baka+indra. drekkana
# returns zero under every spelling tried. The floor cannot be checked as the document
# states it, and the obvious candidates fail.


def src(row: str) -> dict:
    return {"tier": "asserted", "source": f"{DOC} scored inventory, row: {row}"}


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
    # --- section 11 anchors -------------------------------------------------------
    ("anc.agathocles", "Silver coins of Agathocles, Ai-Khanoum", -190, -180, "numismatic",
     ["internal-linguistic", "internal-structural", "internal-doctrinal"], True,
     "Ai-Khanoum excavation; Vasudeva-Krsna with wheel and conch, Samkarsana-Balarama "
     "with plough and club"),
    ("anc.spitzer", "Spitzer manuscript, Kizil", 200, 300, "palaeography",
     ["internal-linguistic", "internal-doctrinal"], True,
     "Palm-leaf fragments from Kizil; parvan list differs from the received one"),
    ("anc.heliodorus", "Heliodorus pillar, Besnagar", -115, -105, "epigraphic-citation",
     ["internal-linguistic", "internal-structural"], True,
     "Besnagar pillar inscription; Vasudeva as god of gods"),
    ("anc.khoh-plates", "Khoh copper plates of Sarvanatha", 500, 520, "epigraphic-citation",
     ["internal-linguistic", "internal-structural", "internal-doctrinal"], True,
     "Khoh plates; the hundred-thousand-verse collection compiled by Vyasa"),
    ("anc.imprecatory-grants", "Imprecatory verses quoted in land grants", 450, 600,
     "epigraphic-citation", ["internal-linguistic", "internal-structural"], True,
     "Standard imprecatory verses in hundreds of copper-plate grants from the 5th c."),
    ("anc.poona-archetype", "Poona critical edition archetype", 320, 600, "palaeography",
     ["internal-doctrinal"], False, "Poona critical edition apparatus"),
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
    ("hor.yavana-presence", "Greek presence in the northwest", -330, -300,
     "archaeological-horizon", "Alexander's campaign and successor settlement; Indo-Greek horizon"),
    ("hor.deccan-contact", "Sustained northern contact with the Deccan", -450, -350,
     "archaeological-horizon", "Pre-Mauryan and Mauryan-era southern material contact"),
    # ONSET, not duration. Grounding pins a referent's emergence to its horizon's interval,
    # so a horizon must express the window in which the thing BEGAN, not how long it lasted.
    # This was first encoded as [-320, -180], the span of the imperial phase, which made the
    # absence argument yield "predates 180 BCE" - the date Pataliputra stopped being an
    # unremarkable thing to omit, which is not the claim. Corrected to the accession window.
    # Every other horizon in this file was already an onset window; this was the only one.
    ("hor.mauryan-capital", "Pataliputra becomes the recognised imperial centre", -350, -300,
     "archaeological-horizon",
     "Pataliputra excavation; Nanda accession through early Mauryan consolidation"),
    ("hor.huna-india", "Huna presence in South Asia", 450, 550, "archaeological-horizon",
     "Hunnic incursion horizon; Gupta-period numismatic and epigraphic record"),
    ("hor.qin-china", "The Qin state, source of Cina", -221, -206, "foreign-catalogue",
     "Qin dynastic records"),
    ("hor.stupa-eduka", "Stupa and reliquary-mound construction", -250, -150,
     "archaeological-horizon", "Early stupa horizon, post-Asokan"),
    ("hor.massed-elephants", "Massed elephant corps in a fourfold army", -500, -350,
     "archaeological-horizon", "Magadhan-era military record; Greek accounts of Indian armies"),
    ("hor.temple-image-worship", "Temple and image worship", -200, -100,
     "archaeological-horizon", "Earliest shrine and image archaeology"),
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
    ("ws.panini", "Panini, Astadhyayi", -370, -330,
     "Panini on devotees of Vasudeva and Arjuna"),
    ("ws.patanjali", "Patanjali, Mahabhasya", -160, -140,
     "Patanjali on staged Kamsa performances"),
    ("ws.asvalayana", "Asvalayana Grhyasutra", -400, -250,
     "Asvalayana Grhyasutra naming Bharata and Mahabharata"),
    ("ws.samkhyakarika", "Isvarakrsna, Samkhyakarika", 350, 450,
     "Unsystematized Samkhya, pre-Samkhyakarika"),
    ("ws.manusmrti", "Manusmrti", -200, 200,
     "Sambuka episode's hardened caste orthodoxy - floor alongside Manusmrti material"),
]

# Ramayana strata. Extents follow the critical edition's kanda.sarga.sloka addressing where
# section 12 localises a claim, and are left open where it does not.
STRATA = [
    ("ram.core", "Core, books 2-6 (Ayodhya through Yuddha) - the adikavya", ["Ram.2", "Ram.6"]),
    # --- Mahabharata strata, section 11 and the stratification in section 4 --------
    ("ws.mbh.core", "MBh heroic narrative: quarrel, dicing, exile, embassy, the eighteen days",
     ["MBh.2", "MBh.11"]),
    ("ws.mbh.carvaka", "MBh didactic mass: Santi and Anusasana", ["MBh.12", "MBh.13"]),
    ("ws.mbh.ramopakhyana", "MBh anthology layer, including the Ramopakhyana", ["MBh.3"]),
    ("mbh.theological", "MBh theological layer: Gita, Narayaniya, avatara doctrine", ["MBh.6"]),
    ("mbh.late-peoples", "MBh passages naming Hunas, Cinas, Romakas", []),
    ("ram.bala", "Balakanda (book 1)", ["Ram.1"]),
    ("ram.uttara", "Uttarakanda (book 7)", ["Ram.7"]),
    ("ram.kiskindha-geog", "Kiskindhakanda geography, with Yavana and Saka lists", ["Ram.4"]),
    # Extent narrowed from the whole of book 6 to the stuti complex. An extraction agent
    # checking e.041 found the Brahma-stuti of Ram.6.105 sitting inside ram.core's declared
    # extent and reported the absence claim as contradicted. It is contradicted only because
    # both strata claimed book 6: this passage is the retrofit seam section 4 already names,
    # and it needs its own boundaries if the carve-out is to mean anything.
    ("ram.yuddha-ending", "Yuddhakanda divine-assembly ending and the Brahma-stuti",
     ["Ram.6.105", "Ram.6.107"]),
    ("ram.jabali", "Jabali's Lokayata speech", ["Ram.2"]),
    ("ram.sambuka", "Sambuka episode", ["Ram.7"]),
]

# Referents. `text_derived` is not a judgement about importance - it records that the
# referent's date comes from texts, which bars it from anchoring the strata it constrains (G-4).
REFERENTS = [
    # id, label, class, emergence(floor, ceiling), text_derived, provenance
    ("ref.horse-chariot", "Horse-and-chariot warfare", "technology", None, None, False,
     att("Sintashta chariot burials; domestic horse lineage; Harappan faunal absence")),
    ("ref.iron-weaponry", "Iron weaponry (krsna-ayas)", "technology", None, None, False,
     att("Earliest iron-bearing levels, South Asian excavation record")),
    ("ref.fortified-ayodhya", "Ayodhya as a great fortified metropolis", "institution",
     None, None, False, att("Ayodhya excavation levels")),
    ("ref.kosala-power", "Kosala as a major power", "institution", None, None, False,
     att("Mahajanapada settlement and fortification record")),
    ("ref.yavana-saka", "Yavanas and Sakas as known peoples", "institution", None, None, False,
     att("Indo-Greek and Saka horizon in the northwest")),
    ("ref.deccan-knowledge", "Southern flora, fauna and place-knowledge", "institution",
     None, None, False, att("Material record of northern contact with the Deccan")),
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
     "institution", None, None, False,
     att("Pataliputra excavation record; Nanda-Mauryan imperial phase")),
    # --- section 11 referents -----------------------------------------------------
    ("ref.hunas", "Hunas as a known people", "institution", None, None, False,
     att("Hunnic incursion horizon, Gupta-period record")),
    ("ref.cinas", "Cinas as a known people", "institution", None, None, False,
     att("Qin dynastic records")),
    ("ref.eduka-polemic", "Eduka and stupa construction as a target of polemic", "institution",
     None, None, False, att("Early stupa horizon, post-Asokan")),
    ("ref.massed-elephant-corps", "Massed elephant corps in a fourfold army", "institution",
     None, None, False, att("Magadhan-era military record; Greek accounts")),
    ("ref.temple-image-worship", "Temple and image worship", "institution", -200, -100,
     False, att("Earliest shrine and image archaeology")),
    ("ref.classical-samkhya", "Classical Samkhya's fixed twenty-five-tattva scheme", "concept",
     None, None, True, src("Unsystematized Samkhya, pre-Samkhyakarika")),
    # Not text-derived: the Khoh plates and the Spitzer fragment attest a work under this
    # name by non-textual means, so it may anchor (G-4).
    ("ref.mbh-as-named-work", "A work circulating under the name Mahabharata", "concept",
     None, None, False, src("Asvalayana Grhyasutra naming Mahabharata")),
    # SPLIT, on the network's own diagnosis. Encoded first as one referent with emergence
    # pinned to the Agathocles coins at [-190, -180], which produced a negative cycle:
    # Panini attests the cult at c. 330 BCE, 150 years before the coins. The witness path
    # named all three constraints. The error was mine and it is the one R-4 exists to
    # prevent - an attestation caps emergence from above and never floors it - but the
    # deeper fault was conflation, so the fix is R-10's split operator.
    #
    # Section 11 already keeps these apart: Panini gives a ceiling on "the cult pairing",
    # the coins on "the divine pair with epic attributes". Two referents, two dates.
    ("ref.vasudeva-arjuna-cult", "The Vasudeva-Arjuna cult pairing", "concept",
     None, None, False, att("Besnagar epigraphy; Panini on devotees of Vasudeva and Arjuna")),
    ("ref.vasudeva-epic-attributes",
     "The divine pair with epic attributes - wheel and conch, plough and club", "concept",
     None, None, False, att("Ai-Khanoum coin types of Agathocles")),
]

# Edges. Each row: id, type, from, to, method, section-12 row, extras.
EDGES = [
    # --- floors: the strata presuppose these referents -------------------------------
    ("e.001", "presupposes", "ram.core", "ref.horse-chariot", "realia-floor",
     "Horses and chariots throughout",
     {"prov": att("Ram.2.090.008 - rathasvagajasambadham yattair yuktam padatibhih; "
                  "an army thronged with chariots, horses and elephants, joined by foot")}),
    ("e.002", "presupposes", "ram.core", "ref.iron-weaponry", "realia-floor",
     "Iron weaponry",
     {"prov": att("Ram.6.086.006 - ayasam parigham grhya; an iron bludgeon wielded in "
                  "battle. Cf. Ram.6.060.022, 6.067.006 sruvam karsnayasam (black iron)")}),
    ("e.003", "presupposes", "ram.core", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    ("e.004", "presupposes", "ram.bala", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    ("e.005", "presupposes", "ram.uttara", "ref.post-vedic-grammar", "linguistic-stratigraphy",
     "Post-Vedic grammar", {}),
    # CORRECTED against the critical edition, and this one was carrying the core's floor.
    # The canonical description of Ayodhya as a great fortified metropolis - gates, engines,
    # high watchtowers, hundreds of sataghni, a deep moat, "unassailable by others" - is
    # Ram.1.005.010-013, in BALAKANDA. Book 2, Ayodhya's own book and part of the core, has
    # zero sataghni and zero gopura; its one moat-and-rampart passage (2.074.017-018)
    # describes the army's road camps, and 2.064.001 describes Rajagrha. The core's entire
    # fortification datum is the single word attalakesu in a list at 2.006.011, which does
    # not support the referent as defined.
    ("e.007", "presupposes", "ram.bala", "ref.fortified-ayodhya", "realia-floor",
     "Ayodhya as a great fortified metropolis [misattributed - see docs/promotion-slice.md]",
     {"prov": att("Ram.1.005.010-013 - kapatatoranavatim, sarvayantrayudhavatim, "
                  "uccattaladhvajavatim sataghnisatasamkulam, durgagambhiraparikham "
                  "durgam anyair durasadam")}),
    ("e.008", "presupposes", "ram.core", "ref.karma-rebirth-moksa", "doctrinal-discontinuity",
     "Karma, rebirth, moksa as assumed framework", {}),
    # VERIFIED against the critical edition, and it holds - the first floor constraint on
    # the core that survives contact with the text. The dating claim rests on Ram.4.039.021,
    # where Kosala appears in a mahajanapada roster with Videha, Kasi, Magadha, Pundra and
    # Vanga. Note the cross-check: book 4's geography knows Indian mahajanapadas and no
    # Greeks or Scythians at all, which is the profile of a pre-Hellenistic core geography.
    ("e.009", "presupposes", "ram.core", "ref.kosala-power", "realia-floor",
     "Kosala as a major power",
     {"prov": att("Ram.4.039.021 - brahmamalan videhams ca malavan kasikosalan / "
                  "magadhams ca mahagraman pundran vangams tathaiva ca; Kosala in a "
                  "mahajanapada roster. Supporting: Ram.2.047.011 bhoksyaty adhirajavat "
                  "(as an overlord); Ram.2.043.007 kosalan kosalesvarah; Ram.5.041.007 and "
                  "Ram.6.031.066 kosalendrasya ramasya, envoys naming Kosala at Lanka")}),
    # RETRACTED CORRECTION, then re-corrected. This edge was moved to ram.bala on a search
    # that returned zero for foreign ethnonyms in Kiskindhakanda. That search was wrong: it
    # used citation-form stems, which case-ending sandhi hides. 'yavana' does not occur
    # because the text has 'yavanams'; the truncated stem 'yavan' finds Ram.4.042.011.
    # Section 12's attribution was right and mine was not. Restored.
    ("e.010", "presupposes", "ram.kiskindha-geog", "ref.yavana-saka", "realia-floor",
     "Yavanas and Sakas in the Kiskindha geography",
     {"prov": att("Ram.4.042.011 - kambojan yavanams caiva sakan arattakan api; Sugriva's "
                  "western-direction speech. Cf. Ram.4.042.010 mleccha, pulinda; "
                  "Ram.4.042.012 cina; Ram.4.040.013 andhra, colan pandyan sakeralan")}),
    ("e.010b", "presupposes", "ram.bala", "ref.yavana-saka", "realia-floor",
     "Yavanas and Sakas - also present in Balakanda",
     {"prov": att("Ram.1.053.020-021, Ram.1.054.003 - pahlavan ... sakan yavanamisritan; "
                  "Vasistha's cow generating barbarian armies")}),
    ("e.011", "presupposes", "ram.jabali", "ref.lokayata-school", "doctrinal-discontinuity",
     "Jabali's Lokayata speech", {}),
    ("e.012", "presupposes", "ram.bala", "ref.avatara-theology", "doctrinal-discontinuity",
     "Avatara theology in Bala and Uttara", {}),
    ("e.013", "presupposes", "ram.uttara", "ref.avatara-theology", "doctrinal-discontinuity",
     "Avatara theology in Bala and Uttara", {}),
    ("e.014", "presupposes", "ram.sambuka", "ref.caste-hardening", "doctrinal-discontinuity",
     "Sambuka episode's hardened caste orthodoxy", {}),
    # Promoted, narrowed to the real half of Sugriva's southern-direction speech. The same
    # sarga slides into cosmography from 4.040.020 - Mount Mahendra sinking into the ocean,
    # the serpent-city Bhogavati, the realm of Yama at the edge of the earth - which is not
    # Deccan realia and is excluded. Section 12's own "grows vaguer with distance" turns out
    # to happen inside a single speech.
    ("e.015", "presupposes", "ram.kiskindha-geog", "ref.deccan-knowledge", "realia-floor",
     "Southern flora, fauna, place-knowledge",
     {"prov": att("Ram.4.040.008-019 - vindhyam, narmadam, godavarim, krsnavenim, "
                  "vidarbhan rsikams ... bangan kalingams ca, andhrams ca pundrams ca colan "
                  "pandyan sakeralan, sacandanavana (sandalwood), kaverim, tamraparnim "
                  "grahajustam (crocodile-infested), kavatam pandyanam. Excludes "
                  "4.040.020-047, mythic cosmography in the same sarga")}),

    # --- referents attested by the material record ------------------------------------
    ("e.020", "attests", "hor.horse-chariot", "ref.horse-chariot", "archaeological-horizon",
     "Horses and chariots throughout", {}),
    ("e.021", "attests", "hor.iron-india", "ref.iron-weaponry", "archaeological-horizon",
     "Iron weaponry", {}),
    ("e.022", "attests", "hor.ayodhya-urban", "ref.fortified-ayodhya", "archaeological-horizon",
     "Ayodhya as a great fortified metropolis", {}),
    ("e.023", "attests", "hor.kosala-power", "ref.kosala-power", "archaeological-horizon",
     "Kosala as a major power", {}),
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
     {"lag_min_years": 0, "confidence": 0.4,
      "prov": att("GRETIL Baroda CE, all 18761 verses: 0 hits for "
                  "/pa?[tt]aliputra|pa?[tt]alipura/ and for the diacritic-folded form. "
                  "A measured silence: re-runnable via tools/concordance.py")}),
    ("e.044", "attests", "hor.mauryan-capital", "ref.pataliputra-imperial",
     "archaeological-horizon", "Pataliputra absent as imperial capital", {}),
    # Promoted from asserted on a measured silence over the full core extent. Fifteen terms
    # at zero hits direct and diacritic-folded; eight further terms returned hits that were
    # read individually and rejected - kuru is the imperative "do!", bhima the adjective
    # "terrible", pandu the colour "pale", arjuna the tree, vyasa a substring of vyasakta.
    #
    # Confidence raised from 0.5 to 0.75. Ram.2.062.010 puts Bharata's itinerary through
    # Hastinapura, Pancala and Kurujangala: the poets knew the Kuru-Pancala region and its
    # capital as ordinary geography and still named no character, dynasty or war. Silence
    # from someone who knows the place is stronger evidence than silence from someone who
    # does not, which is what section 12's score of 3 does not distinguish.
    ("e.042", "absent-from", "ram.core", "ref.bharata-war-narrative", "absence",
     "Ramayana never mentions the Pandavas or the Bharata war",
     {"lag_min_years": 0, "confidence": 0.75,
      "prov": att("Absence search over Ram.2-6 (14130 verses), corpus/sa_rAmAyaNa.xml: "
                  "0 hits for pandava, kaurava, kauravya, kuruksetra, yudhisthira, draupadi, "
                  "duryodhana, dhrtarastra, gandiva, bhisma, abhimanyu, sanjaya, duhsasana, "
                  "hastinapura - direct and diacritic-folded. Re-runnable via "
                  "tools/concordance.py")}),

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

    # ==================================================================================
    # SECTION 11 - MAHABHARATA
    # ==================================================================================
    # Referent ids below without an "mbh" prefix are SHARED with the Ramayana inventory.
    # That sharing is the reification hypothesis under test: if it pays, the second text
    # should give ram.core a second route to one of its bounds.

    ("e.101", "presupposes", "ws.mbh.core", "ref.horse-chariot", "realia-floor",
     "Horses and spoked chariots throughout", {}),
    ("e.102", "presupposes", "ws.mbh.core", "ref.iron-weaponry", "realia-floor",
     "Iron weaponry (krsna-ayas)", {}),
    ("e.103", "presupposes", "ws.mbh.core", "ref.post-vedic-grammar",
     "linguistic-stratigraphy", "Post-Vedic grammar: no accent, collapsed tenses", {}),
    ("e.104", "presupposes", "ws.mbh.core", "ref.karma-rebirth-moksa",
     "doctrinal-discontinuity", "Karma, rebirth, moksa as framework", {}),
    ("e.105", "presupposes", "mbh.late-peoples", "ref.yavana-saka", "realia-floor", "Yavanas", {}),
    ("e.106", "presupposes", "mbh.theological", "ref.avatara-theology",
     "doctrinal-discontinuity", "Bhakti and avatara theology", {}),

    # THE SHARED CEILING. Section 11 carries the same Pataliputra row as section 12, so the
    # two texts meet at one referent. If a second path to ram.core exists, it is here.
    # Promoted, and corroborated rather than merely unopposed. The silence is measured over
    # 123,372 verses (91,573 archetypal-only), twelve searches, all zero. What lifts it above
    # an ordinary argument from absence is the positive control: Magadha's OLDER capital is
    # named repeatedly and unambiguously - Girivraja as Jarasamdha's seat where he holds rival
    # kings captive, and Rajagrha again in the tirtha catalogue. The epic's Magadhan geography
    # is not undescribed. It is described, and stops one city short.
    #
    # Confidence raised 0.4 -> 0.7. Section 11 scores this row 2 as a soft ceiling; the
    # positive control is the thing that score does not account for.
    ("e.107", "absent-from", "ws.mbh.core", "ref.pataliputra-imperial", "absence",
     "Pataliputra absent as imperial capital",
     {"lag_min_years": 0, "confidence": 0.7,
      "prov": att("Absence over MBh.2-11, 123372 verses (91573 archetypal-only): "
                  "pataliputr, patalipur, kusumapur, puspapur all 0 hits, plain, "
                  "archetypal-only and folded. Positive control: MBh.2.013.062 tena ruddha "
                  "hi rajanah sarve jitva girivraje (Jarasamdha's capital); MBh.3.082.089 "
                  "tato rajagrham gacchet tirthasevi. Excludes MBh.2.052.003 and "
                  "MBh.5.049.014, both generic 'king's house'")}),
    ("e.108", "absent-from", "ws.mbh.core", "ref.classical-kavya-style", "absence",
     "Short compounds; no mature kavya style", {"lag_min_years": 0}),

    # Promoted, and checked against the BORI apparatus - the first time that check has been
    # possible for anything. Section 11 calls the Huna floor "the latest binding floor", so
    # whether it rests on constituted text or on material the critical editors excluded is
    # the difference between a real floor and a dinara. It rests on constituted text.
    ("e.110", "presupposes", "mbh.late-peoples", "ref.hunas", "realia-floor",
     "Hunas in the peoples lists - latest binding floor",
     {"prov": att("MBh.2.047.019 - cinan hunan sakan odran; also MBh.2.029.011, "
                  "MBh.3.048.021 harahunams, MBh.6.010.064 hunah paratakaih saha, "
                  "MBh.12.312.015 cinahunanisevitan. All ARCHETYPAL - none is a star or "
                  "appendix passage. Excludes sthuna/prabhunam false positives")}),
    ("e.111", "presupposes", "mbh.late-peoples", "ref.cinas", "realia-floor", "Cinas (from Qin)",
     {"prov": att("MBh.2.023.019 - kirataih ca cinaih ca vrtah pragjyotiso 'bhavat; also "
                  "MBh.2.047.019, MBh.3.048.021. All ARCHETYPAL. Excludes aracina, pracina, "
                  "sucin false positives")}),
    # RETARGETED. Encoded against the didactic mass on my guess about where the Kali Yuga
    # material sits. It is not there - eduk returns zero across MBh.12-13. The only two
    # occurrences in the epic are MBh.3.188, Markandeya's Kali Yuga description in the Vana
    # Parva. Section 11 says "on the Kali Yuga material" and names no book; the stratum
    # assignment was mine and it was wrong.
    #
    # QUALIFICATION. Section 3 glosses this row "Anti-Buddhist", but the passage names no
    # Buddhist: bauddha, sramana and nagnaka are all zero in MBh.3.188, and its four buddh
    # hits are every one of them buddhi, "mind". The polemic is against eduka worship
    # displacing the gods, in an undifferentiated list of degeneracy signs beside sudras
    # teaching dharma and untimely rain. Reading eduka as a Buddhist reliquary mound is an
    # identification the text does not make, so the floor rests on that identification rather
    # than on the verse. Confidence 0.6.
    ("e.112", "presupposes", "ws.mbh.ramopakhyana", "ref.eduka-polemic", "realia-floor",
     "Eduka / stupa polemic - floor on the Kali Yuga material",
     {"confidence": 0.6,
      "prov": att("MBh.3.188.064 - edukan pujayisyanti varjayisyanti devatah; MBh.3.188.066 "
                  "- edukacihna prthivi na devagrhabhusita. Both ARCHETYPAL. Kali Yuga "
                  "context explicit at MBh.3.188.005. Zero hits for eduk in MBh.12-13")}),
    # Promoted on the INSTITUTION, not the animal. Elephants appear constantly and mostly
    # irrelevantly - as a city epithet (gajasahvaya = Hastinapura), as ivory, as tribute, as
    # one named tusker. What the floor needs is the military institution, and MBh.5.152
    # defines it outright.
    ("e.113", "presupposes", "ws.mbh.core", "ref.massed-elephant-corps", "realia-floor",
     "Massed elephant corps, fourfold army",
     {"prov": att("MBh.5.152.019-022 - rathasyasan dasa gaja gajasya dasa vajinah ... "
                  "aksauhiniti paryayair: the aksauhini defined, elephants a fixed arm beside "
                  "chariot, horse and foot. In use at MBh.6.058.031 anikam dasasahasram "
                  "kunjaranam / gajanikam, a 10,000-strong elephant division engaged as a "
                  "unit. In-extent archetypal: caturanga 19, gajanika 34, aksauhini 64")}),
    ("e.114", "presupposes", "ws.mbh.carvaka", "ref.temple-image-worship", "realia-floor",
     "Temple and image worship assumed", {}),

    ("e.120", "attests", "hor.huna-india", "ref.hunas", "archaeological-horizon",
     "Hunas in the peoples lists", {}),
    ("e.121", "attests", "hor.qin-china", "ref.cinas", "foreign-catalogue", "Cinas (from Qin)", {}),
    ("e.122", "attests", "hor.stupa-eduka", "ref.eduka-polemic", "archaeological-horizon",
     "Eduka / stupa polemic", {}),
    ("e.123", "attests", "hor.massed-elephants", "ref.massed-elephant-corps",
     "archaeological-horizon", "Massed elephant corps, fourfold army", {}),
    ("e.125", "attests", "hor.temple-image-worship", "ref.temple-image-worship",
     "archaeological-horizon", "Temple and image worship assumed", {}),
    ("e.126", "attests", "anc.agathocles", "ref.vasudeva-epic-attributes", "numismatic",
     "Agathocles coins, Krsna-Balarama iconography", {}),
    ("e.135", "attests", "anc.heliodorus", "ref.vasudeva-epic-attributes",
     "epigraphic-citation",
     "Heliodorus pillar wording paralleling an epic verse - quotation or commonplace?",
     {"confidence": 0.5}),
    ("e.136", "presupposes", "mbh.theological", "ref.vasudeva-epic-attributes",
     "doctrinal-discontinuity", "Bhakti and avatara theology", {}),
    ("e.127", "attests", "anc.heliodorus", "ref.vasudeva-arjuna-cult", "epigraphic-citation",
     "Heliodorus pillar wording paralleling an epic verse", {}),
    ("e.128", "attests", "ws.panini", "ref.vasudeva-arjuna-cult", "literary-citation",
     "Panini on Vasudeva-Arjuna devotees - ceiling on the cult, not on any text", {}),
    ("e.129", "attests", "ws.patanjali", "ref.vasudeva-arjuna-cult", "literary-citation",
     "Patanjali on staged Kamsa performances", {}),
    ("e.130", "attests", "ws.asvalayana", "ref.mbh-as-named-work", "literary-citation",
     "Asvalayana Grhyasutra naming Bharata and Mahabharata", {}),
    # D-2 refused this referent at degree 1 on the first combined pass. Both further
    # attesters are in the document: the Khoh plates cite the epic by name and size, and
    # the Spitzer fragment is the earliest physical witness to a work so called.
    ("e.133", "attests", "anc.khoh-plates", "ref.mbh-as-named-work", "epigraphic-citation",
     "Copper-plate grants citing the hundred-thousand-verse collection of Vyasa", {}),
    ("e.134", "attests", "anc.spitzer", "ref.mbh-as-named-work", "palaeography",
     "Spitzer manuscript parvan list - earliest physical trace, contents not yet final", {}),
    ("e.131", "attests", "ws.samkhyakarika", "ref.classical-samkhya",
     "doctrinal-discontinuity", "Unsystematized Samkhya, pre-Samkhyakarika", {}),
    ("e.132", "absent-from", "ws.mbh.carvaka", "ref.classical-samkhya",
     "doctrinal-discontinuity",
     "Unsystematized Samkhya caps the didactic layers at c. 350-400 CE", {"lag_min_years": 0}),

    ("e.140", "cites", "anc.spitzer", "ws.mbh.core", "palaeography",
     "Spitzer manuscript parvan list", {"lag_min_years": 1}),
    ("e.141", "cites", "anc.khoh-plates", "ws.mbh.carvaka", "epigraphic-citation",
     "Copper-plate grants citing the hundred-thousand-verse collection of Vyasa",
     {"lag_min_years": 1}),
    ("e.142", "cites", "anc.imprecatory-grants", "ws.mbh.carvaka", "epigraphic-citation",
     "Imprecatory verses quoted in hundreds of grants from the 5th c.", {"lag_min_years": 1}),
    ("e.143", "cites", "anc.poona-archetype", "ws.mbh.core", "palaeography",
     "Poona critical edition archetype", {"lag_min_years": 1}),
    ("e.144", "cites", "anc.veal-kantel", "ws.mbh.carvaka", "epigraphic-citation",
     "Veal Kantel: complete Bharata endowed in Cambodia", {"lag_min_years": 1}),

    ("e.150", "frames", "mbh.theological", "ws.mbh.core", "structural-seam",
     "The Gita lifts out cleanly; Sanjaya's report resumes exactly", {}),
    ("e.151", "frames", "ws.mbh.carvaka", "ws.mbh.core", "structural-seam",
     "Bhisma's death deferred thousands of verses to accommodate the didactic mass", {}),
    ("e.152", "frames", "ws.mbh.ramopakhyana", "ws.mbh.core", "structural-seam",
     "Anthology: Nala, Savitri, Ramopakhyana, tirtha catalogue", {}),
    ("e.153", "frames", "mbh.late-peoples", "ws.mbh.core", "structural-seam",
     "Peoples lists as later expansion", {"confidence": 0.7}),

    # ==================================================================================
    # GROUNDING - the missing half of `attests`
    # ==================================================================================
    # Attestation caps an emergence from above and never floors it, so before these edges
    # existed every material referent carried a hardcoded emergence interval and the
    # thirteen horizon nodes were inert: deleting an anchor changed nothing at all. Each
    # pair below derives the floor from its horizon, so anchors carry the system the way
    # the design says they should.
    ("g.020", "grounds", "hor.horse-chariot", "ref.horse-chariot", "archaeological-horizon",
     "Horses and chariots throughout", {}),
    ("g.021", "grounds", "hor.iron-india", "ref.iron-weaponry", "archaeological-horizon",
     "Iron weaponry", {}),
    ("g.022", "grounds", "hor.ayodhya-urban", "ref.fortified-ayodhya", "archaeological-horizon",
     "Ayodhya as a great fortified metropolis", {}),
    ("g.023", "grounds", "hor.kosala-power", "ref.kosala-power", "archaeological-horizon",
     "Kosala as a major power", {}),
    ("g.025", "grounds", "hor.yavana-presence", "ref.yavana-saka", "archaeological-horizon",
     "Yavanas and Sakas", {}),
    ("g.026", "grounds", "hor.deccan-contact", "ref.deccan-knowledge", "archaeological-horizon",
     "Southern flora, fauna, place-knowledge", {}),
    ("g.044", "grounds", "hor.mauryan-capital", "ref.pataliputra-imperial", "archaeological-horizon",
     "Pataliputra absent as imperial capital", {}),
    ("g.120", "grounds", "hor.huna-india", "ref.hunas", "archaeological-horizon",
     "Hunas in the peoples lists", {}),
    ("g.121", "grounds", "hor.qin-china", "ref.cinas", "foreign-catalogue",
     "Cinas (from Qin)", {}),
    ("g.122", "grounds", "hor.stupa-eduka", "ref.eduka-polemic", "archaeological-horizon",
     "Eduka / stupa polemic", {}),
    ("g.123", "grounds", "hor.massed-elephants", "ref.massed-elephant-corps", "archaeological-horizon",
     "Massed elephant corps, fourfold army", {}),
    ("g.125", "grounds", "hor.temple-image-worship", "ref.temple-image-worship", "archaeological-horizon",
     "Temple and image worship assumed", {}),
    ("g.126", "grounds", "anc.agathocles", "ref.vasudeva-epic-attributes", "numismatic",
     "Agathocles coins, Krsna-Balarama iconography", {}),
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

    # An edge whose source is a horizon or an anchor is a MATERIAL claim, and inherits that
    # node's locus. G-1 defines `attested` as pointing at a resolvable locus - a verse ID,
    # an inscription number, a coin catalogue entry, or an excavation report page - so an
    # edge resting on excavation is attested by that definition, not asserted.
    #
    # This matters more than bookkeeping. With these edges left `asserted`, stripping the
    # asserted tier for F-6 removed every grounding and the whole network went unbounded:
    # the checkable evidence appeared to support nothing at all.
    material = {n: rec for n, rec in
                [(a[0], a[7]) for a in ANCHORS] + [(h[0], h[5]) for h in HORIZONS]}

    for eid, etype, frm, to, method, row, extras in EDGES:
        rec = {"id": eid, "type": etype, "from": frm, "to": to, "method": method}
        extras = dict(extras)
        prov = extras.pop("prov", None)
        rec.update(extras)
        if prov is None and frm in material:
            prov = att(f"{frm}: {material[frm]}")
        rec["provenance"] = prov or src(row)
        dump(STORE / "edges" / f"{eid}.yaml", rec)

    n = len(ANCHORS) + len(HORIZONS) + len(WORK_STATES) + len(STRATA) + len(REFERENTS)
    print(f"emitted {n} nodes, {len(EDGES)} edges into {STORE}")


if __name__ == "__main__":
    if not STORE.exists():
        raise SystemExit(f"no store at {STORE}")
    del shutil
    emit()
