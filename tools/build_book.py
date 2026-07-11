#!/usr/bin/env python3
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import os
import shutil
import subprocess
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "docs" / "book"
BUILD_DIR = BOOK_DIR / "build"
DIST_DIR = BOOK_DIR / "dist"
PRIVATE_DIR = BOOK_DIR / "private"
STEM = "zucchero"
TITLE = "Imparare l'italiano con Zucchero"
SUBTITLE = "Learn Italian with Zucchero"
SOURCE_REPO = "https://github.com/alexy/zucchero"
LIBRARY_ENTRY = "https://firstpair.org/#zucchero"


def run(args: list[str]) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def read_rows() -> list[dict[str, str]]:
    with (BOOK_DIR / "lyric-index.tsv").open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def lyric_index_markdown() -> str:
    rows = read_rows()
    headers = ["Canzone", "ID", "Formato", "Unità"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| --- | --- | --- | ---: |",
    ]

    for row in rows:
        lines.append(
            "| {title} | `{youtube_id}` | {format} | {units} |".format(
                **row
            )
        )

    local_note = (
        "\n\nLe fonti locali inventariate sono in `lyrics/`; i sottotitoli di studio "
        "sono in `captions/` e `video/done/`. Questi percorsi restano locali e "
        "fuori dal repository pubblico."
    )
    return "\n".join(lines) + local_note


def private_lyrics_markdown() -> str:
    if os.environ.get("INCLUDE_LOCAL_LYRICS") != "1":
        return ""

    rows = read_rows()
    lines = [
        "## Appendice privata: testi bilingui locali",
        "",
        "Questa appendice è generata solo quando `INCLUDE_LOCAL_LYRICS=1`. "
        "È destinata allo studio privato e non alla pubblicazione.",
        "",
    ]

    for row in rows:
        lyric_path = ROOT / row["local_lyric_file"]
        lines.extend([f"### {row['title']}", ""])

        if not lyric_path.exists():
            lines.extend([f"_File locale mancante: `{row['local_lyric_file']}`_", ""])
            continue

        lines.append(f"_Fonte locale: `{row['local_lyric_file']}`_")
        lines.append("")
        lines.append("```text")
        lines.append(lyric_path.read_text(encoding="utf-8").strip())
        lines.append("```")
        lines.append("")

    return "\n".join(lines)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_size(path: Path) -> int:
    return path.stat().st_size


def write_generated_manuscript() -> Path:
    source = (BOOK_DIR / "manuscript.md").read_text(encoding="utf-8")
    generated = source.replace("<!-- LYRIC_INDEX -->", lyric_index_markdown())
    generated = generated.replace("<!-- PRIVATE_LYRICS -->", private_lyrics_markdown())
    output = BUILD_DIR / "manuscript.generated.md"
    output.write_text(generated, encoding="utf-8")
    return output


def build_chapters(markdown: Path) -> Path:
    chapters_dir = DIST_DIR / f"{STEM}-chapters"
    zip_path = BUILD_DIR / f"{STEM}-chapters.zip"
    shutil.rmtree(chapters_dir, ignore_errors=True)
    run(
        [
            "pandoc",
            str(markdown),
            "--metadata-file",
            str(BOOK_DIR / "metadata.yaml"),
            "--from",
            "markdown",
            "--to",
            "chunkedhtml",
            "--standalone",
            "--embed-resources",
            "--toc",
            "--toc-depth=2",
            "--split-level=1",
            "--chunk-template=chapter-%n.html",
            "--output",
            str(zip_path),
        ]
    )
    chapters_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(chapters_dir)
    return chapters_dir


def write_version(version: str, artifacts: list[Path], chapters_dir: Path) -> None:
    today = dt.date.today().isoformat()
    versioned_pdf = f"{STEM}-{version}.pdf"
    versioned_epub = f"{STEM}-{version}.epub"
    lines = [
        "# Learn Italian with Zucchero Version",
        "",
        f"- title: {TITLE}",
        f"- subtitle: {SUBTITLE}",
        f"- title_stem: {STEM}",
        f"- version: {version}",
        f"- build_date: {today}",
        f"- source_repo: {SOURCE_REPO}",
        f"- library_entry: {LIBRARY_ENTRY}",
        f"- stable_pdf: {STEM}.pdf",
        f"- stable_epub: {STEM}.epub",
        f"- stable_html: {STEM}.html",
        f"- chapters_dir: {STEM}-chapters",
        f"- pdf_link: {versioned_pdf}",
        f"- epub_link: {versioned_epub}",
        "",
        "## Public Boundary",
        "",
        "This public edition describes the method and inventories local lyric files without reproducing complete copyrighted song lyrics.",
        "",
        "## Artifacts",
        "",
        "| File | Bytes | SHA-256 |",
        "| --- | ---: | --- |",
    ]

    for artifact in artifacts:
        lines.append(f"| `{artifact.name}` | {file_size(artifact)} | `{sha256(artifact)}` |")

    chapter_files = sorted(p for p in chapters_dir.rglob("*") if p.is_file())
    chapter_hash = hashlib.sha256()
    for path in chapter_files:
        rel = path.relative_to(chapters_dir).as_posix()
        chapter_hash.update(rel.encode())
        chapter_hash.update(b"\0")
        chapter_hash.update(sha256(path).encode())
        chapter_hash.update(b"\0")
    lines.append(
        f"| `{chapters_dir.name}/` | {len(chapter_files)} files | `{chapter_hash.hexdigest()}` |"
    )
    lines.append("")
    (DIST_DIR / "VERSION.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    version = os.environ.get("BOOK_VERSION") or f"0.1.0-{dt.date.today():%Y%m%d}"
    include_private = os.environ.get("INCLUDE_LOCAL_LYRICS") == "1"
    global DIST_DIR
    if include_private:
        DIST_DIR = PRIVATE_DIR

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    markdown = write_generated_manuscript()

    pdf = DIST_DIR / f"{STEM}.pdf"
    epub = DIST_DIR / f"{STEM}.epub"
    html = DIST_DIR / f"{STEM}.html"

    common = [
        "pandoc",
        str(markdown),
        "--metadata-file",
        str(BOOK_DIR / "metadata.yaml"),
        "--toc",
        "--toc-depth=2",
    ]
    run(common + ["--pdf-engine=typst", "--output", str(pdf)])
    run(
        common
        + [
            "--css",
            str(BOOK_DIR / "book.css"),
            "--output",
            str(epub),
        ]
    )
    run(
        common
        + [
            "--to",
            "html",
            "--standalone",
            "--embed-resources",
            "--css",
            str(BOOK_DIR / "book.css"),
            "--output",
            str(html),
        ]
    )
    chapters = build_chapters(markdown)
    write_version(version, [pdf, epub, html], chapters)

    print(f"Built {pdf}")
    print(f"Built {epub}")
    print(f"Built {html}")
    print(f"Built {chapters}")
    print(f"Built {DIST_DIR / 'VERSION.md'}")


if __name__ == "__main__":
    main()
