# HumanLup Design Lab

Twenty-nine small web pieces. Each one is a single HTML file you can open in a browser. No build step, no framework.

Made by Anthony Lupo · [humanlup.com](https://humanlup.com) · X [@humanlup](https://x.com/humanlup) · IG [@humanlup.ai](https://www.instagram.com/humanlup.ai) · anthony@humanlup.com

Live: [humanlup-design-lab.vercel.app](https://humanlup-design-lab.vercel.app). Start at `showcase/index.html`. It flips through all of them.

## The pieces

| Lab | Name | What it is |
|---|---|---|
| 02 | Terracotta | 138 colors, fired as little test tiles. |
| 03 | Tidal | A design language for buildings at the water's edge. The tide keeps moving. |
| 04 | Terrain | The ground is made up. The sun is not. Drag it and the shadows move. |
| 05 | Cinema | Short films cut from a few lines of text. Press play. |
| 06 | Taste | An essay on taste with a slider under it. Drag left and it edits itself down. |
| 07 | Prints | Every color gets a fingerprint. Type yours in. |
| 08 | Reflecction | A day of prompts on the left, what it says about me on the right. |
| 09 | Press L | Press L and the page becomes the canvas. |
| 10 | Glass | Glass that acts like glass. Drag a piece over the type. |
| 11 | Rare Form | One magazine issue, set four ways with nothing but type. |
| 12 | Tool Library | A neighborhood tool library. The date is the biggest thing on the page. |
| 13 | Swipe File | I counted every pixel on five sites I like. |
| 14 | Only Copy | Which repos exist only on this laptop? Red is the only copy. |
| 15 | No Script | An issue about CSS with no JavaScript on the page. |
| 16 | Field Notes | My notes on the LLM wiki idea, as 71 pages on a ring. |
| 17 | Set Board | A week of route setting for a climbing gym, on one board. |
| 18 | One Line | How I work, drawn one line each time a job runs. |
| 19 | Seven Grays | Seven grays, one black and a dither made with only CSS. |
| 20 | Your Line | Draw one line and the headline moves out of its way. |
| 21 | Let's Talk | A contact page with no form. Change three sentences and it writes the email. |
| 23 | Call Sheet | A call sheet for a prompt. Fill five lines. |
| 24 | Grow | What if a brand could grow? More flowers than it needs. |
| 25 | Eight | A style guide where every box sits on an 8 px line. |
| 26 | Any Color | Every dot is a different color at the same lightness. Type on it. |
| 27 | One Card | One social card that holds at any shape. Drag the corner. |
| 28 | Take the L | Two Ls make a W. Tap anywhere. |
| 29 | O'clock | A clock you count. Bumps are the hour, the dot is the minute. |
| 30 | Nosy | A page full of little guys that watch your cursor. Sit still and they drift off. |
| 31 | Fold | A sheet of paper. Drag it and it folds, and it keeps the creases. |

## What is in a folder

- `NNN-name/index.html` the piece
- `NNN-name/preview.jpg` a screenshot
- `NNN-name/card.jpg` a 1080 × 1350 social card
- `NNN-name/POST.md` a caption

## Other folders

- `showcase/` the page that flips through everything. `build.py` rebuilds it.
- `_social/` wide cards, all captions in one file, and `card.js`, which makes the cards.
- `_video/` `clip.js` makes a 1080 × 1920 clip of any piece with the HumanLup outro. `VIDEO-PROMPT.md` is the prompt that runs it.
- `_tools/meta.py` stamps author and share tags into every page. Run it with a site address once the pages have a home.

## How these were made

This is an automated build. I gave Claude (Fable 5.2) a folder of my old experiments and one standing prompt, and it ran every hour on a schedule. Over 47 runs, November 9 to 14, 2026, each run:

- picked one old file and read all of it
- made something new from the idea, as one HTML file
- checked it in a real browser at desktop and phone size before saving
- wrote down what it got wrong and what the next run should do better

My taste notes became rules it followed from then on. 31 pieces came out of it; 29 are here and two stayed private. I steered between runs and picked what shipped.

© 2026 Anthony Lupo. Fonts load from Google Fonts.
