#!/usr/bin/env python3
"""Succede Altrove — renderer grafiche Instagram (HTML/CSS -> PNG 1080x1350, 4:5 — formato accettato dalle API Instagram).
Uso: python3 render.py post.json OUT_DIR
Il testo viene SEMPRE composto qui (mai dentro l'immagine AI) per evitare errori di ortografia/accenti."""
import json, sys, re, html, base64, pathlib, asyncio
from playwright.async_api import async_playwright

W, H = 1080, 1350
BRAND = "succede altrove"

CSS = r"""
:root{--navy:#0C1A3A;--paper:#EEF1F6;--blue:#1F3FD0;--red:#E63B2E;--mute:#6B7690}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1080px;height:1350px;overflow:hidden}
body{font-family:Poppins,'Noto Sans CJK SC','Noto Color Emoji',sans-serif;-webkit-font-smoothing:antialiased}
.s{position:relative;width:1080px;height:1350px;padding:92px 76px 72px;display:flex;flex-direction:column;overflow:hidden}
/* posta aerea: bordo a strisce rosso/blu in alto */
.s:before{content:"";position:absolute;left:0;right:0;top:0;height:22px;background:repeating-linear-gradient(135deg,var(--red) 0 34px,var(--paper) 34px 50px,var(--blue) 50px 84px,var(--paper) 84px 100px);z-index:5}
.dark{background:var(--blue);color:var(--paper)}
.paper{background:var(--paper);color:var(--navy)}
.lime{background:var(--red);color:var(--paper)}
.mono{font-family:'DejaVu Sans Mono',monospace;letter-spacing:.02em}
.hd{display:flex;justify-content:space-between;align-items:center;font-size:24px;position:relative;z-index:3}
.logo{display:flex;align-items:center;gap:14px;font-weight:600;letter-spacing:-.01em;font-size:28px}
.mark{width:34px;height:34px;border:4px solid currentColor;border-radius:50%;position:relative}
.mark:after{content:"";position:absolute;width:12px;height:12px;border-radius:50%;background:var(--red);right:-9px;top:-9px;box-shadow:0 0 0 4px var(--bgc)}
.dark{--bgc:#1F3FD0}.paper{--bgc:#EEF1F6}.lime{--bgc:#E63B2E}
.dark .mark:after{background:var(--paper)}.lime .mark:after{background:var(--navy)}
.chip{border:2px dashed currentColor;padding:8px 16px;font-size:22px;display:flex;gap:10px;align-items:center}
.chip .e{font-family:'Noto Color Emoji';font-size:24px}
.ft{margin-top:auto;display:flex;justify-content:space-between;align-items:flex-end;font-size:21px;opacity:.75;position:relative;z-index:3;gap:40px}
.ft .src{max-width:720px;line-height:1.35}
.kicker{font-size:26px;letter-spacing:.14em;text-transform:uppercase;font-weight:600}
h1{font-weight:700;letter-spacing:-.035em;line-height:1.04}
h2{font-weight:700;letter-spacing:-.03em;line-height:1.04;font-size:92px}
p.body{font-weight:500;font-size:50px;line-height:1.3;letter-spacing:-.01em}
mark{--mk:var(--blue);color:var(--paper);background:linear-gradient(180deg,transparent 20%,var(--mk) 20%,var(--mk) 88%,transparent 88%);padding:0 .08em;box-decoration-break:clone;-webkit-box-decoration-break:clone}
.dark mark,.lime mark,.split .top mark{--mk:var(--paper);color:var(--blue)}
.lime mark{color:var(--red)}
b{font-weight:700}
.glyph{position:absolute;right:-40px;bottom:230px;font-family:'Noto Sans CJK SC';font-weight:900;font-size:520px;line-height:1;color:rgba(238,241,246,.11);z-index:1;letter-spacing:-.05em;white-space:nowrap}
.paper .glyph{color:rgba(31,63,208,.07)}
.bgimg{position:absolute;inset:0;background-size:cover;background-position:center;z-index:0}
.bgimg:after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(12,26,58,.10) 0%,rgba(12,26,58,.25) 38%,rgba(12,26,58,.92) 66%,#0C1A3A 100%)}
.heat{display:flex;gap:8px;align-items:center;font-size:22px}
.heat i{display:block;width:16px;height:30px;background:currentColor;opacity:.28}
.heat i.on{opacity:1;background:var(--red)}
.dark .heat i.on{background:var(--paper)}
.num{font-family:'DejaVu Sans Mono',monospace;font-size:30px;font-weight:700;display:inline-block;padding:6px 14px;border:3px solid var(--red);color:var(--red)}
.swipe{font-weight:600;font-size:28px;display:flex;gap:12px;align-items:center}
/* timbro postale: data + luogo, con linee di annullo */
.pm{position:absolute;right:76px;top:150px;width:250px;height:250px;border-radius:50%;border:5px double currentColor;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;transform:rotate(-9deg);font-family:'DejaVu Sans Mono';font-weight:700;font-size:24px;line-height:1.3;z-index:4;opacity:.9}
.pm small{font-size:18px;font-weight:400;letter-spacing:.1em}
.pm:before{content:"";position:absolute;right:230px;top:78px;width:260px;height:90px;background:repeating-linear-gradient(180deg,currentColor 0 5px,transparent 5px 28px);opacity:.7}
.stamp{position:absolute;right:76px;top:430px;padding:10px 18px;border:4px solid var(--red);color:var(--red);transform:rotate(-6deg);font-family:'DejaVu Sans Mono';font-weight:700;font-size:26px;letter-spacing:.08em;z-index:4;background:var(--paper)}
.quote{font-family:Lora,serif;font-style:italic;font-weight:500;font-size:80px;line-height:1.18;letter-spacing:-.01em}
.qm{font-family:Lora,serif;font-size:220px;line-height:.6;color:var(--red);height:110px}
.who{font-size:26px;margin-top:34px}
.split{display:grid;grid-template-rows:1fr 26px 1fr;flex:1;margin:38px 0 24px;border:3px solid var(--navy);overflow:hidden}
.split>.top,.split>.bot{padding:44px 48px;display:flex;flex-direction:column;gap:22px;justify-content:space-between}
.split .band{background:repeating-linear-gradient(135deg,var(--red) 0 30px,var(--paper) 30px 44px,var(--blue) 44px 74px,var(--paper) 74px 88px)}
.split .top{background:var(--blue);color:var(--paper)}
.split .bot{background:#fff;color:var(--navy)}
.split .bot .lab{color:var(--red)}
.split .lab{font-family:'DejaVu Sans Mono';font-weight:700;font-size:26px;letter-spacing:.08em}
.split .txt{font-weight:600;font-size:64px;line-height:1.12;letter-spacing:-.02em}
"""

def md(t):
    t = html.escape(t or "")
    t = re.sub(r"==(.+?)==", r"<mark>\1</mark>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return t.replace("\n", "<br>")

def header(post, theme):
    r = post.get("region", {})
    chip = f'<div class="chip mono"><span class="e">{r.get("flag","")}</span>{html.escape(r.get("label",""))}{" · "+html.escape(r["platform"]) if r.get("platform") else ""}</div>' if r else ""
    return f'<div class="hd"><div class="logo"><div class="mark"></div>{BRAND}</div>{chip}</div>'

def footer(post, i, n, src=None, right=None):
    src = src if src is not None else post.get("source_short", "")
    right = right or f"{i:02d}/{n:02d}"
    return f'<div class="ft mono"><div class="src">{html.escape(src)}</div><div>{right}</div></div>'

def heat(level):
    level = max(1, min(5, int(level or 3)))
    bars = "".join(f'<i class="{"on" if k < level else ""}"></i>' for k in range(5))
    return f'<div class="heat mono">{bars}<span style="margin-left:10px">CALORE {level}/5</span></div>'

def img_uri(p):
    p = pathlib.Path(p)
    if not p.exists(): return None
    mime = "image/png" if p.suffix.lower()==".png" else "image/jpeg" if p.suffix.lower() in (".jpg",".jpeg") else "image/webp"
    return f"data:{mime};base64,{base64.b64encode(p.read_bytes()).decode()}"

def slide_html(post, s, i, n, base):
    t = s["type"]
    if t == "cover":
        uri = img_uri(base / s["image"]) if s.get("image") else None
        bg = f'<div class="bgimg" style="background-image:url({uri})"></div>' if uri else ""
        glyph = f'<div class="glyph">{html.escape(s["glyph"])}</div>' if s.get("glyph") and not uri else ""
        size = s.get("size", 118)
        stamp = f'<div class="stamp">{md(s["stamp"])}</div>' if s.get("stamp") else ""
        if s.get("postmark"):
            pm = s["postmark"]; stamp += f'<div class="pm"><small>{html.escape(pm.get("top","POSTA DA"))}</small>{html.escape(pm.get("place",""))}<small>{html.escape(pm.get("date",""))}</small></div>' 
        inner = f'''{bg}{glyph}{stamp}{header(post,"dark")}
        <div style="margin-top:auto;position:relative;z-index:3">
          <div class="kicker" style="margin-bottom:28px;opacity:.85">{md(s.get("kicker",""))}</div>
          <h1 style="font-size:{size}px">{md(s["headline"])}</h1>
          {f'<p class="body" style="margin-top:34px;font-size:40px;opacity:.9">{md(s["sub"])}</p>' if s.get("sub") else ""}
          <div style="display:flex;justify-content:space-between;align-items:center;margin-top:56px">{heat(s.get("heat",4))}<div class="swipe">scorri <span style="font-size:36px">→</span></div></div>
        </div>'''
        return "dark", inner
    if t == "text":
        glyph = f'<div class="glyph" style="bottom:-70px;font-size:420px">{html.escape(s["glyph"])}</div>' if s.get("glyph") else ""
        inner = f'''{glyph}{header(post,"paper")}
        <div style="margin-top:auto;margin-bottom:auto;position:relative;z-index:3">
          {f'<span class="num">{html.escape(s["num"])}</span>' if s.get("num") else ""}
          <h2 style="margin-top:34px">{md(s["title"])}</h2>
          <p class="body" style="margin-top:40px">{md(s.get("body",""))}</p>
        </div>{footer(post,i,n,s.get("source"))}'''
        return "paper", inner
    if t == "quote":
        inner = f'''{header(post,"paper")}
        <div style="margin-top:auto;margin-bottom:auto;position:relative;z-index:3">
          <div class="qm">“</div>
          <div class="quote">{md(s["quote"])}</div>
          <div class="who mono">— {html.escape(s.get("who",""))}</div>
          {f'<p class="body" style="margin-top:56px;font-size:44px">{md(s["note"])}</p>' if s.get("note") else ""}
        </div>{footer(post,i,n,s.get("source"))}'''
        return "paper", inner
    if t == "split":
        inner = f'''{header(post,"paper")}
        {f'<h2 style="margin-top:44px;font-size:64px">{md(s["title"])}</h2>' if s.get("title") else ""}
        <div class="split">
          <div class="top"><div class="lab">{html.escape(s.get("top_label","NEL MONDO"))}</div><div class="txt">{md(s["top"])}</div></div><div class="band"></div>
          <div class="bot"><div class="lab">{html.escape(s.get("bottom_label","IN ITALIA"))}</div><div class="txt">{md(s["bottom"])}</div></div>
        </div>{footer(post,i,n,s.get("source"), right="@succede.altrove")}'''
        return "paper", inner
    if t == "cta":
        inner = f'''{header(post,"lime")}
        <div style="margin-top:auto;margin-bottom:auto">
          <h1 style="font-size:{s.get("size",104)}px">{md(s["headline"])}</h1>
          {f'<p class="body" style="margin-top:40px">{md(s["sub"])}</p>' if s.get("sub") else ""}
        </div>
        <div class="ft mono" style="opacity:1"><div class="src" style="font-size:24px">Segui @succede.altrove<br>il mondo è già virale. tu lo scopri qui.</div><div>{i:02d}/{n:02d}</div></div>'''
        return "lime", inner
    raise ValueError(t)

async def main(spec_path, out_dir):
    spec_path = pathlib.Path(spec_path); base = spec_path.parent
    post = json.loads(spec_path.read_text())
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    n = len(post["slides"])
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        files = []
        for i, s in enumerate(post["slides"], 1):
            theme, inner = slide_html(post, s, i, n, base)
            doc = f'<!doctype html><html lang="it"><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="s {theme}">{inner}</div></body></html>'
            await pg.set_content(doc, wait_until="load")
            await pg.evaluate("document.fonts.ready")
            # overflow guard: fail loudly if text spills
            over = await pg.evaluate("(()=>{const s=document.querySelector('.s');return [...s.querySelectorAll('h1,h2,p,.quote,.txt')].some(e=>e.getBoundingClientRect().bottom>1350-60)})()")
            f = out / f'{post["post_id"]}_{i:02d}.png'
            await pg.screenshot(path=str(f), clip={"x":0,"y":0,"width":W,"height":H})
            files.append(str(f)); print(("OVERFLOW! " if over else "ok ") + str(f))
        await b.close()
    return files

if __name__ == "__main__":
    asyncio.run(main(sys.argv[1], sys.argv[2]))
