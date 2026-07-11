# Zucchero Book Build

The public book uses the shared FirstPair toolchain and the checked-in
`book.build.json` configuration:

```sh
docs/book/build.sh
```

`tools/prepare_public_book.py` wraps the existing Python manuscript generator
with private lyrics disabled. FirstPair then builds and verifies PDF, EPUB,
single-file HTML, chapter HTML, stable artifacts, versioned aliases, and the
machine-readable `VERSION.md` under `docs/book/dist/`.

The private lyrics workflow remains separate:

```sh
python3 tools/build_book_with_lyrics.py lyrics
```

Private artifacts stay under ignored `docs/book/private/` and must never be
passed to the FirstPair library publisher.
