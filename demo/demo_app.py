"""
Fast Finder — local UI demo server.

    python demo/demo_app.py            # http://localhost:8080

Runs the REAL web UI (web/dashboard_routes.py, post_routes.py, actor_routes.py,
stats_routes.py, profile_routes.py, login_routes.py, stream_routes.py) against
in-memory sample data, so every screen can be clicked through without Telegram
or MongoDB. Nothing in this folder is imported by the production bot.
"""
from __future__ import annotations

import html
import os
import sys
import uuid
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT))

import mocks  # noqa: E402  (must run before the web.* imports)

mocks.install()

from aiohttp import web  # noqa: E402

from web.web_assets import CSS  # noqa: E402
from web.stream_routes import routes as stream_routes  # noqa: E402
from web.search_api import search_routes  # noqa: E402
from web.dashboard_routes import dashboard_routes  # noqa: E402
from web.login_routes import login_routes  # noqa: E402
from web.stats_routes import stats_routes  # noqa: E402
from web.profile_routes import profile_routes  # noqa: E402
from web.actor_routes import actor_routes  # noqa: E402
from web.post_routes import post_routes  # noqa: E402

from utils import temp, get_size  # noqa: E402
from database.users_chats_db import db as user_db  # noqa: E402

DEMO_ROUTES = web.RouteTableDef()

# routes we replace with demo-friendly equivalents
SKIP_PATHS = {
    "/api/search", "/api/thumb",
    "/watch/{message_id}", "/download/{message_id}", "/stream/{message_id}",
    "/api/actor/search",
}

ROUTE_TABLES = [
    stream_routes, search_routes, dashboard_routes, login_routes,
    stats_routes, profile_routes, actor_routes, post_routes,
]


# ─────────────────────────────────────────────────────────────
# demo helpers
# ─────────────────────────────────────────────────────────────
def _poster(stem: str) -> str:
    return f"/demo-static/posters/{stem}.jpg"


def _result_json(doc, mode="tg"):
    fid = doc["_id"]
    thumb = _poster(doc["thumb_url"].split(":", 1)[1]) if doc.get("thumb_url") else ""
    return {
        "file_id": fid,
        "name": doc["file_name"],
        "size": get_size(doc["file_size"]),
        "type": doc["file_type"].upper(),
        "source": doc["source_col"].capitalize(),
        "raw_collection": doc["source_col"],
        "poster": thumb,
        "tg_thumb": thumb if mode != "none" else "",
        "watch": f"/watch/{fid}",
        "download": f"/watch/{fid}?download=1",
        "caption": doc.get("caption", ""),
    }


@DEMO_ROUTES.get("/demo-static/{tail:.*}")
async def demo_static(request):
    tail = request.match_info["tail"]
    path = (HERE / "static" / tail).resolve()
    if not str(path).startswith(str((HERE / "static").resolve())) or not path.is_file():
        raise web.HTTPNotFound()
    content_type = "image/jpeg" if path.suffix == ".jpg" else "application/octet-stream"
    return web.Response(body=path.read_bytes(), content_type=content_type,
                        headers={"Cache-Control": "public, max-age=86400"})


@DEMO_ROUTES.get("/api/search")
async def demo_search(request):
    q = request.query.get("q", "").strip()
    col = request.query.get("col", "all")
    mode = request.query.get("mode", "tg")
    try:
        offset = int(request.query.get("offset") or 0)
    except ValueError:
        offset = 0

    if not q:
        return web.json_response({"results": [], "total": 0, "next_offset": "", "is_admin": True})

    terms = [t for t in q.lower().split() if t]
    hits = []
    for doc in mocks.MEDIA:
        hay = f"{doc['file_name']} {doc.get('caption','')}".lower()
        if all(t in hay for t in terms):
            if col != "all" and doc["source_col"] != col:
                continue
            hits.append(doc)

    limit = 12
    page = hits[offset:offset + limit]
    next_offset = str(offset + limit) if offset + limit < len(hits) else ""
    return web.json_response({
        "results": [_result_json(d, mode) for d in page],
        "total": len(hits),
        "next_offset": next_offset,
        "is_admin": True,
    })


@DEMO_ROUTES.get("/api/actor/search")
async def demo_actor_search(request):
    q = request.query.get("q", "").strip().lower()
    col = request.query.get("col", "all")
    mode = request.query.get("mode", "tg")
    try:
        offset = int(request.query.get("offset") or 0)
    except ValueError:
        offset = 0

    actor = await mocks.actor_routes_doc(request.query.get("id"))
    name_terms = (actor or {}).get("name", "").split()[:1]
    hits = []
    for doc in mocks.MEDIA:
        hay = f"{doc['file_name']} {doc.get('caption','')}".lower()
        if any(t.lower() in hay for t in name_terms) or not name_terms:
            if col != "all" and doc["source_col"] != col:
                continue
            hits.append(doc)

    limit = 6
    page = hits[offset:offset + limit]
    next_offset = str(offset + limit) if offset + limit < len(hits) else ""
    return web.json_response({
        "results": [_result_json(d, mode) for d in page],
        "next_offset": next_offset,
    })


async def _actor_doc(actor_id):
    for a in mocks.ACTOR_DOCS:
        if str(a["_id"]) == str(actor_id):
            return a
    return None


mocks.actor_routes_doc = _actor_doc


# ─────────────────────────────────────────────────────────────
# demo watch page
# ─────────────────────────────────────────────────────────────
WATCH_TMPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#08080b">
<title>{title} — Fast Finder</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<style>{css}
.wrap{{max-width:1120px;margin:0 auto;padding:26px clamp(14px,3.4vw,30px) 60px}}
.back{{display:inline-flex;align-items:center;gap:7px;color:var(--muted);font-size:12.5px;font-weight:700;text-decoration:none;margin-bottom:16px}}
.back:hover{{color:var(--text)}}
.stage{{position:relative;border-radius:20px;overflow:hidden;border:1px solid var(--border);background:#000;box-shadow:var(--shadow-2);aspect-ratio:16/9}}
.stage img{{width:100%;height:100%;object-fit:cover;opacity:.62;filter:saturate(1.05)}}
.stage::after{{content:'';position:absolute;inset:0;background:radial-gradient(circle at 50% 60%,rgba(0,0,0,.15),rgba(0,0,0,.78))}}
.play{{position:absolute;inset:0;margin:auto;width:84px;height:84px;border-radius:50%;border:1px solid rgba(255,255,255,.5);background:rgba(229,9,20,.92);color:#fff;display:flex;align-items:center;justify-content:center;cursor:pointer;z-index:3;box-shadow:0 18px 44px rgba(229,9,20,.55);transition:transform .18s}}
.play:hover{{transform:scale(1.06)}}
.play svg{{width:30px;height:30px;margin-left:4px;fill:currentColor}}
.bar{{position:absolute;left:0;right:0;bottom:0;padding:16px 18px;z-index:4;background:linear-gradient(to top,rgba(0,0,0,.9),transparent);display:flex;align-items:center;gap:14px;color:#fff;font-size:12px}}
.track{{flex:1;height:5px;border-radius:99px;background:rgba(255,255,255,.22);overflow:hidden}}
.fill{{height:100%;width:0%;background:var(--grad);border-radius:99px;transition:width .3s linear}}
.tc{{font-variant-numeric:tabular-nums;font-weight:700;letter-spacing:.04em}}
.meta{{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0 10px}}
.chip{{background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:5px 11px;font-size:11px;font-weight:700;color:var(--muted)}}
.chip.primary{{color:#6ee7a0;border-color:rgba(34,197,94,.4);background:rgba(20,83,45,.3)}}
.chip.cloud{{color:#9ecbff;border-color:rgba(96,165,250,.4);background:rgba(20,52,95,.3)}}
.chip.archive{{color:#fdc08a;border-color:rgba(251,146,60,.4);background:rgba(90,38,10,.3)}}
h1.title{{font-size:clamp(20px,3vw,30px);line-height:1.2;font-weight:800}}
.caption{{color:var(--muted);font-size:13.5px;margin-top:10px;line-height:1.65;max-width:80ch}}
.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:22px}}
.note{{margin-top:26px;padding:14px 16px;border-radius:14px;border:1px dashed var(--border);color:var(--muted);font-size:12.5px;display:flex;gap:10px;align-items:flex-start}}
.note b{{color:var(--text)}}
</style></head>
<body class="with-narrow">
<header class="topbar">
  <a class="logo" href="/"><span class="nf-icon">F</span><span class="logo-text">FAST <b>FINDER</b></span></a>
  <div class="topbar-right"><a href="/dashboard" class="pg-btn" style="text-decoration:none;display:inline-flex;align-items:center;height:38px">Dashboard</a></div>
</header>
<div class="wrap">
  <a class="back" href="/dashboard">&larr; Back to search</a>
  <div class="stage">
    <img src="{poster}" alt="">
    <button class="play" id="playBtn" aria-label="Play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></button>
    <div class="bar"><span class="tc" id="tc">00:00</span><div class="track"><div class="fill" id="fill"></div></div><span class="tc">{duration}</span></div>
  </div>
  <div class="meta">
    <span class="chip">{kind}</span><span class="chip">{size}</span>
    <span class="chip {sc}">{collection}</span><span class="chip">1080p · HDR</span><span class="chip">Demo asset</span>
  </div>
  <h1 class="title">{title}</h1>
  <p class="caption">{caption}</p>
  <div class="actions">
    <button class="search-btn" onclick="fakeDownload()">Download file</button>
    <button class="pg-btn" onclick="document.getElementById('playBtn').click()">Resume playback</button>
  </div>
  <div class="note">
    <span style="font-size:16px">💡</span>
    <div><b>This is a UI demo.</b> In production this page streams the actual Telegram file through a ranged video endpoint, with poster caching and resume support. Sample art and metadata are used here.</div>
  </div>
</div>
<script>
(function(){{
  var playing=false, pct=0, btn=document.getElementById('playBtn'),
      fill=document.getElementById('fill'), tc=document.getElementById('tc'), timer=null;
  function fmt(s){{var m=Math.floor(s/60),x=Math.floor(s%60);return String(m).padStart(2,'0')+':'+String(x).padStart(2,'0');}}
  btn.addEventListener('click',function(){{
    playing=!playing;
    btn.innerHTML='<svg viewBox="0 0 24 24">'+(playing?'<path d="M6 5h4v14H6zM14 5h4v14h-4z"/>':'<path d="M8 5v14l11-7z"/>')+'</svg>';
    if(playing){{ timer=setInterval(function(){{ pct=Math.min(100,pct+0.55); fill.style.width=pct+'%'; tc.textContent=fmt(pct*1.28); if(pct>=100){{clearInterval(timer);playing=false;btn.innerHTML='<svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg>';}} }},140); }}
    else {{ clearInterval(timer); }}
  }});
  function fakeDownload(){{
    var t=document.createElement('div'); t.className='toast show'; t.textContent='Demo mode — downloads are served by Telegram in production.';
    document.body.appendChild(t); setTimeout(function(){{t.classList.remove('show');setTimeout(function(){{t.remove()}},350)}},3000);
  }}
}})();
</script></body></html>"""


@DEMO_ROUTES.get("/watch/{file_id}")
async def demo_watch(request):
    fid = request.match_info["file_id"]
    doc = next((d for d in mocks.MEDIA if d["_id"] == fid), None)
    if not doc:
        raise web.HTTPNotFound(text="Unknown demo asset")
    poster = _poster(doc["thumb_url"].split(":", 1)[1])
    body = WATCH_TMPL.format(
        title=html.escape(doc["file_name"]),
        poster=poster,
        caption=html.escape(doc.get("caption", "")),
        size=get_size(doc["file_size"]),
        kind=doc["file_type"].upper(),
        collection=doc["source_col"].capitalize(),
        sc=doc["source_col"],
        duration="02:14:00",
        css=CSS,
    )
    return web.Response(text=body, content_type="text/html")


# ─────────────────────────────────────────────────────────────
# demo identity switcher
# ─────────────────────────────────────────────────────────────
@DEMO_ROUTES.get("/demo/login")
async def demo_login(request):
    role = request.query.get("role", "admin")
    tg_id = mocks.ADMIN_ID if role == "admin" else mocks.MEMBER_ID
    token = str(uuid.uuid4())
    temp.USER_SESSIONS[token] = {"tg_id": tg_id, "expiry": time.time() + 86400 * 7}
    res = web.HTTPFound("/dashboard")
    res.set_cookie("user_session", token, max_age=86400 * 7)
    return res


# ─────────────────────────────────────────────────────────────
# demo hub — every screen in one place
# ─────────────────────────────────────────────────────────────
HUB_TMPL = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Fast Finder — UI demo</title>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<style>{css}
.hub{{max-width:1120px;margin:0 auto;padding:clamp(26px,5vw,54px) clamp(16px,4vw,30px) 70px}}
.hub-head{{max-width:64ch;margin-bottom:30px}}
.hub-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px}}
.hub-card{{display:flex;flex-direction:column;gap:8px;padding:20px;border-radius:18px;background:var(--card);
  border:1px solid var(--border);text-decoration:none;color:var(--text);box-shadow:var(--shadow-1);
  transition:transform .2s,border-color .2s,box-shadow .2s;position:relative;overflow:hidden}}
.hub-card:hover{{transform:translateY(-4px);border-color:rgba(229,9,20,.45);box-shadow:0 22px 44px -20px rgba(0,0,0,.8)}}
.hub-ico{{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;
  background:rgba(229,9,20,.12);border:1px solid rgba(229,9,20,.28);color:var(--accent);margin-bottom:4px}}
.hub-ico svg{{width:19px;height:19px}}
.hub-card h3{{font-size:15px;font-weight:700;font-family:var(--font-display)}}
.hub-card p{{font-size:12.5px;color:var(--muted);line-height:1.55}}
.hub-path{{font-size:10.5px;font-weight:700;letter-spacing:.06em;color:var(--muted);opacity:.75;font-family:ui-monospace,monospace}}
.hub-actions{{display:flex;gap:9px;flex-wrap:wrap;margin:18px 0 30px}}
.note{{margin-top:28px;padding:14px 16px;border-radius:14px;border:1px dashed var(--border);color:var(--muted);font-size:12.5px}}
</style></head>
<body>
<header class="topbar">
  <a class="logo" href="/"><span class="nf-icon">F</span><span class="logo-text">FAST <b>FINDER</b></span></a>
  <div class="topbar-right"><a href="/" style="font-size:12px;font-weight:700;color:var(--muted);text-decoration:none;padding:8px 12px;border:1px solid var(--border);border-radius:10px">Public site</a></div>
</header>
<div class="hub">
  <div class="hub-head">
    <div class="page-eyebrow">UI 2.0 · walkthrough</div>
    <h1 class="page-title" style="font-size:clamp(26px,4vw,38px)">Fast Finder web UI demo</h1>
    <p class="page-sub">Every screen below is rendered by the real route modules with sample data.
      Start with the dashboard — search a title, switch collections, open a player.</p>
  </div>
  <div class="hub-actions">
    <a class="search-btn" href="/demo/login?role=admin" style="text-decoration:none">Open dashboard as admin</a>
    <a class="pg-btn" href="/demo/login?role=user" style="text-decoration:none;display:inline-flex;align-items:center;height:46px">Member view</a>
  </div>
  <div class="hub-grid">{cards}</div>
  <div class="note">Sample posters are AI-generated stand-ins; titles, sizes and counters are fictional.
    In production the same screens are driven by MongoDB + Telegram.</div>
</div>
</body></html>"""

HUB_ITEMS = [
    ("Search dashboard", "Hero, quick chips, live search, poster grid and pagination.", "/dashboard", "search"),
    ("Landing page", "Public entry point with search that deep-links into the bot.", "/", "home"),
    ("Sign in", "Glass auth card with Telegram OTP messaging.", "/login", "profile"),
    ("Posts catalog", "Curated releases with category filters.", "/posts", "posts"),
    ("Directory", "Actors, apps and websites in one grid.", "/actors", "actors"),
    ("Actor profile", "Tabs, gallery and linked media search.", "/actor/a0000000000000000000001", "actors"),
    ("Post detail", "Editorial layout with tags and screenshots.", "/post/b0000000000000000000001", "posts"),
    ("Analytics", "Admin-only storage, audience and telemetry panels.", "/stats", "stats"),
    ("Account settings", "Profile, security and plan status.", "/profile", "profile"),
    ("Player", "Watch screen with simulated playback.", "/watch/demo0003", "play"),
]

_ICON = {
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/>',
    "search": '<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>',
    "posts": '<rect x="3" y="4.5" width="18" height="15" rx="3"/><path d="M7.5 9h9M7.5 12.5h9M7.5 16h5"/>',
    "actors": '<circle cx="12" cy="8.2" r="3.6"/><path d="M4.8 20c.7-3.6 3.6-5.4 7.2-5.4s6.5 1.8 7.2 5.4"/>',
    "stats": '<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>',
    "profile": '<circle cx="12" cy="8" r="3.4"/><path d="M5 20c.8-3.4 3.6-5.1 7-5.1s6.2 1.7 7 5.1"/>',
    "play": '<rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="m10 9.5 5 2.5-5 2.5v-5Z"/>',
}


@DEMO_ROUTES.get("/demo")
async def demo_hub(request):
    cards = ""
    for title, desc, path, icon in HUB_ITEMS:
        cards += (
            f'<a class="hub-card" href="{path}">'
            f'<span class="hub-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round">{_ICON[icon]}</svg></span>'
            f'<h3>{title}</h3><p>{desc}</p><span class="hub-path">{path}</span></a>'
        )
    return web.Response(text=HUB_TMPL.format(css=CSS, cards=cards), content_type="text/html")


# ─────────────────────────────────────────────────────────────
# app assembly
# ─────────────────────────────────────────────────────────────
DEMO_BAR = """
<style>
.demo-bar{position:fixed;right:16px;bottom:16px;z-index:400;display:flex;align-items:center;gap:8px;
  padding:7px 9px 7px 12px;border-radius:14px;background:rgba(12,12,18,.92);
  -webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);border:1px solid rgba(255,255,255,.14);
  box-shadow:0 18px 40px rgba(0,0,0,.55);font-family:'DM Sans',system-ui,sans-serif;font-size:11.5px;color:#f2f2f6}
.demo-bar .dot{width:6px;height:6px;border-radius:50%;background:#2dd4a7;box-shadow:0 0 8px #2dd4a7}
.demo-bar b{font-weight:800;letter-spacing:.08em;text-transform:uppercase;font-size:10px;color:#9c9cae}
.demo-bar a{color:#f2f2f6;text-decoration:none;font-weight:700;padding:5px 9px;border-radius:8px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.10)}
.demo-bar a:hover{background:#e50914;border-color:transparent;color:#fff}
.demo-bar .sep{width:1px;height:16px;background:rgba(255,255,255,.14)}
@media(max-width:820px){.demo-bar{bottom:82px;right:10px;padding:6px 8px}.demo-bar a{padding:4px 7px;font-size:11px}}
</style>
<div class="demo-bar">
  <span class="dot"></span><b>Demo</b><span class="sep"></span>
  <a href="/demo/login?role=admin">Admin view</a>
  <a href="/demo/login?role=user">Member view</a>
  <a href="/demo">All screens</a>
  <a href="/" target="_blank" rel="noopener">Public site</a>
</div>
"""


@web.middleware
async def demo_bar_middleware(request, handler):
    resp = await handler(request)
    ctype = resp.headers.get("Content-Type", "")
    if isinstance(resp, web.Response) and resp.status == 200 and "text/html" in ctype and "demo-bar" not in (resp.text or ""):
        try:
            body = resp.text or ""
            if "</body>" in body:
                resp.text = body.replace("</body>", DEMO_BAR + "</body>", 1)
        except Exception:
            pass
    return resp


def build_app():
    app = web.Application(client_max_size=64 * 1024 * 1024, middlewares=[demo_bar_middleware])
    seen = set()
    for table in ROUTE_TABLES:
        for rd in table:
            path = getattr(rd, "path", None)
            method = getattr(rd, "method", "GET")
            if not path or path in SKIP_PATHS:
                continue
            if (method, path) in seen:
                continue
            seen.add((method, path))
            app.router.add_route(method, path, rd.handler)
    app.add_routes(DEMO_ROUTES)
    return app


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app = build_app()
    print(f"  Fast Finder demo UI  →  http://0.0.0.0:{port}")
    print("  walkthrough: /demo   admin: /demo/login?role=admin   member: /demo/login?role=user")
    web.run_app(app, host="0.0.0.0", port=port, print=None, access_log=None)
