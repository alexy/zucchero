# Learn Italian with Zucchero Book

This directory contains the public-safe book source for *Learn Italian with
Zucchero*. The book is an Italian article about the method, with the English
subtitle as a translation.

The public edition inventories the local lyric files and caption builders
without reproducing complete copyrighted lyrics. Full lyric text, media,
transcripts, and generated captions remain local working inputs outside Git.

Build:

```sh
python3 tools/build_book.py
```

The generated artifacts in `dist/` are delivered to First Pair under the
`zucchero` catalog slug.
