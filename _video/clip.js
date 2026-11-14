// HumanLup Design Lab clip maker. node clip.js jobs.json
// Frame-stepped, not screen-recorded: the page clock is held and moved 1/30 s at a time, so a clip comes out the same on any machine, fast or slow.
// One job per piece: {slug, file, hash?, nn, title, ground, ink, accent, outro?, wait?, acts:[...]}
// Acts play inside the framed page (476 x 620 CSS px, shown at 2x). Coordinates are in that frame, times in ms of clip time.
//   ["move",x,y,ms]  ["path",[[x,y],...],ms]  ["tap",x,y]  ["drag",x1,y1,x2,y2,ms]  ["wait",ms]  ["key","f"]  ["hide"]
// Output: out/<slug>.mp4, 1080 x 1920, 30 fps, H.264, silent. Sound goes on after (see VIDEO-PROMPT.md).
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path'); const { spawn } = require('child_process');
const OX = 64, OY = 430, S = 2, FPS = 30, DT = 1000/FPS, here = __dirname;
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2])); fs.mkdirSync(path.join(here,'out'),{recursive:true});
  const b = await chromium.launch({ args:['--allow-file-access-from-files'] });
  for (const j of jobs) {
    const ctx = await b.newContext({ viewport:{width:1080,height:1920} }); const p = await ctx.newPage();
    await p.clock.install({ time: new Date('2026-11-13T10:10:00') });
    const u = new URLSearchParams({ src:'file://'+path.resolve(here, j.file), hash:j.hash||'', title:j.title, nn:j.nn, ground:j.ground, ink:j.ink, accent:j.accent, outro:j.outro||j.accent });
    await p.goto('file://'+path.join(here,'stage.html')+'?'+u); await p.waitForTimeout(1500); await p.evaluate(() => document.fonts.ready);
    await p.clock.pauseAt(new Date('2026-11-13T10:10:05')); await p.clock.runFor(j.wait||1500);
    const out = path.join(here,'out',j.slug+'.mp4');
    const ff = spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(FPS),'-c:v','mjpeg','-i','-','-vf','format=yuv420p','-c:v','libx264','-crf','17','-preset','slow','-movflags','+faststart','-an',out],{stdio:['pipe','inherit','inherit']});
    const X = x => OX + x*S, Y = y => OY + y*S; let cx = 238, cy = 310, show = false, down = false, frames = 0;
    const step = async () => {
      await p.clock.runFor(DT);
      for (const fr of p.frames()) await fr.evaluate(dt => { for (const a of document.getAnimations()) { if (!a.__held) { a.pause(); a.__held = 1; a.__t = 0; } a.__t += dt; a.currentTime = a.__t; } }, DT).catch(()=>{});
      await p.evaluate(([x,y,show,down]) => { const t = document.getElementById('tip'); t.style.left = x+'px'; t.style.top = y+'px'; t.style.opacity = show ? .9 : 0; t.style.transform = down ? 'scale(.7)' : 'none'; }, [X(cx),Y(cy),show,down]);
      const buf = await p.screenshot({ type:'jpeg', quality:95 }); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); frames++;
    };
    const hold = async ms => { for (let k = 0; k < Math.round(ms/DT); k++) await step(); };
    const glide = async (x,y,ms) => { const n = Math.max(1, Math.round(ms/DT)), sx = cx, sy = cy; show = true;
      for (let k = 1; k <= n; k++) { const e = k/n, s = e*e*(3-2*e); cx = sx+(x-sx)*s; cy = sy+(y-sy)*s; await p.mouse.move(X(cx),Y(cy)); await step(); } };
    for (const a of j.acts) {
      if (a[0]==='move') await glide(a[1],a[2],a[3]||600);
      else if (a[0]==='path') { const per = (a[2]||2000)/a[1].length; for (const [x,y] of a[1]) await glide(x,y,per); }
      else if (a[0]==='tap') { await glide(a[1],a[2],350); down = true; await p.mouse.down(); await hold(100); await p.mouse.up(); down = false; await hold(60); }
      else if (a[0]==='drag') { await glide(a[1],a[2],350); down = true; await p.mouse.down(); await glide(a[3],a[4],a[5]||900); await p.mouse.up(); down = false; await hold(60); }
      else if (a[0]==='key') { await p.keyboard.press(a[1]); await hold(60); }
      else if (a[0]==='hide') show = false;
      else if (a[0]==='wait') await hold(a[1]);
    }
    show = false; await hold(200); p.evaluate(() => { window.outro(); }); await hold(4200);
    ff.stdin.end(); await new Promise(r => ff.on('close', r)); await ctx.close();
    console.log('done', j.slug, (frames/FPS).toFixed(1)+'s', out);
  }
  await b.close();
})();
