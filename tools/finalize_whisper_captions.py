#!/usr/bin/env python3
"""Create study captions from mlx_whisper SRT outputs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / "work"
CAPTIONS_DIR = ROOT / "captions"
TRANSLATIONS_DIR = ROOT / "translations"
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ']+")


GLOSSARY = {
    "a": "to",
    "accende": "lights",
    "accendi": "you-light",
    "acceso": "lit",
    "adesso": "now",
    "addirittura": "even",
    "agli": "to-the",
    "al": "to-the",
    "amore": "love",
    "andiamo": "we-go",
    "andranno": "they-will-go",
    "anima": "soul",
    "attimo": "moment",
    "bacio": "kiss",
    "balordi": "ruffians",
    "bambino": "child",
    "bel": "beautiful",
    "bella": "beautiful",
    "bisogno": "need",
    "bocca": "mouth",
    "brillanti": "shining",
    "buio": "dark",
    "buono": "good",
    "caduti": "fallen",
    "caduto": "fallen",
    "calare": "set",
    "camminato": "walked",
    "c'è": "there-is",
    "ceccato": "[unclear]",
    "che": "that",
    "cielo": "sky",
    "cime": "peaks",
    "ci": "there/it",
    "codardi": "cowards",
    "col": "with-the",
    "come": "like",
    "con": "with",
    "così": "so",
    "cuore": "heart",
    "dammi": "give-me",
    "danzare": "to-dance",
    "da": "from/as",
    "dal": "from-the",
    "dei": "of-the",
    "del": "of-the",
    "dentro": "inside",
    "di": "of",
    "dirsi": "to-say-to-oneself",
    "dolore": "pain",
    "dove": "where",
    "dovunque": "wherever",
    "e": "and",
    "è": "is",
    "festa": "party",
    "fiore": "flower",
    "fondo": "bottom/depth",
    "freddi": "you-chill",
    "fu": "was",
    "fughe": "escapes",
    "gelson": "Gelson",
    "gelsonino": "Gelsonino",
    "gioia": "joy",
    "giorni": "days",
    "giordano": "Jordan",
    "ha": "has",
    "ho": "I-have",
    "i": "the",
    "il": "the",
    "illimitato": "unlimited",
    "illumini": "you-light-up",
    "immenso": "immense",
    "in": "in",
    "intorno": "around",
    "l'altro": "the-other",
    "l'anima": "the-soul",
    "la": "the",
    "le": "the",
    "lo": "it/the",
    "luce": "light",
    "lucida": "lucid",
    "mi": "me",
    "mio": "my",
    "mondo": "world",
    "nebbia": "fog",
    "nel": "in-the",
    "nei": "in-the",
    "nell'oscurità": "in-the-darkness",
    "nella": "in-the",
    "noi": "we/us",
    "non": "not",
    "occhi": "eyes",
    "ognuno": "everyone",
    "oltre": "beyond",
    "oscuro": "dark",
    "odore": "smell",
    "paradiso": "paradise",
    "pazzi": "madmen",
    "pensa": "thinks",
    "per": "for/through",
    "perché": "because",
    "perduto": "lost",
    "pianto": "weeping",
    "più": "more",
    "poi": "then",
    "prego": "I-pray/please",
    "profano": "profane",
    "proprio": "just/exactly",
    "qualcosa": "something",
    "quello": "that",
    "questo": "this",
    "quiete": "quiet",
    "quotidiano": "daily",
    "ritorni": "returns",
    "rive": "banks/shores",
    "sacro": "sacred",
    "sai": "you-know",
    "sate": "[unclear]",
    "sé": "himself/herself",
    "sei": "you-are",
    "senti": "you-feel",
    "sento": "I-feel",
    "sera": "evening",
    "si": "itself/one",
    "siamo": "we-are",
    "sole": "sun",
    "solo": "alone/only",
    "sogno": "I-dream",
    "son": "I-am",
    "spara": "shoots/fires",
    "spirit": "spirit",
    "spirito": "spirit",
    "sto": "I-am",
    "strade": "streets",
    "sulle": "on-the",
    "te": "you",
    "ti": "you",
    "tormento": "torment",
    "troppo": "too-much",
    "tuo": "your",
    "tuoi": "your",
    "tutto": "all",
    "un": "a",
    "una": "a",
    "vano": "vain",
    "vecchio": "old",
    "vedere": "to-see",
    "vedo": "I-see",
    "vero": "true",
    "visto": "seen",
    "volo": "flight",
    "vorrei": "I-would-like",
    "vuole": "takes/wants",
}

ENGLISH_WORDS = {
    "baby",
    "crowd",
    "cry",
    "don't",
    "i",
    "lost",
    "lord",
    "me",
    "my",
    "oh",
    "say",
    "somebody",
    "sometime",
    "take",
    "the",
    "to",
    "way",
    "yeah",
}


def parse_srt(path: Path) -> list[tuple[str, str, list[str]]]:
    blocks = []
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        blocks.append((lines[0], lines[1], lines[2:]))
    return blocks


def normalize_line(line: str) -> str:
    return " ".join(WORD_RE.findall(line.casefold()))


def looks_english(line: str) -> bool:
    words = [word.casefold() for word in WORD_RE.findall(line)]
    if not words:
        return False
    english_hits = sum(1 for word in words if word in ENGLISH_WORDS)
    italian_marks = bool(re.search(r"[àèéìòù]", line.casefold()))
    return not italian_marks and english_hits / len(words) >= 0.6


def gloss_line(line: str) -> str | None:
    if looks_english(line):
        return None
    glosses = []
    for word in WORD_RE.findall(line):
        key = word.casefold()
        glosses.append(GLOSSARY.get(key, f"?{word}?"))
    return " ".join(glosses)


def clean_blocks(blocks: list[tuple[str, str, list[str]]], max_consecutive: int) -> list[tuple[str, str, list[str]]]:
    cleaned = []
    previous = ""
    count = 0
    for _, timing, lines in blocks:
        text = " ".join(lines).strip()
        normalized = normalize_line(text)
        if not normalized:
            continue
        if normalized == previous:
            count += 1
        else:
            previous = normalized
            count = 1
        if count > max_consecutive:
            continue
        cleaned.append((str(len(cleaned) + 1), timing, lines))
    return cleaned


def render(blocks: list[tuple[str, str, list[str]]]) -> tuple[str, str, str]:
    srt_parts = []
    translation_parts = []
    english_parts = []
    for index, timing, lines in blocks:
        srt_parts.append(index)
        srt_parts.append(timing)
        for line in lines:
            srt_parts.append(line)
            gloss = gloss_line(line)
            if gloss is not None:
                srt_parts.append(gloss)
                translation_parts.append(f"{line}\n{gloss}\n")
                english_parts.append(gloss)
            else:
                translation_parts.append(f"{line}\n")
        srt_parts.append("")
    return (
        "\n".join(srt_parts).rstrip() + "\n",
        "\n".join(translation_parts).rstrip() + "\n",
        "\n".join(english_parts).rstrip() + "\n",
    )


def finalize_one(yt_id: str, max_consecutive: int) -> None:
    source = WORK_DIR / yt_id / "whisper" / f"{yt_id}.srt"
    if not source.exists():
        raise SystemExit(f"Missing Whisper SRT: {source}")
    blocks = clean_blocks(parse_srt(source), max_consecutive)
    srt, translation, english = render(blocks)

    CAPTIONS_DIR.mkdir(parents=True, exist_ok=True)
    TRANSLATIONS_DIR.mkdir(parents=True, exist_ok=True)
    work_final = WORK_DIR / yt_id / "final"
    work_final.mkdir(parents=True, exist_ok=True)

    (CAPTIONS_DIR / f"{yt_id}.srt").write_text(srt, encoding="utf-8")
    (work_final / f"{yt_id}.word-by-word.srt").write_text(srt, encoding="utf-8")
    (work_final / f"{yt_id}.word-by-word.txt").write_text(translation, encoding="utf-8")
    (work_final / f"{yt_id}.english-word-gloss-only.txt").write_text(english, encoding="utf-8")
    (TRANSLATIONS_DIR / f"{yt_id}.word-by-word.txt").write_text(translation, encoding="utf-8")
    (TRANSLATIONS_DIR / f"{yt_id}.english-word-gloss-only.txt").write_text(english, encoding="utf-8")
    print(f"{yt_id}: wrote {CAPTIONS_DIR / f'{yt_id}.srt'} ({len(blocks)} blocks)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("yt_ids", nargs="*", help="YouTube IDs to finalize; defaults to every work/*/whisper/*.srt")
    parser.add_argument("--max-consecutive", type=int, default=3)
    args = parser.parse_args()

    yt_ids = args.yt_ids
    if not yt_ids:
        yt_ids = sorted(path.parent.parent.name for path in WORK_DIR.glob("*/whisper/*.srt"))
    for yt_id in yt_ids:
        finalize_one(yt_id, args.max_consecutive)


if __name__ == "__main__":
    main()
