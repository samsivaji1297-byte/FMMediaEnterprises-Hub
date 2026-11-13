import json
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE_SKELETON = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@900&family=Playfair+Display:ital,wght@1,700&display=swap" rel="stylesheet">
<style>
:root{--bg:#000;--fg:#fff;color-scheme:dark;box-sizing:border-box}
*{box-sizing:border-box;margin:0}
html,body{height:100%;background:var(--bg);overflow:hidden}
body{display:flex;align-items:center;justify-content:center;font-family:Inter,"Helvetica Neue",Arial,sans-serif;font-weight:900;color:var(--fg)}
#frame{width:1080px;height:1920px;position:relative;flex:none;overflow:hidden;background:#000}
#cam{position:absolute;inset:0;transform-origin:50% 45%}
.fx{position:absolute;inset:0;pointer-events:none;z-index:9}
#vig{background:radial-gradient(ellipse at center,transparent 50%,rgba(0,0,0,.85))}
#grain{opacity:.16;mix-blend-mode:screen;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='220' height='220' filter='url(%23n)'/></svg>");animation:g .5s steps(3) infinite}
@keyframes g{0%{background-position:0 0}33%{background-position:-60px 40px}66%{background-position:50px -70px}100%{background-position:0 0}}
#flash{background:#fff;opacity:0;z-index:10;transition:opacity .5s}
#flash.on{opacity:.9;transition:opacity .04s}
.abs{position:absolute;left:0;width:1080px;text-align:center}
#wall{inset:0;left:0;display:flex;gap:20px;padding:0 10px;opacity:0;transition:opacity .8s;-webkit-mask-image:linear-gradient(transparent,#000 25%,#000 75%,transparent);mask-image:linear-gradient(transparent,#000 25%,#000 75%,transparent)}
.s2 #wall,.s3 #wall{opacity:.2}
.s4 #wall{opacity:.1}
#wall div{flex:1;font-size:46px;line-height:1.12;letter-spacing:-.035em;text-align:left;animation:up 30s linear infinite}
#wall div:nth-child(2){animation-direction:reverse;animation-duration:38s}
#wall div:nth-child(3){animation-duration:34s}
#wall p{margin:0 0 34px}
@keyframes up{to{transform:translateY(-50%)}}
#hook{top:290px;font-size:150px;line-height:1.02;letter-spacing:-.05em;padding:0 40px;z-index:3;transition:top .8s cubic-bezier(.7,0,.2,1),font-size .8s cubic-bezier(.7,0,.2,1)}
.inv{background:#fff;color:#000;padding:0 .12em;display:inline-block;margin:.04em 0}
#cards{top:1170px;height:340px;perspective:1400px;z-index:2}
.c{position:absolute;left:410px;top:0;width:260px;height:330px;border:2px solid #fff;background:#060606;padding:26px;text-align:left;transform-origin:50% 100%;transition:transform .9s cubic-bezier(.6,0,.2,1),opacity .6s;animation:fl 3s ease-in-out infinite}
.c b{display:block;height:20px;background:#fff;width:88%;margin-bottom:14px}
.c u{display:block;height:10px;background:rgba(255,255,255,.35);margin-bottom:12px;width:100%}
.c u+u{width:70%}.c u+u+u{width:84%}
.c s{position:absolute;left:26px;bottom:26px;width:70px;height:22px;border:2px solid #fff;border-radius:99px}
.c:nth-child(1){transform:translateX(-210px) rotate(-18deg) rotateY(18deg);animation-delay:-.6s}
.c:nth-child(2){transform:translateX(-105px) rotate(-9deg) rotateY(9deg);animation-delay:-1.2s}
.c:nth-child(3){transform:rotate(0)}
.c:nth-child(4){transform:translateX(105px) rotate(9deg) rotateY(-9deg);animation-delay:-1.8s}
.c:nth-child(5){background:#fff;transform:translateX(210px) rotate(18deg) rotateY(-18deg);animation-delay:-2.4s}
.c:nth-child(5) b{background:#000}.c:nth-child(5) u{background:rgba(0,0,0,.35)}.c:nth-child(5) s{border-color:#000}
@keyframes fl{50%{margin-top:-18px}}
.s2 .c{opacity:0}
.s2 .c:nth-child(1){transform:translate(-700px,-900px) rotate(-90deg)}
.s2 .c:nth-child(2){transform:translate(-300px,-1100px) rotate(-40deg)}
.s2 .c:nth-child(3){transform:translate(0,-1200px) rotate(20deg)}
.s2 .c:nth-child(4){transform:translate(300px,-1100px) rotate(40deg)}
.s2 .c:nth-child(5){transform:translate(700px,-900px) rotate(90deg)}
#num{top:430px;z-index:2;opacity:0;transition:opacity .3s}
#num b{display:inline-block;font-size:520px;line-height:.95;letter-spacing:-.07em;padding:0 .06em;font-variant-numeric:tabular-nums}
#num.done b{background:#fff;color:#000}
#lbl{top:1010px;font-size:64px;letter-spacing:-.035em;z-index:2;opacity:0;transition:opacity .3s}
.s2 #num,.s2 #lbl{opacity:1}
.s2 #hook{top:215px;font-size:60px}
#copy{top:1230px;font-size:112px;letter-spacing:-.05em;z-index:3}
#copy span{display:inline-block;opacity:0;transform:translateY(40px) scale(1.15);transition:opacity .2s,transform .3s}
.s3 #copy span{opacity:1;transform:none}
.s3 #copy span:nth-child(2){transition-delay:.35s}.s3 #copy span:nth-child(3){transition-delay:.7s}
#simple{top:600px;opacity:0;z-index:3;transition:opacity .3s}
#simple span{font-size:132px;letter-spacing:-.05em;background:#fff;color:#000;padding:.02em .22em;display:inline-block;line-height:1.1}
#why{top:880px;font-size:62px;line-height:1.2;letter-spacing:-.03em;color:rgba(255,255,255,.65);opacity:0;z-index:3;transition:opacity .4s}
#why em{font-family:"Playfair Display",Georgia,serif;font-style:italic;font-weight:700;color:#fff;letter-spacing:-.01em}
#cta{top:1330px;opacity:0;z-index:3;transition:opacity .3s}
#cta span{display:inline-block;border:3px solid #fff;border-radius:999px;padding:26px 66px;font-size:56px;animation:pl 1.2s ease-in-out infinite}
@keyframes pl{50%{box-shadow:0 0 0 14px rgba(255,255,255,.14)}}
.s4 #hook,.s4 #num,.s4 #lbl,.s4 #copy{opacity:0;transition:opacity .3s}
.s4 #simple{opacity:1;transition-delay:.3s}.s4 #why{opacity:1;transition-delay:.8s}.s4 #cta{opacity:1;transition-delay:1.4s}
</style>
</head>
<body>
<div id="frame">
  <div id="cam">
    <div id="wall" class="abs">
      <div>{wall_col_1}</div>
      <div>{wall_col_2}</div>
      <div>{wall_col_3}</div>
    </div>
    <div id="hook" class="abs">{hook_html}</div>
    <div id="cards" class="abs"><div class="c"><b></b><u></u><u></u><u></u><s></s></div><div class="c"><b></b><u></u><u></u><u></u><s></s></div><div class="c"><b></b><u></u><u></u><u></u><s></s></div><div class="c"><b></b><u></u><u></u><u></u><s></s></div><div class="c"><b></b><u></u><u></u><u></u><s></s></div></div>
    <div id="num" class="abs"><b id="n">00</b></div>
    <div id="lbl" class="abs">{counter_label}</div>
    <div id="copy" class="abs"><span>{beat_1}</span> <span>{beat_2}</span> <span>{beat_3}</span></div>
    <div id="simple" class="abs">{punchline_html}</div>
    <div id="why" class="abs">{subtext_plain}<br><em>{subtext_italic}</em></div>
    <div id="cta" class="abs"><span>{cta_text}</span></div>
  </div>
  <div id="vig" class="fx"></div><div id="grain" class="fx"></div><div id="flash" class="fx"></div>
</div>
<script>
(function(){{
  var frame=document.getElementById('frame'),cam=document.getElementById('cam'),num=document.getElementById('num'),n=document.getElementById('n'),fl=document.getElementById('flash'),timers=[],iv;
  var wall=document.getElementById('wall');wall.querySelectorAll('div').forEach(function(d){{d.innerHTML+=d.innerHTML;}});
  var TARGET={counter_target};
  var STEP_MS=Math.max(16, Math.floor(2000/Math.max(1,TARGET)));
  function fit(){{var s=Math.min(window.innerWidth/1080,window.innerHeight/1920);frame.style.transform='scale('+s+')';}}
  window.addEventListener('resize',fit);fit();
  function at(ms,fn){{timers.push(setTimeout(fn,ms));}}
  function flash(){{fl.classList.add('on');setTimeout(function(){{fl.classList.remove('on');}},60);}}
  function run(){{
    timers.forEach(clearTimeout);clearInterval(iv);timers=[];
    frame.className='';num.classList.remove('done');n.textContent='00';
    cam.style.transition='none';cam.style.transform='scale(1)';void cam.offsetWidth;
    cam.style.transition='transform 13.4s linear';cam.style.transform='scale(1.08)';
    at(2600,function(){{flash();frame.classList.add('s2');}});
    at(3300,function(){{var v=0;iv=setInterval(function(){{v++;n.textContent=(v<10?'0':'')+v;if(v>=TARGET){{clearInterval(iv);num.classList.add('done');flash();}}}},STEP_MS);}});
    at(5700,function(){{frame.classList.add('s3');}});
    at(8200,function(){{flash();frame.classList.add('s4');}});
  }}
  run();
}})();
</script>
</body>
</html>"""

def compile_reel(topic_brief: str, output_path: str):
    system_prompt = """You are an elite brutalist copywriter and motion-graphics script generator.
Your tone is cold, sovereign, high-leverage, and razor-sharp (think Peter Thiel meets high-end digital publishing). Avoid fluff, generic advice, or marketing cliches entirely.

Return ONLY a valid JSON object matching this schema, strictly adhering to character limits to prevent layout breaking:
{
  "hook_before": "1-2 words before highlight (max 15 chars)",
  "hook_highlight": "2-3 heavy impact words to invert in white box (max 20 chars)",
  "hook_after": "2-4 words after highlight (max 25 chars)",
  "counter_target": integer between 3 and 99,
  "counter_label": "2-3 words with periods (e.g., 'posts. written.')",
  "beat_1": "Single word + period (e.g., 'Copy.')",
  "beat_2": "Single word + period (e.g., 'Paste.')",
  "beat_3": "Single word + period (e.g., 'Post.')",
  "punchline_text": "2-4 words for the white background box (e.g., 'It’s that simple.')",
  "subtext_plain": "3-5 words (e.g., 'Claude wrote them.')",
  "subtext_italic": "2-4 words italicized (e.g., 'Prompts included.')",
  "cta_text": "Call to action text (e.g., 'Comment FM')",
  "wall_lines": [
    "18 distinct, highly tactical, short one-liners (4-8 words each) forming the continuous background scroll."
  ]
}"""

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate Reel JSON for this premise:\n{topic_brief}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.5
    )

    data = json.loads(res.choices[0].message.content)
    
    # Format background wall
    lines = data["wall_lines"]
    col1 = "".join(f"<p>{l}</p>" for l in lines[0:6])
    col2 = "".join(f"<p>{l}</p>" for l in lines[6:12])
    col3 = "".join(f"<p>{l}</p>" for l in lines[12:18])

    hook_html = f'{data["hook_before"]} <span class="inv">{data["hook_highlight"]}</span><br>{data["hook_after"]}'
    punchline_html = f'<span>{data["punchline_text"]}</span>'

    html = HTML_TEMPLATE_SKELETON.format(
        wall_col_1=col1,
        wall_col_2=col2,
        wall_col_3=col3,
        hook_html=hook_html,
        counter_target=int(data["counter_target"]),
        counter_label=data["counter_label"],
        beat_1=data["beat_1"],
        beat_2=data["beat_2"],
        beat_3=data["beat_3"],
        punchline_html=punchline_html,
        subtext_plain=data["subtext_plain"],
        subtext_italic=data["subtext_italic"],
        cta_text=data["cta_text"]
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Compiled high-fidelity reel HTML to {output_path}")
