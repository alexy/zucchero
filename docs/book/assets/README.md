# Zucchero Book Artwork

The cover and headboard are derived from the user-supplied Venetian Zucchero
performance montage. The source screenshot itself is not redistributed here;
the checked-in `source/` files are the two edited artwork bases produced for
this edition.

`zucchero-cover.png` is the canonical 1800 × 2880 cover. It carries the exact
Italian title, English subtitle, byline `Alexy Khrabrov con Zucchero`, and the
canonical First Pair Press mask from
`~/src/firstpair/logo/firstpair-publisher-mask.png`.

`zucchero-headboard.png` is the canonical 2400 × 1350 wide blog/library hero.
It keeps the left third quiet for page copy. It intentionally has no embedded
type or logo because the First Pair library adds the book title, description,
and dark accessibility gradient at runtime and center-crops the image on small
screens.

The renderer samples a light warm ink directly from the cover palette, tints
the neutral publisher mask with that color, and follows First Pair's documented
cover placement and opacity guidance. It uses Baskerville from macOS for exact,
deterministic text rather than asking an image model to render words.

Render with an environment that already provides Pillow; Pillow is deliberately
not part of the book build:

```sh
python3 tools/render_book_art.py
```

The production run used the bundled Codex artifact Python runtime:

```sh
/Users/alexy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  tools/render_book_art.py
```

## Image-generation prompts

Cover base:

> Recompose the supplied layered photograph into a polished portrait 5:8 book
> cover. Preserve the recognizable musician in the tall hat at the instrument
> and microphone, Piazza San Marco and basilica architecture, reflected
> Venetian city layers, and the warm sepia-olive double-exposure atmosphere.
> Keep quiet space above and below for deterministic typography. Add no text,
> logo, watermark, border, people, objects, UI, or invented architecture.

Headboard base:

> Refine the supplied layered photograph into a polished wide 16:9 editorial
> headboard. Preserve the musician, instrument, microphone, Piazza San Marco,
> basilica, Venetian reflections, and warm timeworn double-exposure mood.
> Place the musician in the center-right third, keep the left third quieter for
> page copy, remove the screenshot border, and add no text, logo, watermark,
> people, objects, UI, or invented architecture.
