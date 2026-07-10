# Learn Italian with Zucchero

Scripts and book source for a local Italian-study workflow built around
Zucchero songs.

- First Pair library entry: [Learn Italian with Zucchero](https://firstpair.org/#zucchero)
- Online reader: [firstpair.org/read/zucchero/](https://firstpair.org/read/zucchero/)
- Scripts repository: [github.com/alexy/zucchero](https://github.com/alexy/zucchero)
- Public book source: [docs/book](docs/book)

## Boundary

The local workspace may contain media, transcripts, subtitles, translations, and
lyric files supplied by the user for private study. Those files are ignored by
Git and are not redistributed by this public scripts repository.

The public book describes the method and inventories the local lyric files that
have been studied so far. It does not reproduce full copyrighted song lyrics.

## Caption Workflow

Put intake videos directly in `video/`. The YouTube ID is read from a filename
suffix such as `[U3VqULD_pk4].mp4`.

```sh
python3 tools/batch_whisper_videos.py transcribe
python3 tools/finalize_whisper_captions.py
python3 tools/batch_whisper_videos.py move-done
```

Finished sidecars live next to the archived videos:

```text
video/done/Title [YT_ID].mp4
video/done/Title [YT_ID].srt
```

For lyric-aligned songs, use the track-specific builders captured in
[AGENTS.md](AGENTS.md). The source lyric file is the text authority; Whisper and
Parakeet are timing evidence.

## Book Build

Build the public article/book package with:

```sh
python3 tools/build_book.py
```

The build writes:

```text
docs/book/dist/zucchero.pdf
docs/book/dist/zucchero.epub
docs/book/dist/zucchero.html
docs/book/dist/zucchero-chapters/
docs/book/dist/VERSION.md
```

First Pair owns the public catalog, Blob URLs, hosted readers, and deployment.
This repo owns the scripts, method article, and local build manifest.
