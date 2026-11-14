// HumanLup Design Lab card maker. node card.js config.json
// Each job: {file, nn, slug, title, ground, ink, accent, wait, pre:[["click","#sel"],["press","l"],["move",x,y],["wait",ms]], portrait:"out.jpg", wide:"out.jpg"}
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const run = async (p, pre=[]) => { for (const a of pre) { if (a[0]==='click') await p.click(a[1]); else if (a[0]==='press') await p.keyboard.press(a[1]); else if (a[0]==='move') await p.mouse.move(a[1],a[2],{steps:8}); else if (a[0]==='wait') await p.waitForTimeout(a[1]); else if (a[0]==='fill') await p.fill(a[1],a[2]); else if (a[0]==='eval') await p.evaluate(a[1]); } };
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2])); const b = await chromium.launch();
  for (const j of jobs) {
    const snap = async (w,h) => { const p = await b.newPage({ viewport:{width:w,height:h}, deviceScaleFactor:2 }); await p.goto('file://'+path.resolve(j.file)+(j.hash||'')); await p.waitForTimeout(j.wait||2500); await run(p,j.pre); await p.waitForTimeout(400); const buf = await p.screenshot({type:'png'}); await p.close(); return 'data:image/png;base64,'+buf.toString('base64'); };
    const fonts = `<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..900&family=Inter:wght@400..700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">`;
    if (j.portrait) { const img = await snap(1440,900); const p = await b.newPage({ viewport:{width:1080,height:1350}, deviceScaleFactor:2 });
      await p.setContent(`<!doctype html><meta charset=utf-8>${fonts}<style>*{margin:0;box-sizing:border-box}body{width:1080px;height:1350px;background:${j.ground};color:${j.ink};font-family:Inter,sans-serif;position:relative;overflow:hidden}
      .top{position:absolute;left:64px;right:64px;top:56px;display:flex;justify-content:space-between;align-items:baseline;font:600 27px Inter}.top span:last-child{font:500 24px 'JetBrains Mono';letter-spacing:.04em}
      h1{position:absolute;left:64px;right:64px;top:150px;height:290px;display:flex;align-items:center;font-family:Archivo;font-weight:800;font-stretch:112%;letter-spacing:-.03em;line-height:.9;color:${j.accent};white-space:nowrap}
      .shot{position:absolute;left:64px;top:476px;width:952px;height:595px;border-radius:16px;overflow:hidden;box-shadow:0 0 0 1.5px color-mix(in srgb,${j.ink} 22%,transparent),0 30px 60px -20px rgba(0,0,0,.35)}.shot img{width:100%;height:100%;display:block}
      .foot{position:absolute;left:64px;right:64px;bottom:96px;display:flex;justify-content:space-between;align-items:flex-end}.foot span{font:500 26px Inter;padding-bottom:70px}.foot b{font-family:Archivo;font-weight:800;font-stretch:112%;font-size:128px;line-height:.8;letter-spacing:-.03em}
      .ck{position:absolute;left:0;right:0;bottom:0;height:18px;background:conic-gradient(${j.accent} 25%,${j.ground} 0 50%,${j.accent} 0 75%,${j.ground} 0) 0 0/36px 36px}</style>
      <div class=top><span>HumanLup</span><span>Design Lab</span></div><h1 id=t>${j.title}</h1><div class=shot><img src="${img}"></div><div class=foot><span>Built by Lupo</span><b>${j.nn}</b></div><div class=ck></div>`);
      await p.evaluate(async () => { await document.fonts.ready; const t = document.getElementById('t'); let s = 330; t.style.fontSize = s+'px'; while ((t.scrollWidth > t.clientWidth || s > 300) && s > 60) { s -= 4; t.style.fontSize = s+'px'; if (t.scrollWidth <= t.clientWidth && s <= 300) break; } });
      await p.waitForTimeout(300); await p.screenshot({ path:j.portrait, type:'jpeg', quality:90 }); await p.close(); }
    if (j.wide) { const img = await snap(1600,788); const p = await b.newPage({ viewport:{width:1600,height:900}, deviceScaleFactor:2 });
      await p.setContent(`<!doctype html><meta charset=utf-8>${fonts}<style>*{margin:0;box-sizing:border-box}body{width:1600px;height:900px;background:#fff;font-family:Inter,sans-serif}img{display:block;width:1600px;height:788px}
      .bar{height:100px;border-top:1.5px solid #111;display:flex;justify-content:space-between;align-items:center;padding:0 48px;color:#111}.bar b{font:600 44px Inter;letter-spacing:-.02em}.bar span{font:500 24px Inter}
      .ck{height:12px;background:conic-gradient(#111 25%,#fff 0 50%,#111 0 75%,#fff 0) 0 0/24px 24px}</style><img src="${img}"><div class=bar><b>${j.title}</b><span>HumanLup Design Lab ${j.nn}</span></div><div class=ck></div>`);
      await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300); await p.screenshot({ path:j.wide, type:'jpeg', quality:88 }); await p.close(); }
    console.log('done', j.nn, j.title);
  }
  await b.close();
})();
