import time
from aiohttp import web
from info import ADMINS, MAX_WEB_RESULTS
from utils import temp
from database.users_chats_db import db as user_db

# ----------------- ULTRA-PREMIUM GLASS DIAGNOSTICS ASSETS -----------------
CSS = """
/* ═══════════════════════════════════════════════════════════════════
   FAST FINDER — UI 2.0 DESIGN SYSTEM
   One source of truth for every page (dashboard, posts, actors,
   stats, profile, login). Page modules extend these tokens/vars only.
   ═══════════════════════════════════════════════════════════════════ */

*,*::before,*::after{box-sizing:border-box}
*{margin:0;padding:0}

:root{
  /* surfaces */
  --bg:#08080b;
  --bg2:#0d0d12;
  --bg3:#14141c;
  --bg4:#1e1e2a;
  --card:#101018;
  --glass:rgba(13,13,18,.72);
  /* type */
  --text:#f6f6f9;
  --muted:#9c9cae;
  --border:#232332;
  --border-2:#303044;
  /* brand */
  --accent:#e50914;
  --accent-hover:#c00812;
  --accent-2:#ff5a4d;
  --accent-soft:rgba(229,9,20,.12);
  --grad:linear-gradient(135deg,#e50914 0%,#ff5a4d 100%);
  /* accents */
  --sky:#4c9aff;
  --mint:#2dd4a7;
  --amber:#f5a524;
  --violet:#a855f7;
  /* geometry */
  --radius:16px;
  --radius-sm:10px;
  --radius-lg:24px;
  --radius-pill:999px;
  --sidebar-w:272px;
  --topbar-h:66px;
  /* elevation */
  --shadow-1:0 1px 2px rgba(0,0,0,.35),0 10px 26px rgba(0,0,0,.32);
  --shadow-2:0 26px 70px rgba(0,0,0,.6);
  --ring:0 0 0 3px rgba(229,9,20,.20);
  /* fonts */
  --font-display:'Sora','DM Sans',system-ui,-apple-system,sans-serif;
  --font-body:'DM Sans',system-ui,-apple-system,'Segoe UI',sans-serif;
  /* live progress vars (stats page) */
  --primary-p:0%;
  --cloud-p:0%;
  --archive-p:0%;
}

html.light,.light{
  --bg:#f5f6f9;
  --bg2:#ffffff;
  --bg3:#eef0f5;
  --bg4:#e1e5ee;
  --card:#ffffff;
  --glass:rgba(255,255,255,.80);
  --text:#0e0e15;
  --muted:#5f6274;
  --border:#e4e7ef;
  --border-2:#d2d7e3;
  --accent-soft:rgba(229,9,20,.08);
  --shadow-1:0 1px 2px rgba(16,18,30,.06),0 10px 26px rgba(16,18,30,.08);
  --shadow-2:0 26px 70px rgba(16,18,30,.16);
  --ring:0 0 0 3px rgba(229,9,20,.14);
}

html{scroll-behavior:smooth;-webkit-text-size-adjust:100%}
body{
  font-family:var(--font-body);
  background:var(--bg);
  color:var(--text);
  min-height:100vh;
  overflow-x:hidden;
  line-height:1.5;
  -webkit-font-smoothing:antialiased;
  -moz-osx-font-smoothing:grayscale;
  transition:background .25s ease,color .25s ease;
}
body::before{
  content:'';
  position:fixed;
  inset:0;
  z-index:-1;
  pointer-events:none;
  background:
    radial-gradient(760px 420px at 8% -8%,rgba(229,9,20,.16),transparent 62%),
    radial-gradient(680px 420px at 96% -4%,rgba(168,85,247,.14),transparent 60%),
    radial-gradient(900px 520px at 50% 110%,rgba(76,154,255,.10),transparent 65%);
}
.light body::before,html.light body::before{
  background:
    radial-gradient(760px 420px at 8% -8%,rgba(229,9,20,.10),transparent 62%),
    radial-gradient(680px 420px at 96% -4%,rgba(168,85,247,.09),transparent 60%);
}
h1,h2,h3,h4,.hero-title,.hero-num,.big-stat-val{font-family:var(--font-display);letter-spacing:-.02em}
a{color:inherit}
img{display:block;max-width:100%}
button{font-family:inherit}
::selection{background:rgba(229,9,20,.32);color:#fff}
:focus-visible{outline:none;box-shadow:var(--ring);border-radius:8px}

/* ── scrollbar ─────────────────────────────────────────────── */
*{scrollbar-width:thin;scrollbar-color:var(--bg4) transparent}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:transparent}
::-webkit-scrollbar-thumb{background:var(--bg4);border-radius:99px;border:3px solid transparent;background-clip:content-box}
::-webkit-scrollbar-thumb:hover{background:var(--border-2);background-clip:content-box}

/* ── top bar ───────────────────────────────────────────────── */
.topbar{
  background:var(--glass);
  -webkit-backdrop-filter:blur(20px) saturate(150%);
  backdrop-filter:blur(20px) saturate(150%);
  height:var(--topbar-h);
  padding:0 clamp(14px,3.4vw,34px);
  display:flex;
  align-items:center;
  gap:12px;
  position:sticky;
  top:0;
  z-index:100;
  border-bottom:1px solid var(--border);
  box-shadow:0 12px 30px -18px rgba(0,0,0,.7);
}
.ham-btn{
  background:transparent;
  border:1px solid transparent;
  border-radius:12px;
  cursor:pointer;
  color:var(--text);
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
  gap:4px;
  width:42px;
  height:42px;
  padding:0;
  flex-shrink:0;
  transition:background .18s,border-color .18s,transform .18s;
}
.ham-btn:hover{background:var(--bg3);border-color:var(--border)}
.ham-btn:active{transform:scale(.94)}
.ham-line{width:18px;height:2px;border-radius:2px;background:currentColor;transition:transform .22s,opacity .22s}
.ham-btn.open .ham-line:nth-child(1){transform:translateY(6px) rotate(45deg)}
.ham-btn.open .ham-line:nth-child(2){opacity:0}
.ham-btn.open .ham-line:nth-child(3){transform:translateY(-6px) rotate(-45deg)}

.logo{
  font-family:var(--font-display);
  font-size:16px;
  font-weight:800;
  letter-spacing:.14em;
  color:var(--text);
  display:inline-flex;
  align-items:center;
  gap:11px;
  text-decoration:none;
  flex:1;
  min-width:0;
}
.logo-text{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.logo-text b{color:var(--accent);font-weight:800}
.nf-icon{
  width:32px;
  height:32px;
  border-radius:10px;
  background:var(--grad);
  color:#fff;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  font-size:15px;
  font-weight:900;
  line-height:1;
  letter-spacing:0;
  box-shadow:0 6px 18px rgba(229,9,20,.42),inset 0 1px 0 rgba(255,255,255,.28);
  flex-shrink:0;
}
.topbar-right{display:flex;align-items:center;gap:8px;flex-shrink:0}

.theme-btn{
  width:38px;
  height:38px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:7px;
  background:var(--bg3);
  border:1px solid var(--border);
  border-radius:12px;
  color:var(--muted);
  font-size:12px;
  font-weight:700;
  cursor:pointer;
  transition:background .18s,color .18s,border-color .18s,transform .18s;
}
.theme-btn:hover{background:var(--bg4);color:var(--text);border-color:var(--border-2)}
.theme-btn:active{transform:scale(.94)}
.theme-btn svg{width:17px;height:17px}
.theme-btn .t-moon{display:none}
html.light .theme-btn .t-moon,.light .theme-btn .t-moon{display:block}
html.light .theme-btn .t-sun,.light .theme-btn .t-sun{display:none}

.avatar{
  width:36px;
  height:36px;
  border-radius:50%;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  font-size:13px;
  font-weight:800;
  text-decoration:none;
  color:#fff;
  background:linear-gradient(135deg,#3d3d55,#1c1c28);
  border:1px solid var(--border-2);
  box-shadow:var(--shadow-1);
  transition:transform .18s,border-color .18s;
}
.avatar:hover{transform:translateY(-1px);border-color:var(--accent)}
.avatar.admin{background:var(--grad);border-color:transparent;box-shadow:0 6px 18px rgba(229,9,20,.4)}

/* ── sidebar ───────────────────────────────────────────────── */
.sidebar-overlay{
  position:fixed;
  inset:0;
  background:rgba(4,4,8,.66);
  -webkit-backdrop-filter:blur(3px);
  backdrop-filter:blur(3px);
  z-index:150;
  opacity:0;
  pointer-events:none;
  transition:opacity .25s ease;
}
.sidebar-overlay.open{opacity:1;pointer-events:all}
.sidebar{
  position:fixed;
  top:0;
  left:0;
  height:100%;
  width:var(--sidebar-w);
  max-width:86vw;
  background:linear-gradient(180deg,var(--bg2),var(--bg));
  border-right:1px solid var(--border);
  z-index:160;
  display:flex;
  flex-direction:column;
  transform:translateX(-102%);
  transition:transform .3s cubic-bezier(.32,.72,0,1);
  box-shadow:40px 0 90px -40px rgba(0,0,0,.9);
}
.sidebar.open{transform:translateX(0)}
.sb-header{
  padding:18px 16px 18px 20px;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  border-bottom:1px solid var(--border);
}
.sb-logo{
  display:flex;
  align-items:center;
  gap:11px;
  font-family:var(--font-display);
  font-size:13px;
  font-weight:800;
  letter-spacing:.12em;
  color:var(--text);
}
.sb-brand-sub{font-family:var(--font-body);font-size:10.5px;font-weight:500;letter-spacing:.02em;color:var(--muted);margin-top:2px}
.sb-close{
  background:var(--bg3);
  border:1px solid var(--border);
  color:var(--muted);
  width:32px;
  height:32px;
  border-radius:10px;
  font-size:15px;
  line-height:1;
  cursor:pointer;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  transition:background .18s,color .18s;
}
.sb-close:hover{background:var(--bg4);color:var(--text)}
.sb-nav{flex:1;overflow-y:auto;padding:16px 12px;display:flex;flex-direction:column;gap:3px}
.sb-section{
  font-size:10px;
  font-weight:800;
  letter-spacing:.16em;
  text-transform:uppercase;
  color:var(--muted);
  opacity:.75;
  padding:14px 12px 7px;
}
.sb-section:first-child{padding-top:2px}
.sb-link{
  display:flex;
  align-items:center;
  gap:11px;
  padding:11px 13px;
  border-radius:12px;
  text-decoration:none;
  color:var(--muted);
  font-size:14px;
  font-weight:600;
  border:1px solid transparent;
  transition:background .16s,color .16s,border-color .16s,transform .16s;
}
.sb-link svg{width:18px;height:18px;flex-shrink:0;opacity:.85}
.sb-link:hover{background:var(--bg3);color:var(--text)}
.sb-link:active{transform:scale(.985)}
.sb-link.active{
  color:var(--text);
  background:linear-gradient(90deg,rgba(229,9,20,.18),rgba(229,9,20,.03));
  border-color:rgba(229,9,20,.30);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.04);
}
.sb-link.active svg{color:var(--accent);opacity:1}
.sb-link.active::after{
  content:'';
  margin-left:auto;
  width:5px;
  height:5px;
  border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 10px var(--accent);
}
.sb-footer{padding:12px;border-top:1px solid var(--border);display:flex;flex-direction:column;gap:8px}
.sb-user{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:var(--bg3);border:1px solid var(--border)}
.sb-user-meta{min-width:0}
.sb-user-name{font-size:12.5px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.sb-user-role{font-size:10.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.1em}
.sb-logout{
  display:flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  padding:11px;
  border-radius:12px;
  text-align:center;
  text-decoration:none;
  color:var(--muted);
  font-size:13px;
  font-weight:700;
  border:1px solid var(--border);
  transition:background .18s,color .18s,border-color .18s;
}
.sb-logout:hover{background:var(--accent-soft);color:var(--accent);border-color:rgba(229,9,20,.4)}
.sb-logout svg{width:16px;height:16px}

/* ── mobile bottom nav ─────────────────────────────────────── */
.bottom-nav{
  display:none;
  position:fixed;
  left:0;
  right:0;
  bottom:0;
  z-index:120;
  padding:8px 10px calc(8px + env(safe-area-inset-bottom));
  gap:2px;
  background:var(--glass);
  -webkit-backdrop-filter:blur(20px) saturate(150%);
  backdrop-filter:blur(20px) saturate(150%);
  border-top:1px solid var(--border);
  box-shadow:0 -12px 30px -20px rgba(0,0,0,.8);
}
.bn-item{
  flex:1;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  gap:3px;
  padding:6px 2px;
  border-radius:12px;
  text-decoration:none;
  color:var(--muted);
  font-size:9.5px;
  font-weight:700;
  letter-spacing:.02em;
  transition:color .16s,background .16s;
}
.bn-item svg{width:21px;height:21px}
.bn-item.active{color:var(--accent);background:var(--accent-soft)}

/* ── layout helpers ────────────────────────────────────────── */
.main{
  padding:0 clamp(14px,3.4vw,34px) 48px;
  max-width:1440px;
  margin:0 auto;
  width:100%;
}
.page-head{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:18px;
  flex-wrap:wrap;
  padding:30px 0 18px;
}
.page-eyebrow{
  font-size:11px;
  font-weight:800;
  letter-spacing:.18em;
  text-transform:uppercase;
  color:var(--accent);
  margin-bottom:8px;
  display:flex;
  align-items:center;
  gap:8px;
}
.page-eyebrow::before{content:'';width:18px;height:2px;border-radius:2px;background:var(--accent)}
.page-title{
  font-size:clamp(24px,3.6vw,34px);
  font-weight:800;
  line-height:1.15;
}
.page-sub{color:var(--muted);font-size:14px;margin-top:6px;max-width:60ch}

/* ── generic card ──────────────────────────────────────────── */
.scard{
  background:var(--card);
  padding:24px;
  border-radius:var(--radius);
  position:relative;
  box-shadow:var(--shadow-1);
  border:1px solid var(--border);
  transition:border-color .2s,box-shadow .2s,background .25s;
}
.scard:hover{border-color:var(--border-2)}
.scard-label{font-size:11px;font-weight:800;color:var(--muted);margin-bottom:10px;text-transform:uppercase;letter-spacing:.12em}
.scard-val{font-size:36px;font-weight:800;color:var(--text);margin-bottom:8px;font-variant-numeric:tabular-nums;line-height:1}
.scard-sub{font-size:13px;color:var(--muted);display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.scard.red{border-color:rgba(229,9,20,.35);background:linear-gradient(160deg,rgba(229,9,20,.10),var(--card))}
.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin-bottom:24px}

.big-stat{
  background:linear-gradient(150deg,var(--card) 0%,var(--bg3) 100%);
  padding:38px 22px;
  border-radius:var(--radius-lg);
  text-align:center;
  margin-bottom:26px;
  border:1px solid var(--border);
  box-shadow:var(--shadow-1);
  position:relative;
  overflow:hidden;
}
.big-stat::before{content:'';position:absolute;inset:0;background:radial-gradient(420px 180px at 50% 0,rgba(229,9,20,.16),transparent 70%);pointer-events:none}
.big-stat-val{font-size:clamp(44px,7vw,68px);font-weight:900;color:var(--accent);margin-bottom:8px;line-height:1;letter-spacing:-.03em;font-variant-numeric:tabular-nums}
.big-stat-label{font-size:11.5px;color:var(--muted);font-weight:800;letter-spacing:.22em;text-transform:uppercase}

/* ── search zone (shared base) ─────────────────────────────── */
.search-zone{padding:0 clamp(14px,3.4vw,34px);max-width:1440px;margin:0 auto}
.search-row{display:flex;gap:10px;flex-wrap:wrap}
.search-wrap{flex:1;position:relative;min-width:200px}
.search-input{
  width:100%;
  height:48px;
  background:var(--bg3);
  border:1px solid var(--border);
  border-radius:var(--radius-pill);
  padding:0 18px 0 46px;
  color:var(--text);
  font-size:14.5px;
  font-family:inherit;
  outline:none;
  transition:border-color .18s,box-shadow .18s,background .18s;
}
.search-input::placeholder{color:var(--muted)}
.search-input:focus{border-color:rgba(229,9,20,.55);box-shadow:var(--ring);background:var(--bg3)}
.search-btn{
  display:inline-flex;
  align-items:center;
  justify-content:center;
  gap:8px;
  background:var(--grad);
  color:#fff;
  border:0;
  border-radius:var(--radius-pill);
  height:48px;
  padding:0 26px;
  font-weight:700;
  font-size:14px;
  cursor:pointer;
  box-shadow:0 10px 26px -10px rgba(229,9,20,.85);
  transition:transform .16s,box-shadow .16s,filter .16s;
  white-space:nowrap;
}
.search-btn:hover{transform:translateY(-1px);box-shadow:0 14px 32px -10px rgba(229,9,20,.95);filter:brightness(1.06)}
.search-btn:active{transform:translateY(0) scale(.98)}
.s-icon{position:absolute;left:16px;top:50%;transform:translateY(-50%);color:var(--muted);width:18px;height:18px;pointer-events:none}

/* ── result grid & media cards ─────────────────────────────── */
.results-info{padding:4px 2px 14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap}
.results-count{font-size:12.5px;font-weight:700;color:var(--muted);letter-spacing:.02em}
.res-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(218px,1fr));gap:16px;margin-bottom:26px}
.res-grid.mode-none .poster-box{display:none}
.mode-none .poster-box{display:none}

.file-card{
  background:var(--card);
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--border);
  display:flex;
  flex-direction:column;
  transition:transform .28s cubic-bezier(.2,.8,.2,1),box-shadow .28s,border-color .28s;
  cursor:pointer;
  position:relative;
  box-shadow:0 2px 8px rgba(0,0,0,.25);
}
.file-card:hover{
  transform:translateY(-5px);
  border-color:rgba(229,9,20,.45);
  box-shadow:0 22px 44px -18px rgba(0,0,0,.85),0 0 0 1px rgba(229,9,20,.18);
  z-index:2;
}
.file-card:active{transform:translateY(-2px) scale(.99)}

.poster-box{
  position:relative;
  padding-top:56.25%;
  background:linear-gradient(90deg,var(--bg3) 0px,var(--bg4) 50%,var(--bg3) 100%);
  background-size:200% 100%;
  animation:shimmer 1.6s infinite linear;
  overflow:hidden;
  width:100%;
}
@keyframes shimmer{0%{background-position:200% 0}100%{background-position:-200% 0}}
.poster-box::after{
  content:'';
  position:absolute;
  left:0;right:0;bottom:0;
  height:58%;
  background:linear-gradient(to top,rgba(4,4,8,.86),rgba(4,4,8,.32) 45%,transparent);
  opacity:.9;
  pointer-events:none;
  z-index:2;
}
.fc-poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:0;transition:opacity .35s ease,transform .55s cubic-bezier(.2,.8,.2,1)}
.fc-poster.loaded{opacity:1}
.file-card:hover .fc-poster{transform:scale(1.06)}
.thumb-error{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:var(--bg3);z-index:2;color:var(--muted);font-size:11px}

.poster-top{position:absolute;top:0;left:0;right:0;display:flex;align-items:center;gap:5px;padding:9px;z-index:4}
.type-chip,.size-chip,.source-pill{
  -webkit-backdrop-filter:blur(10px);
  backdrop-filter:blur(10px);
  border-radius:7px;
  padding:3.5px 8px;
  font-size:9.5px;
  font-weight:800;
  letter-spacing:.06em;
  line-height:1.35;
  border:1px solid rgba(255,255,255,.14);
  white-space:nowrap;
}
.type-chip{background:rgba(10,10,14,.72);color:#fff}
.size-chip{background:rgba(10,10,14,.55);color:#e6e6ef;font-weight:600;letter-spacing:.02em}
.source-pill{margin-left:auto;display:inline-flex;align-items:center;gap:4px;letter-spacing:.05em}
.source-pill.primary{background:rgba(20,83,45,.82);color:#6ee7a0;border-color:rgba(34,197,94,.4)}
.source-pill.cloud{background:rgba(20,52,95,.82);color:#9ecbff;border-color:rgba(96,165,250,.4)}
.source-pill.archive{background:rgba(90,38,10,.82);color:#fdc08a;border-color:rgba(251,146,60,.4)}
.source-dot{width:5px;height:5px;border-radius:50%;flex-shrink:0}
.primary .source-dot{background:#22c55e;box-shadow:0 0 6px #22c55e}
.cloud .source-dot{background:#60a5fa;box-shadow:0 0 6px #60a5fa}
.archive .source-dot{background:#fb923c;box-shadow:0 0 6px #fb923c}

/* hover play affordance */
.fc-play{
  position:absolute;
  inset:0;
  margin:auto;
  width:46px;
  height:46px;
  border-radius:50%;
  display:flex;
  align-items:center;
  justify-content:center;
  background:rgba(255,255,255,.14);
  border:1px solid rgba(255,255,255,.55);
  -webkit-backdrop-filter:blur(6px);
  backdrop-filter:blur(6px);
  color:#fff;
  z-index:3;
  opacity:0;
  transform:scale(.75);
  transition:opacity .22s,transform .22s;
  pointer-events:none;
}
.fc-play svg{width:16px;height:16px;margin-left:2px;fill:currentColor}
.file-card:hover .fc-play{opacity:1;transform:scale(1)}

.fc-body{padding:11px 12px 13px;flex:1;display:flex;flex-direction:column;gap:6px;justify-content:flex-start}
.fc-name{
  color:var(--text);
  font-size:12.8px;
  font-weight:600;
  line-height:1.45;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
  cursor:pointer;
  transition:color .16s;
  text-decoration:none;
}
.fc-name:hover{color:var(--accent)}
.fc-text-info{display:flex;align-items:center;gap:6px;padding:11px 12px 0;flex-wrap:wrap}
.tc-type{background:var(--bg4);color:var(--muted);border-radius:6px;padding:2px 7px;font-size:9px;font-weight:800;letter-spacing:.08em;border:1px solid var(--border)}
.tc-size{color:var(--muted);font-size:11px}

/* admin hover actions */
.poster-admin{position:absolute;left:0;right:0;bottom:0;display:flex;gap:6px;padding:8px;opacity:0;transform:translateY(8px);transition:opacity .2s,transform .22s;pointer-events:none;z-index:5}
.file-card.admin-active .poster-admin{opacity:1;transform:translateY(0);pointer-events:all}
.text-admin-row{display:none;gap:6px;padding:6px 12px 0}
.file-card.admin-active .text-admin-row{display:flex}
.btn-edit,.btn-del{flex:1;padding:7px 0;border-radius:8px;font-size:11px;font-weight:700;cursor:pointer;border:1px solid transparent;transition:background .14s,transform .12s}
.btn-edit{background:rgba(30,30,40,.92);color:#fff;border-color:rgba(255,255,255,.18);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.btn-edit:hover{background:rgba(58,58,76,.96)}
.btn-del{background:rgba(150,10,16,.82);color:#fff;border-color:rgba(229,9,20,.45);-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px)}
.btn-del:hover{background:rgba(229,9,20,.95)}
.poster-wrap{position:relative;overflow:hidden}

/* staggered entrance */
@keyframes cardEnter{0%{opacity:0;transform:translateY(22px) scale(.97)}60%{opacity:1;transform:translateY(-2px) scale(1.004)}100%{opacity:1;transform:translateY(0) scale(1)}}
.card-enter{opacity:0}
.card-enter.card-visible{animation:cardEnter .5s cubic-bezier(.25,.9,.3,1) forwards}

/* states */
.spin-wrap{display:flex;flex-direction:column;align-items:center;gap:14px;padding:64px 20px;color:var(--muted);grid-column:1/-1;font-size:13px}
.spinner{width:34px;height:34px;border:3px solid var(--border);border-top-color:var(--accent);border-radius:50%;animation:spin .8s linear infinite}
@keyframes spin{to{transform:rotate(360deg)}}
.empty{text-align:center;padding:64px 20px;color:var(--muted);grid-column:1/-1;display:flex;flex-direction:column;align-items:center;gap:6px}
.empty-icon{
  width:64px;height:64px;border-radius:20px;
  display:flex;align-items:center;justify-content:center;
  font-size:26px;
  background:var(--bg3);
  border:1px solid var(--border);
  margin-bottom:10px;
  box-shadow:var(--shadow-1);
}
.empty p{font-size:14px;max-width:36ch;line-height:1.6}
.empty b{color:var(--text)}

/* ── pagination ────────────────────────────────────────────── */
.pagination{display:none;align-items:center;justify-content:center;gap:12px;margin:6px 0 40px;padding-bottom:10px;flex-wrap:wrap}
.pg-btn{
  background:var(--bg3);
  color:var(--text);
  border:1px solid var(--border);
  border-radius:12px;
  padding:10px 20px;
  font-size:12.5px;
  font-weight:700;
  cursor:pointer;
  transition:background .16s,transform .14s,box-shadow .16s,color .16s,border-color .16s;
}
.pg-btn:disabled{opacity:.42;cursor:not-allowed}
.pg-btn:not(:disabled):hover{background:var(--grad);color:#fff;border-color:transparent;box-shadow:0 10px 24px -10px rgba(229,9,20,.9)}
.pg-btn:not(:disabled):active{transform:scale(.96)}
.pg-info{color:var(--muted);font-size:12px;font-weight:700;letter-spacing:.04em;padding:0 4px}
.pg-bar{display:flex;align-items:center;gap:6px}

/* ── toast ─────────────────────────────────────────────────── */
.toast{
  position:fixed;
  left:50%;
  bottom:26px;
  transform:translate(-50%,140%);
  background:rgba(18,18,26,.96);
  -webkit-backdrop-filter:blur(16px);
  backdrop-filter:blur(16px);
  color:#fff;
  padding:13px 20px 13px 16px;
  border-radius:14px;
  font-weight:600;
  font-size:13.5px;
  z-index:300;
  border:1px solid rgba(255,255,255,.12);
  border-left:3px solid var(--mint);
  box-shadow:0 20px 50px rgba(0,0,0,.6);
  max-width:min(92vw,440px);
  transition:transform .32s cubic-bezier(.2,.8,.2,1),opacity .3s;
  opacity:0;
}
.toast.show{transform:translate(-50%,0);opacity:1}
.toast.error{border-left-color:var(--accent)}

/* ── auth pages ────────────────────────────────────────────── */
.login-bg{
  min-height:100vh;
  display:flex;
  flex-direction:column;
  position:relative;
  isolation:isolate;
  background:
    radial-gradient(900px 620px at 12% 0,rgba(229,9,20,.26),transparent 60%),
    radial-gradient(760px 560px at 92% 12%,rgba(168,85,247,.20),transparent 62%),
    radial-gradient(900px 700px at 50% 118%,rgba(76,154,255,.16),transparent 62%),
    linear-gradient(180deg,#0a0a10,#050508 70%);
}
html.light .login-bg,.light .login-bg{
  background:
    radial-gradient(900px 620px at 12% 0,rgba(229,9,20,.14),transparent 60%),
    radial-gradient(760px 560px at 92% 12%,rgba(168,85,247,.12),transparent 62%),
    linear-gradient(180deg,#f7f8fb,#eef0f6 70%);
}
.login-bg::before{
  content:'';
  position:absolute;
  inset:0;
  z-index:-1;
  background-image:radial-gradient(rgba(255,255,255,.055) 1px,transparent 1px);
  background-size:22px 22px;
  -webkit-mask-image:radial-gradient(circle at 50% 38%,#000 0%,transparent 72%);
  mask-image:radial-gradient(circle at 50% 38%,#000 0%,transparent 72%);
}
html.light .login-bg::before,.light .login-bg::before{background-image:radial-gradient(rgba(10,12,24,.07) 1px,transparent 1px)}
.login-bg .topbar{position:relative;background:transparent;border-bottom:none;box-shadow:none;-webkit-backdrop-filter:none;backdrop-filter:none}
.login-wrap{flex:1;display:flex;align-items:center;justify-content:center;padding:28px 18px 44px}
.login-card{
  background:linear-gradient(165deg,rgba(22,22,32,.92),rgba(12,12,18,.96));
  -webkit-backdrop-filter:blur(26px) saturate(150%);
  backdrop-filter:blur(26px) saturate(150%);
  padding:38px 34px 34px;
  border-radius:22px;
  width:100%;
  max-width:440px;
  box-shadow:var(--shadow-2);
  border:1px solid rgba(255,255,255,.10);
  position:relative;
}
.login-card::before{
  content:'';
  position:absolute;
  inset:0 0 auto 0;
  height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.4),transparent);
  border-radius:22px 22px 0 0;
}
html.light .login-card,.light .login-card{
  background:linear-gradient(165deg,rgba(255,255,255,.96),rgba(248,249,252,.98));
  border-color:rgba(12,14,28,.08);
}
.login-brand{display:flex;justify-content:center;margin-bottom:18px}
.login-brand .nf-icon{width:46px;height:46px;border-radius:14px;font-size:20px}
.login-card h2{font-size:25px;font-weight:800;margin-bottom:8px;text-align:center;line-height:1.2}
.login-sub{text-align:center;color:var(--muted);font-size:13.5px;margin-bottom:24px;line-height:1.55}
.login-card label.field-label{display:block;font-size:11px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin:0 0 7px 2px}
.login-card input{
  width:100%;
  background:rgba(255,255,255,.045);
  border:1px solid var(--border);
  padding:13px 15px;
  color:var(--text);
  margin-bottom:15px;
  border-radius:12px;
  outline:none;
  font-size:14px;
  font-family:inherit;
  transition:border-color .18s,box-shadow .18s,background .18s;
}
html.light .login-card input,.light .login-card input{background:rgba(10,12,24,.028)}
.login-card input::placeholder{color:var(--muted);opacity:.8}
.login-card input:focus{border-color:rgba(229,9,20,.55);box-shadow:var(--ring);background:rgba(255,255,255,.06)}
html.light .login-card input:focus,.light .login-card input:focus{background:#fff}
.login-card .submit-btn{
  width:100%;
  background:var(--grad);
  color:#fff;
  border:0;
  padding:14px;
  font-weight:800;
  font-size:14.5px;
  margin-top:8px;
  border-radius:12px;
  cursor:pointer;
  letter-spacing:.01em;
  box-shadow:0 14px 30px -12px rgba(229,9,20,.95);
  transition:transform .16s,filter .16s,box-shadow .16s;
}
.login-card .submit-btn:hover{filter:brightness(1.07);transform:translateY(-1px)}
.login-card .submit-btn:active{transform:translateY(0) scale(.99)}
.login-foot{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:18px;font-size:13px}
.login-foot a{color:var(--muted);text-decoration:none;transition:color .16s}
.login-foot a:hover{color:var(--text)}
.login-foot a.strong{color:var(--text);font-weight:700}
.login-foot a.strong:hover{color:var(--accent)}
.login-note{display:flex;align-items:center;gap:9px;margin-top:20px;padding:11px 13px;border-radius:12px;background:rgba(76,154,255,.10);border:1px solid rgba(76,154,255,.24);font-size:11.5px;color:var(--muted);line-height:1.5}
.login-note svg{width:16px;height:16px;flex-shrink:0;color:var(--sky)}
.err-box{background:rgba(232,124,3,.14);border:1px solid rgba(232,124,3,.4);color:#fbbf24;padding:11px 14px;border-radius:11px;margin-bottom:16px;font-size:12.5px;font-weight:600}
.success-box{background:rgba(40,167,69,.14);border:1px solid rgba(40,167,69,.4);color:#4ade80;padding:11px 14px;border-radius:11px;margin-bottom:16px;font-size:12.5px;font-weight:600}

/* ── modal (admin edit) ────────────────────────────────────── */
.edit-modal{
  position:fixed;
  inset:0;
  background:rgba(3,3,6,.82);
  -webkit-backdrop-filter:blur(8px);
  backdrop-filter:blur(8px);
  z-index:200;
  display:flex;
  align-items:center;
  justify-content:center;
  opacity:0;
  pointer-events:none;
  transition:opacity .2s;
  overflow-y:auto;
  padding:20px 12px;
}
.edit-modal.open{opacity:1;pointer-events:all}
.em-card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:18px;
  padding:24px;
  width:100%;
  max-width:480px;
  box-shadow:var(--shadow-2);
  position:relative;
  margin:auto;
}
.em-close{position:absolute;top:14px;right:16px;background:var(--bg3);border:1px solid var(--border);width:30px;height:30px;border-radius:9px;color:var(--muted);font-size:14px;cursor:pointer;z-index:10}
.em-close:hover{color:var(--text);background:var(--bg4)}
.em-title{font-size:17px;font-weight:800;margin-bottom:18px;display:flex;align-items:center;gap:8px}
.em-input{width:100%;background:var(--bg3);border:1px solid var(--border);padding:11px 13px;color:var(--text);margin-bottom:14px;border-radius:11px;outline:none;font-size:13.5px;font-family:inherit}
.em-input:focus{border-color:rgba(229,9,20,.5);box-shadow:var(--ring)}
.thumb-preview-box{width:100%;aspect-ratio:16/9;background:var(--bg3);border:1px solid var(--border);border-radius:12px;margin-bottom:14px;overflow:hidden;position:relative;display:flex;align-items:center;justify-content:center}
.t-prev-img{max-width:100%;max-height:100%;object-fit:contain}
.em-upload-btn{display:block;text-align:center;background:var(--bg3);border:1px dashed var(--border-2);padding:12px;border-radius:12px;cursor:pointer;font-weight:700;font-size:12.5px;margin-bottom:16px;transition:background .18s,border-color .18s}
.em-upload-btn:hover{background:var(--bg4);border-color:var(--accent)}
.em-save-btn{width:100%;background:var(--grad);color:#fff;border:0;padding:13px;font-weight:800;border-radius:12px;cursor:pointer;font-size:14px;transition:filter .16s,transform .16s}
.em-save-btn:hover{filter:brightness(1.07)}
.em-save-btn:disabled{opacity:.5;cursor:not-allowed}
.cropper-container-box{width:100%;aspect-ratio:16/9;margin-bottom:14px;border-radius:12px;overflow:hidden;display:none;background:#000}

/* ── actor cards ───────────────────────────────────────────── */
.act-card{
  background:var(--card);
  border:1px solid var(--border);
  border-radius:16px;
  overflow:hidden;
  transition:transform .24s cubic-bezier(.2,.8,.2,1),border-color .24s,box-shadow .24s;
  cursor:pointer;
  box-shadow:0 2px 8px rgba(0,0,0,.22);
}
.act-card:hover{transform:translateY(-5px);border-color:rgba(229,9,20,.45);box-shadow:0 22px 44px -20px rgba(0,0,0,.85)}
.act-card:active{transform:scale(.985)}
.act-poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .45s cubic-bezier(.2,.8,.2,1)}
.act-card:hover .act-poster{transform:scale(1.07)}
.act-text-card:active{transform:scale(.985)}
.card-body{padding:12px}

/* ── stat / telemetry atoms (used by stats page) ───────────── */
.st-card,.hero-stat,.t-card,.scard{border-radius:var(--radius)}
.thumb-badge{display:inline-flex;align-items:center;gap:5px;font-size:11px;background:var(--bg3);border:1px solid var(--border);border-radius:8px;padding:4px 10px;color:var(--muted)}
.pct-label{font-size:13px;font-weight:800}
.prog-wrap{background:var(--bg4);border-radius:99px;height:5px;margin-bottom:10px;overflow:hidden}
.prog-bar{height:100%;border-radius:99px}
.user-sub-row{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:12px}
.user-sub-cell{background:var(--bg3);border:1px solid var(--border);border-radius:10px;padding:9px 12px}
.user-sub-cell-lbl{font-size:10px;color:var(--muted);margin-bottom:2px}
.user-sub-cell-val{font-size:15px;font-weight:800;font-variant-numeric:tabular-nums}
.flush-btn{margin-top:12px;width:100%;background:transparent;border:1px solid var(--border);border-radius:10px;padding:9px 12px;font-size:12px;font-weight:700;color:var(--muted);cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center;gap:6px}
.flush-btn:hover{background:var(--bg3);color:var(--text);border-color:var(--accent)}

/* ── misc utility ──────────────────────────────────────────── */
.tag{
  background:var(--bg3);
  border:1px solid var(--border);
  padding:8px 16px;
  border-radius:var(--radius-pill);
  font-size:12.5px;
  font-weight:700;
  cursor:pointer;
  color:var(--text);
  transition:background .16s,color .16s,border-color .16s,transform .16s;
}
.tag:hover{background:var(--accent);color:#fff;border-color:transparent;transform:translateY(-1px)}
.hidden{display:none!important}

/* responsive shell */
@media (max-width:820px){
  :root{--topbar-h:60px}
  body{padding-bottom:74px}
  .bottom-nav{display:flex}
  .logo{font-size:14px;letter-spacing:.1em}
  .login-card{padding:30px 22px 26px;border-radius:18px}
  .res-grid{grid-template-columns:repeat(auto-fill,minmax(156px,1fr));gap:12px}
  .fc-body{padding:9px 10px 11px}
  .fc-name{font-size:11.8px}
  .page-head{padding:22px 0 12px}
}
@media (max-width:420px){
  .res-grid{grid-template-columns:1fr 1fr}
  .avatar{display:none}
}

/* desktop: sidebar is permanent, content shifts right */
@media (min-width:1180px) and (min-height:620px){
  body.with-sidebar{padding-left:var(--sidebar-w)}
  body.with-sidebar .sidebar{transform:none;box-shadow:none}
  body.with-sidebar .sidebar-overlay{display:none}
  body.with-sidebar .ham-btn{display:none}
  body.with-sidebar .bottom-nav{display:none}
  body.with-sidebar .sb-close{display:none}
  body.with-sidebar .sidebar{background:linear-gradient(180deg,var(--bg2) 0%,var(--bg) 62%)}
}


/* ── shared search UI used by the posts / actors directory pages ──── */
.search-box{
  border-radius:var(--radius)!important;
  border-color:var(--border)!important;
  padding:14px!important;
  box-shadow:var(--shadow-1)!important;
}
.s-input{
  height:46px;
  border-radius:var(--radius-pill)!important;
  padding:0 18px!important;
  background:var(--bg3)!important;
  font-size:14px!important;
  font-weight:500!important;
}
.s-input:focus{border-color:rgba(229,9,20,.55)!important;box-shadow:var(--ring)!important}
.s-btn{
  height:46px;
  border-radius:var(--radius-pill)!important;
  padding:0 22px!important;
  background:var(--grad)!important;
  font-weight:700!important;
  letter-spacing:.01em;
  box-shadow:0 10px 26px -12px rgba(229,9,20,.9)!important;
}
.s-btn:hover{filter:brightness(1.06)!important;transform:translateY(-1px)!important;background:var(--grad)!important}
.search-box .cdd-wrap{
  border-radius:var(--radius-pill)!important;
  border:1px solid var(--border)!important;
  background:var(--bg3)!important;
  padding:11px 15px!important;
  font-size:12px!important;
}
.search-box .cdd-wrap:hover{border-color:rgba(229,9,20,.45)!important}
.search-box .cdd-menu{border-radius:14px!important;border:1px solid var(--border-2)!important;box-shadow:var(--shadow-2)!important}
.search-box .cdd-item{font-size:12.5px!important}

/* accessibility */
@media (prefers-reduced-motion:reduce){
  *,*::before,*::after{animation-duration:.001ms!important;animation-iteration-count:1!important;transition-duration:.001ms!important;scroll-behavior:auto!important}
}
"""

JS = """
(function(){if(localStorage.getItem('theme')==='light')document.documentElement.classList.add('light')})();
function toggleThemeFixed(){var l=document.documentElement.classList.toggle('light');localStorage.setItem('theme',l?'light':'dark');}
function openSidebar(){document.getElementById('sidebar').classList.add('open');document.getElementById('sbOverlay').classList.add('open');document.getElementById('hamBtn').classList.add('open');}
function closeSidebar(){document.getElementById('sidebar').classList.remove('open');document.getElementById('sbOverlay').classList.remove('open');document.getElementById('hamBtn').classList.remove('open');}
var curQ='',curOff=0,nextOff='',curCol='all',curPage=1;
var pMode=localStorage.getItem('posterMode')||'tg';
var LIMIT_VAL = __LIMIT_PLACEHOLDER__;

var activeFid = '', activeCol = '', cropperInstance = null;

function handleThumbError(fileId) {
    var img = document.getElementById('img-poster-' + fileId);
    if (img) { img.style.opacity = '0'; }
    var errBox = document.getElementById('thumb-err-' + fileId);
    if (!errBox) {
        var box = document.getElementById('poster-box-' + fileId);
        if (box) {
            var div = document.createElement('div');
            div.id = 'thumb-err-' + fileId;
            div.className = 'thumb-error';
            div.innerHTML = '<div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#1f1f1f; padding:10px;"><span style="font-size:11px; color:var(--muted); text-align:center;">थंबनेल लोड नहीं हुआ</span></div>';
            box.appendChild(div);
        }
    }
}

async function reloadThumb(fileId) {
    var timestamp = new Date().getTime();
    var img = document.getElementById('img-poster-' + fileId);
    if (img) {
        img.src = '/api/thumb?file_id=' + fileId + '&retry=true&t=' + timestamp;
        img.classList.remove('loaded');
    }
    var errBox = document.getElementById('thumb-err-' + fileId);
    if (errBox) { errBox.remove(); }
}

var _tt;
function showToast(m,t){
    t=t||'success';
    var x=document.getElementById('toast');
    if(!x){x=document.createElement('div');x.id='toast';x.className='toast';document.body.appendChild(x);}
    x.textContent=m;x.className='toast '+t+' show';
    clearTimeout(_tt);
    _tt=setTimeout(function(){x.classList.remove('show');},3000);
}

function toggleAdminBtns(card,e){
    e.stopPropagation();
    var isActive=card.classList.contains('admin-active');
    document.querySelectorAll('.file-card.admin-active').forEach(function(c){c.classList.remove('admin-active');});
    if(!isActive) card.classList.add('admin-active');
}

document.addEventListener('click',function(){
    document.querySelectorAll('.file-card.admin-active').forEach(function(c){c.classList.remove('admin-active');});
});

async function deleteFile(fid,col){
    if(!confirm('Are you sure you want to delete this file?'))return;
    try{
        var r=await fetch('/api/delete',{method:'POST',body:JSON.stringify({file_id:fid,collection:col}),headers:{'Content-Type':'application/json'}});
        var res=await r.json();
        if(res.success){ showToast('✅ File deleted successfully!'); refreshGridAfterEdit(); }
        else{ showToast(res.error||'Delete failed!','error'); }
    }catch(e){showToast('Delete failed','error');}
}

function editFile(fid, col, encName, encCaption){
    var currentName = decodeURIComponent(encName);
    var currentCaption = (encCaption && encCaption !== 'undefined') ? decodeURIComponent(encCaption) : '';
    activeFid = fid; activeCol = col;
    if(cropperInstance){cropperInstance.destroy();cropperInstance=null;}
    document.getElementById('emName').value=currentName;
    document.getElementById('emFile').value='';
    document.getElementById('cropContainer').style.display='none';
    if(document.getElementById('emMoveCol')) document.getElementById('emMoveCol').value = col;
    if(document.getElementById('emAddCaption')) document.getElementById('emAddCaption').value = currentCaption;
    
    var prevBox=document.getElementById('emPreviewBox');
    prevBox.style.display='flex';
    prevBox.innerHTML='<img src="/api/thumb?file_id='+fid+'&col='+activeCol+'" class="t-prev-img" onerror="this.src=\\'https://placehold.co/600x338/181818/FFF?text=No+Thumbnail\\';">';
    document.getElementById('editCombinedModal').classList.add('open');
}

function closeCombinedModal(){
    document.getElementById('editCombinedModal').classList.remove('open');
    if(cropperInstance){cropperInstance.destroy();cropperInstance=null;}
}

function handleLocalPreview(input){
    if(input.files&&input.files[0]){
        var reader=new FileReader();
        reader.onload=function(e){
            if(cropperInstance) cropperInstance.destroy();
            document.getElementById('emPreviewBox').style.display='none';
            var cropWrap=document.getElementById('cropContainer');
            cropWrap.style.display='block';
            cropWrap.innerHTML='<img id="cropImage" src="'+e.target.result+'" style="max-width:100%;">';
            var img=document.getElementById('cropImage');
            cropperInstance=new Cropper(img,{aspectRatio:16/9,viewMode:1,background:false,zoomable:true,movable:true});
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function saveAllChanges(){
    var newName=document.getElementById('emName').value.trim();
    var addCaption=document.getElementById('emAddCaption') ? document.getElementById('emAddCaption').value.trim() : '';
    var moveCol=document.getElementById('emMoveCol') ? document.getElementById('emMoveCol').value : activeCol;
    if(!newName){showToast('File name cannot be empty!','error');return;}
    
    var btn=document.getElementById('emSaveBtn');
    btn.disabled=true; btn.innerText='Processing...';
    try{
        var thumbUpdated = false;
        
        if(cropperInstance){
            showToast('✂️ Cropping & Uploading...');
            var canvas=cropperInstance.getCroppedCanvas({width:1280,height:720,imageSmoothingEnabled:true,imageSmoothingQuality:'high'});
            var blob=await new Promise(r=>canvas.toBlob(r,'image/jpeg',0.9));
            if(blob){
                var fd=new FormData(); fd.append('file_id',activeFid); fd.append('collection',activeCol); fd.append('image',blob,'cropped.jpg');
                var upRes=await fetch('/api/upload_thumb',{method:'POST',body:fd});
                var upData=await upRes.json();
                if(!upData.success){showToast('Upload failed!','error'); btn.disabled=false; btn.innerText='Save Changes'; return;}
                thumbUpdated = true;
            }
        }
        var payload = { file_id: activeFid, collection: activeCol, new_name: newName, add_caption: addCaption, target_collection: moveCol };
        var r=await fetch('/api/edit_name',{method:'POST',body:JSON.stringify(payload),headers:{'Content-Type':'application/json'}});
        var res=await r.json();
        
        if(res.success||cropperInstance){
            showToast('✨ File updated successfully!');
            closeCombinedModal();
            
            if (activeCol !== moveCol) {
                refreshGridAfterEdit();
                return;
            }
            
            var nameElement = document.getElementById('name-title-' + activeFid);
            if (nameElement) nameElement.innerText = newName;
            
            if (thumbUpdated) reloadThumb(activeFid);
            
        } else showToast(res.error||'Update failed!','error');
    }catch(e){showToast('Network Error','error');}
    finally{btn.disabled=false; btn.innerText='Save Changes';}
}

function refreshGridAfterEdit() {
    if (typeof doSearch === 'function') doSearch(curOff);
    else if (typeof triggerActorSearchAjax === 'function') triggerActorSearchAjax();
    else window.location.reload();
}
function staggerCards(container){
    var cards=container.querySelectorAll('.card-enter');
    if(!cards.length) return;
    var seen=0;
    var obs=new IntersectionObserver(function(entries){
        entries.forEach(function(entry){
            if(!entry.isIntersecting) return;
            var c=entry.target;
            var delay=Math.min(seen,10)*0.08; seen++;
            c.style.animationDelay=delay+'s';
            c.classList.add('card-visible');
            var totalDur=(0.6+delay)*1000;
            setTimeout(function(){ c.classList.remove('card-enter','card-visible'); c.style.animationDelay=''; },totalDur);
            obs.unobserve(c);
        });
    },{threshold:0.08});
    cards.forEach(function(c){ obs.observe(c); });
}
""".replace("__LIMIT_PLACEHOLDER__", str(MAX_WEB_RESULTS))

def _h(html): return web.Response(text=html.encode('utf-8','replace').decode('utf-8'), content_type='text/html', charset='utf-8')

async def get_auth(req):
    s_user = req.cookies.get('user_session')
    if s_user and hasattr(temp, 'USER_SESSIONS') and s_user in temp.USER_SESSIONS and temp.USER_SESSIONS[s_user]['expiry'] > time.time():
        tg_id = temp.USER_SESSIONS[s_user]['tg_id']
        if tg_id in ADMINS: return 'admin', tg_id
        return 'user', tg_id
    return None, None

# ✅ FIX: यह एक ही जगह से premium/plan चेक करने वाला shared helper है।
# पहले सिर्फ dashboard_routes.py अपने अंदर यह चेक करता था, actors/posts पेज नहीं करते थे
# जिससे expired user login करके /actors और /posts freely खोल सकता था (sync issue)।
# अब सभी route files (dashboard, actors, posts) इसी एक function को call करेंगे,
# ताकि logic कहीं भी duplicate न हो और तीनों जगह एक जैसा behave करे।
async def require_active_plan(role, tg_id):
    """Admin हमेशा allowed. 'user' role के लिए plan.premium चेक होता है।"""
    if role != 'user':
        return True
    mp = await user_db.get_plan(tg_id)
    return bool(mp.get("premium"))

# ─────────────────────────────────────────────────────────────────────────────
# 🧩 INLINE ICON SET (stroke icons, single source of truth)
# ─────────────────────────────────────────────────────────────────────────────
def _svg(paths, sw=1.8, extra=""):
    return (f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"{extra}>{paths}</svg>')

_ICONS = {
    "home":     _svg('<path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/>'),
    "posts":    _svg('<rect x="3" y="4.5" width="18" height="15" rx="3"/><path d="M7.5 9h9M7.5 12.5h9M7.5 16h5"/>'),
    "actors":   _svg('<circle cx="12" cy="8.2" r="3.6"/><path d="M4.8 20c.7-3.6 3.6-5.4 7.2-5.4s6.5 1.8 7.2 5.4"/>'),
    "stats":    _svg('<path d="M4 20V10"/><path d="M10 20V4"/><path d="M16 20v-7"/><path d="M22 20H2"/>'),
    "profile":  _svg('<circle cx="12" cy="8" r="3.4"/><path d="M5 20c.8-3.4 3.6-5.1 7-5.1s6.2 1.7 7 5.1"/>'),
    "logout":   _svg('<path d="M15 17l5-5-5-5"/><path d="M20 12H9"/><path d="M12 4H6.5A2.5 2.5 0 0 0 4 6.5v11A2.5 2.5 0 0 0 6.5 20H12"/>'),
    "search":   _svg('<circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/>'),
    "sun":      '<svg class="t-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/></svg>',
    "moon":     '<svg class="t-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.2A8.6 8.6 0 0 1 9.8 3.5 8.7 8.7 0 1 0 20.5 14.2Z"/></svg>',
    "shield":   _svg('<path d="M12 3l7 3v5.5c0 4.2-2.9 7.6-7 9.5-4.1-1.9-7-5.3-7-9.5V6l7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/>'),
}

_NAV = {
    "dash":    ("home",    "/dashboard", "Home"),
    "posts":   ("posts",   "/posts",     "Posts"),
    "actors":  ("actors",  "/actors",    "Actors"),
    "stats":   ("stats",   "/stats",     "Database Stats"),
    "profile": ("profile", "/profile",   "Profile Settings"),
}
_ADMIN_TABS = ("dash", "posts", "actors", "stats", "profile")
_USER_TABS = ("dash", "posts", "actors", "profile")
_MOBILE_LABELS = {"dash": "Home", "posts": "Posts", "actors": "Actors", "stats": "Stats", "profile": "Profile"}


def _sidebar_link(key, active_tab):
    icon, href, label = _NAV[key]
    act = " active" if active_tab == key else ""
    return f'<a href="{href}" class="sb-link{act}">{_ICONS[icon]}<span>{label}</span></a>'


def _bottom_link(key, active_tab):
    icon, href, label = _NAV[key]
    act = " active" if active_tab == key else ""
    return f'<a href="{href}" class="bn-item{act}">{_ICONS[icon]}<span>{_MOBILE_LABELS[key]}</span></a>'


def _theme_button():
    return (f'<button class="theme-btn" onclick="toggleThemeFixed()" aria-label="Toggle colour theme" '
            f'title="Toggle theme">{_ICONS["sun"]}{_ICONS["moon"]}</button>')


def build_page(title, body, cls="", active_tab="", role=None):
    tabs = _ADMIN_TABS if role == "admin" else _USER_TABS if role == "user" else ()

    if role:
        primary = "".join(_sidebar_link(k, active_tab) for k in tabs if k != "profile")
        role_label = "Administrator" if role == "admin" else "Premium Member"
        initial = "A" if role == "admin" else "U"
        nav_links = (f'<div class="sb-section">Discover</div>{primary}'
                     f'<div class="sb-section">Account</div>{_sidebar_link("profile", active_tab)}')

        nav = (
            '<div class="sidebar-overlay" id="sbOverlay" onclick="closeSidebar()"></div>'
            '<aside class="sidebar" id="sidebar" aria-label="Main navigation">'
                '<div class="sb-header">'
                    f'<div class="sb-logo"><span class="nf-icon">F</span><div><div>FAST FINDER</div><div class="sb-brand-sub">Media Cloud</div></div></div>'
                    '<button class="sb-close" onclick="closeSidebar()" aria-label="Close menu">&#10005;</button>'
                '</div>'
                f'<nav class="sb-nav">{nav_links}</nav>'
                '<div class="sb-footer">'
                    f'<div class="sb-user"><span class="avatar{" admin" if role == "admin" else ""}">{initial}</span>'
                        f'<div class="sb-user-meta"><div class="sb-user-name">Signed in</div><div class="sb-user-role">{role_label}</div></div>'
                    '</div>'
                    f'<a href="/logout" class="sb-logout">{_ICONS["logout"]}<span>Sign out</span></a>'
                '</div>'
            '</aside>'
            '<header class="topbar">'
                '<button class="ham-btn" id="hamBtn" onclick="openSidebar()" aria-label="Open menu">'
                    '<span class="ham-line"></span><span class="ham-line"></span><span class="ham-line"></span>'
                '</button>'
                f'<a class="logo" href="/dashboard"><span class="nf-icon">F</span><span class="logo-text">FAST <b>FINDER</b></span></a>'
                f'<div class="topbar-right">{_theme_button()}'
                    f'<a href="/profile" class="avatar{" admin" if role == "admin" else ""}" title="{role_label}">{initial}</a>'
                '</div>'
            '</header>'
            f'<nav class="bottom-nav">{"".join(_bottom_link(k, active_tab) for k in tabs)}</nav>'
        )
        body_cls = f"{cls} with-sidebar".strip()
    else:
        nav = (
            '<header class="topbar" style="position:absolute;width:100%;background:transparent;'
            'border-bottom:none;box-shadow:none;-webkit-backdrop-filter:none;backdrop-filter:none;">'
                f'<a class="logo" href="/"><span class="nf-icon">F</span><span class="logo-text">FAST <b>FINDER</b></span></a>'
                f'<div class="topbar-right">{_theme_button()}</div>'
            '</header>'
        )
        body_cls = cls

    modals = """
    <div class="edit-modal" id="editCombinedModal" onclick="if(event.target===this)closeCombinedModal()">
        <div class="em-card">
            <button class="em-close" onclick="closeCombinedModal()">&#10005;</button>
            <div class="em-title">✏️ Edit Title Metadata</div>

            <div class="scard-label">File Name</div>
            <input type="text" id="emName" class="em-input">

            <div class="scard-label" style="margin-top:5px;">➕ Add Search Tags to Caption (Optional)</div>
            <input type="text" id="emAddCaption" class="em-input" placeholder="e.g. Ajay Devgan, 1080p, Comedy...">

            <div class="scard-label">📂 Move File to Collection</div>
            <select id="emMoveCol" class="em-input" style="font-weight:600; cursor:pointer;">
                <option value="primary">🟢 Primary</option>
                <option value="cloud">🔵 Cloud</option>
                <option value="archive">🟠 Archive</option>
            </select>

            <div class="scard-label" style="margin-top:5px;">Poster Thumbnail (YouTube Studio Mode)</div>
            <div class="thumb-preview-box" id="emPreviewBox"></div>
            <div class="cropper-container-box" id="cropContainer"></div>

            <label class="em-upload-btn">
                📂 Choose New Image / Poster
                <input type="file" id="emFile" accept="image/*" style="display:none;" onchange="handleLocalPreview(this)">
            </label>

            <button class="em-save-btn" id="emSaveBtn" onclick="saveAllChanges()">Save Changes</button>
        </div>
    </div>
    """ if role == 'admin' else ""

    shell_js = """
    <script>
    (function(){
      var sb=document.getElementById('sidebar');
      document.addEventListener('keydown',function(e){ if(e.key==='Escape' && sb && sb.classList.contains('open')) closeSidebar(); });
      document.querySelectorAll('.sb-link, .sb-logout').forEach(function(a){
        a.addEventListener('click',function(){ if(sb && sb.classList.contains('open')) closeSidebar(); });
      });
    })();
    </script>
    """

    return _h(
        f'<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        f'<meta name="theme-color" content="#08080b">'
        f'<title>{title}</title>'
        f'<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700;900&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">'
        f'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.css">'
        f'<style>{CSS}</style>'
        f'<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.6.1/cropper.min.js"></script>'
        f'<script>{JS}</script></head><body class="{body_cls}">{nav}{body}{modals}{shell_js}</body></html>'
    )


def form_wrapper(title, content, err="", msg="", subtitle=""):
    e = f'<div class="err-box">{err}</div>' if err else ""
    m = f'<div class="success-box">{msg}</div>' if msg else ""
    sub = f'<p class="login-sub">{subtitle}</p>' if subtitle else ""
    note = (
        f'<div class="login-note">{_ICONS["shield"]}'
        '<span>Secured by Telegram OTP — your password is stored hashed, never in plain text.</span></div>'
    )
    return (
        f'<div class="login-wrap"><div class="login-card">'
        f'<div class="login-brand"><span class="nf-icon">F</span></div>'
        f'<h2>{title}</h2>{sub}{e}{m}{content}{note}'
        f'</div></div>'
    )
