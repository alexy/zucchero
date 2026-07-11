# Local Lyric Sources

This directory is for private study lyric files. The repository tracks this
README only; full lyric files are ignored by Git.

## Capture Process

For each song, the working process is:

1. Search Google for `Zucchero <song title> lyrics`.
2. Use the lyric result for the original Italian.
3. Click Google's `Translate` affordance to render the English line.
4. Save the result locally as alternating English / Italian nonblank lines:

   ```text
   English translation line
   Italian lyric line
   ```

5. For Italian-only sources, use the `.it.txt` suffix instead of `.en-it.txt`.

These files support local study, timing alignment, and private builds. They are
not redistributed through GitHub or First Pair unless redistribution rights are
separately confirmed.

## Private Book Build

To include the local lyric files in a local-only copy of the book:

```sh
INCLUDE_LOCAL_LYRICS=1 python3 tools/build_book.py
```

The output goes to `docs/book/private/`, which is ignored by Git.

To generate a private appendix from this directory and rebuild the local-only
book package in one step:

```sh
python3 tools/build_book_with_lyrics.py lyrics
```

The script writes `docs/book/private/song-list.tsv`,
`docs/book/private/song-list.md`, and
`docs/book/private/lyrics-appendix.md`, then rebuilds the private PDF, EPUB,
HTML, chapters, and `VERSION.md`.
