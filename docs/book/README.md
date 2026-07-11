# Learn Italian with Zucchero Book

This directory contains the public-safe book source for *Learn Italian with
Zucchero*. The book is an Italian article about the method, with an English
subtitle and sentence-by-sentence English translations underneath the Italian
text.

The public edition inventories the local lyric files and caption builders
without reproducing complete copyrighted lyrics. Full lyric text, media,
transcripts, and generated captions remain local working inputs outside Git.

Build:

```sh
./build.sh
```

The generated artifacts in `dist/` are delivered to First Pair under the
`zucchero` catalog slug.

Private local-only builds can include a generated lyrics appendix from a lyrics
directory:

```sh
./build.sh --config book.private.build.json
```

That command uses First Pair's unified book builder. Its prepare hook writes
`docs/book/private/song-list.tsv`,
`docs/book/private/song-list.md`, and
`docs/book/private/lyrics-appendix.md`, then rebuilds the private PDF, EPUB,
HTML, chapters, and `VERSION.md` under `docs/book/private/`.
