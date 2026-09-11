#!/usr/bin/env python3
"""Gira dentro GitHub Actions. Per ogni inbox/AAAA-MM-GG/queue.json:
rende le slide (render.py, 4:5) in posts/AAAA-MM-GG/<slug>/NN.jpg e scrive queue/AAAA-MM-GG.json con gli URL pubblici.
Rigenera anche storico.md da published/*.json."""
import json, os, pathlib, shutil, subprocess, sys
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = os.environ.get("GITHUB_REPOSITORY", "Succedealtrove/succede-altrove-media")
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
CDN = f"https://cdn.jsdelivr.net/gh/{REPO}@main/"


def render(spec, dest):
    tmp = dest / "_png"
    shutil.rmtree(tmp, ignore_errors=True)
    out = subprocess.run([sys.executable, str(ROOT / "engine/render.py"), str(spec), str(tmp)],
                         capture_output=True, text=True, check=True).stdout
    over = [l for l in out.splitlines() if l.startswith("OVERFLOW")]
    files = []
    for i, p in enumerate(sorted(tmp.glob("*.png")), 1):
        f = dest / f"{i:02d}.jpg"
        Image.open(p).convert("RGB").save(f, "JPEG", quality=92, optimize=True, progressive=True)
        files.append(f)
    shutil.rmtree(tmp)
    return files, over


def build_day(qin):
    date = qin.parent.name
    qout = ROOT / "queue" / f"{date}.json"
    src = json.loads(qin.read_text())
    if qout.exists() and json.loads(qout.read_text()).get("version") == src.get("version"):
        return
    for it in src["items"]:
        if it.get("status") != "ready":
            continue
        dest = ROOT / "posts" / date / it["slug"]
        shutil.rmtree(dest, ignore_errors=True)
        dest.mkdir(parents=True)
        files, over = render(qin.parent / f"{it['slug']}.json", dest)
        if over:
            it["status"], it["slot"] = "skipped", None
            it.setdefault("qa_errors", []).append(f"testo che sborda in {len(over)} slide (render GitHub)")
            shutil.rmtree(dest)
            continue
        rel = [f.relative_to(ROOT).as_posix() for f in files]
        it["image_urls"] = [RAW + r for r in rel]
        it["fallback_urls"] = [CDN + r for r in rel]
        it["action"] = "create_image_post" if len(rel) == 1 else "create_carousel_post"
    qout.parent.mkdir(exist_ok=True)
    qout.write_text(json.dumps(src, ensure_ascii=False, indent=2))
    print("ok", date, [(i["slot"], i["slug"], i["status"]) for i in src["items"]])


def storico():
    rows = []
    for f in sorted((ROOT / "published").glob("*.json")):
        p = json.loads(f.read_text())
        rows.append(f"- {p.get('date')} · {p.get('slot')} · {p.get('slug')} · {p.get('pillar','')} · "
                    f"{p.get('hook','')} · {p.get('status')} · {p.get('media_id') or p.get('error','')}")
    (ROOT / "storico.md").write_text("# Storico pubblicazioni @succede.altrove\n\n"
                                     "data · ora · slug · pilastro · hook · esito · media_id/errore\n\n" + "\n".join(rows) + "\n")


if __name__ == "__main__":
    for q in sorted((ROOT / "inbox").glob("*/queue.json")):
        build_day(q)
    storico()
