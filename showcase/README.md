# HumanLup Design Lab · showcase

One page that flips through the pieces like the social cards: name, screenshot, one line, number. The page takes each piece's colors.

- `index.html` is built by `build.py` from `template.html`. Images are in `shots/`. "Open it" goes to `../NNN-slug/index.html`.
- `build.py` also writes `project.html` (small images inside the file, no links) for the Graveyard Shift project as `revivals/000-design-lab.html`. It needs Pillow.
- To add a piece: 1440 by 900 screenshot in `shots/NNN-slug.jpg`, one row in `PIECES` (name, ground, ink, title color, one line), run `python3 build.py`. The build stops if a color pair is too low in contrast.
- Left out on purpose: 001 (real names), 022 (still about the old page).
- Sources: every piece here pairs with its own `SOURCE.md` in its folder. This page has no archive source of its own.
