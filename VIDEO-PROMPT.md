# HumanLup Design Lab · the clip prompt

One prompt. Paste it into Claude Code (or Cowork) opened on `~/Projects/archive/_revival`. Change the piece numbers on the first line and send.

Three clips already made this way are in `_video/out/` (28 Two Ls, 30 Nosy, 31 Fold) so you can see what it gives before running it.

---

```
Make social clips for HumanLup Design Lab pieces: [ALL, or numbers like 24 29 30].

Where things are
- Pieces: ./NNN-slug/index.html. Caption for each: ./NNN-slug/POST.md. Card colors and titles: ./_social/card-jobs-*.json and ./showcase/build.py (PIECES).
- Clip maker: ./_video/clip.js with ./_video/stage.html. Jobs in ./_video/jobs.json. Read the comment at the top of clip.js first. Three jobs are already there as examples.
- Skip 001 and 022. They are private.

How to make each clip
1. Open the piece in a browser at 476 x 620 and find the one move that shows it off. A drag, a tap, a key, or just letting it run. One idea per clip, 8 to 14 seconds before the outro.
2. Add a job to jobs.json: slug lab-NN-name, file, nn, title (one or two words, same as the card), ground, ink, accent from the card job, and the acts. Start with the piece already doing something inside the first second. End on its best frame and hold it for one second.
3. Run `node _video/clip.js _video/jobs.json`. It steps the page one frame at a time, so the clip is smooth on any machine, and it ends with the HumanLup outro (checkers climb, ink fills, one line runs in, takes a loop and lands as the rule under HumanLup, then "ideas | projects | craft", "Design Lab NN", humanlup.com and @humanlup). Do not rebuild the outro per clip. If it needs to change, change stage.html once.
4. Pull 8 frames from the mp4 into one contact sheet and look at it. If the piece sits still, the pointer covers the good part, or the title is cut off, fix the acts and run it again. Do this before any sound.

Sound, with the ElevenLabs plugin
5. Music: one bed for the whole series so the clips feel like a set. Generate a 20 second instrumental loop: warm, minimal, a little playful, around 100 bpm, soft kick, round bass, one plucked or mallet voice, no vocals, nothing epic. Save it as _video/sound/bed.mp3 and reuse it. Make a new one only if I ask.
6. Outro hit: one short sound for the moment the name lands (a soft low thump with a small click on top, under one second). Save as _video/sound/hit.mp3 and reuse it.
7. Touch sounds: for each tap or drag in the acts, a quiet paper or wood tick at that time. Sound effects, not music. Keep them at about a third of the bed's volume.
8. Voice is off by default. If I say "with voice", read the first sentence of that piece's POST.md caption in my ElevenLabs voice, start it at second one, and duck the bed under it.
9. Mix with ffmpeg: bed from zero, fade in 0.3 s, drop the bed 6 dB when the outro starts, hit at outro start plus 2.1 s (when the line lands), fade everything out over the last 0.4 s. Loudness to -14 LUFS. Write _video/out/lab-NN-name.mp4 (1080 x 1920, 30 fps, H.264, AAC). Keep the silent one beside it as lab-NN-name.silent.mp4.

If a piece cannot be driven by clip.js (needs a real microphone, a file drop, hover states that only fire on a real pointer), use my cap skill to record that one by hand at the same framing, then run only the outro and sound steps on it. Tell me which ones went that way.

Also make, for each clip
- A 1080 x 1350 version for the Instagram grid: same clip, crop the stage evenly top and bottom, do not squash it.
- A poster frame: lab-NN-name.jpg, taken from the best frame, not the first.
- A line in _video/POSTS-VIDEO.md: the caption from POST.md cut to one sentence, in first person, plain. End with "HumanLup Design Lab NN". On X tag @humanlup. On Instagram tag @humanlup.ai. No hashtags unless I ask.

Rules
- The clip is about the new piece. Nothing in it about old builds, where it came from, or how it was made.
- The name on screen is HumanLup. The sign-off is "Built by Lupo". Never Lupo Studios.
- Text on screen is the title and the number. Nothing else gets added.
- Do not post anything. Do not push anything. Show me the contact sheets and the list of files when done.
- If something fails, say which piece and why, and keep going with the rest.
```

---

## Why this way and not screen recording

You asked if there is a better way to do it in code. There is, and it is what `_video/clip.js` does.

- A screen recording depends on the machine. Dropped frames, a stray cursor, a notification. Here the page clock is held and moved one thirtieth of a second at a time, with a screenshot per step, so every clip is frame-perfect and the same every run.
- The pointer path is written down in `jobs.json`. Want the drag slower, or to end on a different frame? Change a number and run it again. No retakes.
- The frame around the piece is the same design as the cards (title, number, checkered strip), so a clip and its card look like one set.
- The outro is part of the stage page. One place to change it for all clips.
- It needs Node, Playwright and ffmpeg. Nothing paid. ElevenLabs is only for sound.

What it does not do: sound (that is the ElevenLabs half of the prompt), and pieces that need a real mic or a real file drop. Those are what cap is for.

Not checked by me: what your cap skill does exactly. I could not see it from here, so the prompt only leans on it as the fallback recorder.
