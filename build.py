#!/usr/bin/env python3
"""Bygger index.html fra media/-mappa. Kjør på nytt etter at nye filer er lagt inn."""
import base64, json, subprocess, pathlib

ROOT = pathlib.Path(__file__).parent
MEDIA = ROOT / "media"
TITLE = "Bilder & video"


def probe_duration(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(p)], capture_output=True, text=True).stdout
    return round(float(out.strip() or 0), 1)


def img_size(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)],
                         capture_output=True, text=True).stdout.split()
    return int(out[out.index("pixelWidth:") + 1]), int(out[out.index("pixelHeight:") + 1])


items = []
for p in sorted(list((MEDIA / "foto").glob("*.jpg")) + list((MEDIA / "video").glob("*.mp4")),
                key=lambda x: x.stem):
    is_video = p.suffix == ".mp4"
    it = {
        "n": p.name,
        "t": "v" if is_video else "i",
        "th": f"media/thumbs/{p.stem}.jpg",
        "f": f"media/{'video' if is_video else 'foto'}/{p.name}",
        "s": p.stat().st_size,
    }
    lqip = ROOT / ".lqip" / f"{p.stem}.jpg"
    if lqip.exists():
        it["b"] = "data:image/jpeg;base64," + base64.b64encode(lqip.read_bytes()).decode()
    if is_video:
        it["d"] = probe_duration(p)
    else:
        it["w"] = f"media/web/{p.name}"
        it["wh"] = img_size(MEDIA / "web" / p.name)
    items.append(it)

html = (ROOT / "template.html").read_text()
html = html.replace("__TITLE__", TITLE).replace("__ITEMS__", json.dumps(items, separators=(",", ":")))
(ROOT / "index.html").write_text(html)
n_v = sum(i["t"] == "v" for i in items)
print(f"index.html: {len(items) - n_v} bilder, {n_v} videoer")
