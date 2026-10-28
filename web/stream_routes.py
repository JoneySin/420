import math, secrets, mimetypes, logging
from urllib.parse import quote
from aiohttp import web
from info import BIN_CHANNEL
from utils import temp
from web.utils.custom_dl import TGCustomYield, chunk_size, offset_fix
from web.utils.render_template import media_watch

routes = web.RouteTableDef()
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🏠 ROOT ROUTE
# ─────────────────────────────────────────────
@routes.get("/", allow_head=True)
async def root_route_handler(request):
    bot_username = getattr(temp, 'U_NAME', 'AutoFilterBot')

    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#08080b">
<title>Fast Finder — Movies, Series &amp; More</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Sora:wght@600;700;800&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#07070a;--card:#101019;--bg3:#15151f;--border:#252535;
  --text:#f7f7fa;--muted:#9b9bad;--accent:#e50914;--accent2:#ff5a4d;
  --shadow:0 26px 70px rgba(0,0,0,.6);
}
html.light{--bg:#f6f7fa;--card:#fff;--bg3:#eef0f5;--border:#e0e4ee;--text:#0d0d16;--muted:#5d6072;--shadow:0 26px 60px rgba(16,18,30,.14)}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--bg);color:var(--text);min-height:100vh;overflow-x:hidden;line-height:1.55;-webkit-font-smoothing:antialiased;transition:background .25s,color .25s}
h1,h2,h3{font-family:'Sora','DM Sans',sans-serif;letter-spacing:-.025em}
a{color:inherit;text-decoration:none}
:focus-visible{outline:none;box-shadow:0 0 0 3px rgba(229,9,20,.25);border-radius:10px}

.bg{position:fixed;inset:0;z-index:-2;pointer-events:none;background:
  radial-gradient(900px 600px at 10% -10%,rgba(229,9,20,.30),transparent 60%),
  radial-gradient(760px 620px at 92% 0%,rgba(168,85,247,.22),transparent 62%),
  radial-gradient(900px 700px at 50% 108%,rgba(76,154,255,.16),transparent 62%);
}
.bg::after{content:'';position:absolute;inset:0;background-image:radial-gradient(rgba(255,255,255,.055) 1px,transparent 1px);background-size:24px 24px;-webkit-mask-image:radial-gradient(circle at 50% 30%,#000,transparent 72%);mask-image:radial-gradient(circle at 50% 30%,#000,transparent 72%)}
html.light .bg{background:radial-gradient(900px 600px at 10% -10%,rgba(229,9,20,.16),transparent 60%),radial-gradient(760px 620px at 92% 0%,rgba(168,85,247,.12),transparent 62%)}
html.light .bg::after{background-image:radial-gradient(rgba(12,14,26,.07) 1px,transparent 1px)}

.navbar{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:18px clamp(16px,5vw,56px);position:sticky;top:0;z-index:20;background:linear-gradient(to bottom,rgba(7,7,10,.86),rgba(7,7,10,0));-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px)}
html.light .navbar{background:linear-gradient(to bottom,rgba(246,247,250,.92),rgba(246,247,250,0))}
.logo{font-family:'Sora',sans-serif;font-size:15px;font-weight:800;letter-spacing:.14em;display:inline-flex;align-items:center;gap:10px}
.logo b{color:var(--accent)}
.nf-icon{width:32px;height:32px;border-radius:10px;background:linear-gradient(135deg,#e50914,#ff5a4d);color:#fff;display:inline-flex;align-items:center;justify-content:center;font-size:15px;font-weight:900;box-shadow:0 6px 18px rgba(229,9,20,.45)}
.header-actions{display:flex;align-items:center;gap:9px}
.theme-btn{width:38px;height:38px;display:inline-flex;align-items:center;justify-content:center;background:rgba(255,255,255,.05);border:1px solid var(--border);border-radius:11px;color:var(--muted);cursor:pointer;transition:.18s}
html.light .theme-btn{background:#fff}
.theme-btn:hover{color:var(--text);border-color:var(--muted)}
.theme-btn svg{width:17px;height:17px}
.theme-btn .t-moon{display:none}
html.light .theme-btn .t-moon{display:block}
html.light .theme-btn .t-sun{display:none}
.admin-btn{display:inline-flex;align-items:center;gap:8px;padding:0 20px;height:38px;border-radius:11px;font-weight:700;font-size:13.5px;color:var(--text);border:1px solid var(--border);background:rgba(255,255,255,.05);transition:.18s}
html.light .admin-btn{background:#fff}
.admin-btn:hover{border-color:var(--accent);color:var(--accent);transform:translateY(-1px)}

.hero{max-width:1080px;margin:0 auto;padding:clamp(28px,7vw,72px) clamp(16px,5vw,40px) 0;text-align:center}
.pill{display:inline-flex;align-items:center;gap:8px;padding:6px 14px 6px 9px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid var(--border);font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin-bottom:20px}
html.light .pill{background:#fff}
.pill .dot{width:7px;height:7px;border-radius:50%;background:#2dd4a7;box-shadow:0 0 10px #2dd4a7}
.hero h1{font-size:clamp(34px,6.6vw,62px);font-weight:800;line-height:1.04;margin-bottom:16px}
.hero h1 .grad{background:linear-gradient(100deg,#ff6b5f,#e50914 55%,#a855f7);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p.sub{color:var(--muted);font-size:clamp(14px,1.9vw,17px);max-width:56ch;margin:0 auto 28px}
.search-shell{max-width:660px;margin:0 auto;display:flex;gap:9px;padding:8px;border-radius:999px;background:rgba(255,255,255,.05);border:1px solid var(--border);box-shadow:var(--shadow);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);transition:border-color .2s,box-shadow .2s}
html.light .search-shell{background:#fff}
.search-shell:focus-within{border-color:rgba(229,9,20,.55);box-shadow:var(--shadow),0 0 0 4px rgba(229,9,20,.12)}
.search-shell .s-ico{display:flex;align-items:center;padding-left:14px;color:var(--muted)}
.search-shell svg{width:19px;height:19px}
#searchInput{flex:1;min-width:0;background:transparent;border:0;outline:none;color:var(--text);font-size:15.5px;font-family:inherit;padding:0 4px}
#searchInput::placeholder{color:var(--muted)}
.search-btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;border:0;border-radius:999px;background:linear-gradient(135deg,#e50914,#ff5a4d);color:#fff;height:46px;padding:0 26px;font-size:14.5px;font-weight:700;font-family:inherit;cursor:pointer;box-shadow:0 12px 28px -10px rgba(229,9,20,.9);transition:transform .16s,filter .16s;white-space:nowrap}
.search-btn:hover{transform:translateY(-1px);filter:brightness(1.06)}
.search-btn:active{transform:scale(.98)}
.helper{font-size:11.5px;color:var(--muted);margin-top:12px}
.helper b{color:var(--text)}
.quick-picks{margin-top:26px;display:flex;flex-wrap:wrap;justify-content:center;gap:8px;align-items:center}
.qp-title{width:100%;font-size:10.5px;color:var(--muted);font-weight:800;letter-spacing:.18em;text-transform:uppercase;margin-bottom:6px}
.tag{background:rgba(255,255,255,.05);border:1px solid var(--border);padding:8px 16px;border-radius:999px;font-size:12.5px;font-weight:700;cursor:pointer;color:var(--text);font-family:inherit;transition:.18s}
html.light .tag{background:#fff}
.tag:hover{background:var(--accent);border-color:transparent;color:#fff;transform:translateY(-1px)}

.features{max-width:1080px;margin:clamp(44px,7vw,84px) auto 0;padding:0 clamp(16px,5vw,40px);display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.f-card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:22px;box-shadow:var(--shadow);position:relative;overflow:hidden;transition:transform .22s,border-color .22s}
.f-card:hover{transform:translateY(-4px);border-color:rgba(229,9,20,.4)}
.f-ico{width:40px;height:40px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:rgba(229,9,20,.12);border:1px solid rgba(229,9,20,.28);color:var(--accent);margin-bottom:14px}
.f-ico svg{width:20px;height:20px}
.f-card h3{font-size:15px;margin-bottom:7px;font-weight:700}
.f-card p{font-size:13px;color:var(--muted);line-height:1.6}
.steps{max-width:1080px;margin:clamp(28px,4vw,44px) auto 0;padding:0 clamp(16px,5vw,40px) 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.step{display:flex;gap:13px;align-items:flex-start;padding:16px 18px;border-radius:16px;border:1px dashed var(--border);background:rgba(255,255,255,.02)}
html.light .step{background:#fff}
.step-n{width:30px;height:30px;flex-shrink:0;border-radius:9px;background:var(--bg3);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-weight:800;font-size:13px;color:var(--accent)}
.step h4{font-size:13.5px;margin-bottom:3px}
.step p{font-size:12.5px;color:var(--muted);line-height:1.55}
footer{max-width:1080px;margin:clamp(40px,6vw,72px) auto 0;padding:24px clamp(16px,5vw,40px) 40px;display:flex;justify-content:space-between;gap:14px;flex-wrap:wrap;align-items:center;border-top:1px solid var(--border);font-size:12px;color:var(--muted)}
footer a{color:var(--text);font-weight:600}
@media(max-width:600px){
  .search-shell{flex-direction:column;border-radius:22px;padding:10px;gap:8px}
  .search-shell .s-ico{display:none}
  #searchInput{padding:12px 14px;background:rgba(255,255,255,.04);border-radius:14px;font-size:15px}
  html.light #searchInput{background:var(--bg3)}
  .search-btn{width:100%;height:46px}
  .hero{padding-top:20px}
  .admin-btn{padding:0 14px;font-size:12.5px}
  .logo{font-size:12.5px;letter-spacing:.1em}
}
@media(prefers-reduced-motion:reduce){*{animation-duration:.001ms!important;transition-duration:.001ms!important}}
</style>
</head>
<body>
<div class="bg"></div>
<header class="navbar">
  <a href="/" class="logo"><span class="nf-icon">F</span> FAST <b>FINDER</b></a>
  <div class="header-actions">
    <button class="theme-btn" id="theme-btn" aria-label="Toggle theme">
      <svg class="t-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.2 5.2l1.4 1.4M17.4 17.4l1.4 1.4M18.8 5.2l-1.4 1.4M6.6 17.4l-1.4 1.4"/></svg>
      <svg class="t-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 14.2A8.6 8.6 0 0 1 9.8 3.5 8.7 8.7 0 1 0 20.5 14.2Z"/></svg>
    </button>
    <a href="/login" class="admin-btn">Sign in</a>
  </div>
</header>

<main class="hero">
  <div class="pill"><span class="dot"></span> Live library · powered by Telegram</div>
  <h1>Every movie.<br><span class="grad">One search away.</span></h1>
  <p class="sub">Stream and download movies, series, anime and more — instantly, straight from our Telegram cloud. No ads, no waiting rooms.</p>

  <div class="search-shell">
    <span class="s-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg></span>
    <input type="text" id="searchInput" placeholder="Search a title, actor or genre…" autocomplete="off" spellcheck="false">
    <button class="search-btn" onclick="startSearch()">Search
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h13"/><path d="m12 5 7 7-7 7"/></svg>
    </button>
  </div>
  <p class="helper">Press <b>Enter</b> — we open our Telegram bot with your search ready.</p>

  <div class="quick-picks">
    <div class="qp-title">Trending searches</div>
    <button class="tag" onclick="fillAndSearch('Action')">Action</button>
    <button class="tag" onclick="fillAndSearch('Comedy')">Comedy</button>
    <button class="tag" onclick="fillAndSearch('Thriller')">Thriller</button>
    <button class="tag" onclick="fillAndSearch('Anime')">Anime</button>
    <button class="tag" onclick="fillAndSearch('4K')">4K UHD</button>
    <button class="tag" onclick="fillAndSearch('Sci-Fi')">Sci-Fi</button>
    <button class="tag" onclick="fillAndSearch('Web Series')">Web Series</button>
  </div>
</main>

<section class="features">
  <div class="f-card">
    <div class="f-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2 4.5 13.5H11l-1 8.5 8.5-11.5H12l1-8.5Z"/></svg></div>
    <h3>Instant results</h3>
    <p>Indexed captions and filenames make every title findable in milliseconds — even across huge archives.</p>
  </div>
  <div class="f-card">
    <div class="f-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><rect x="2.5" y="5" width="19" height="14" rx="3"/><path d="m10 9.5 5 2.5-5 2.5v-5Z"/></svg></div>
    <h3>Stream in-app</h3>
    <p>A built-in player with resume, quality switching and 10-second skip gestures. Or grab the file directly.</p>
  </div>
  <div class="f-card">
    <div class="f-ico"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l7 3v5.5c0 4.2-2.9 7.6-7 9.5-4.1-1.9-7-5.3-7-9.5V6l7-3Z"/><path d="m9 12 2.2 2.2L15.5 10"/></svg></div>
    <h3>Private by design</h3>
    <p>Your account is linked to Telegram with a one-time OTP. Passwords are hashed — never stored in plain text.</p>
  </div>
</section>

<section class="steps">
  <div class="step"><div class="step-n">1</div><div><h4>Search here</h4><p>Type any title above to jump straight into the bot.</p></div></div>
  <div class="step"><div class="step-n">2</div><div><h4>Open the bot</h4><p>Tap the result you want and press play inside Telegram.</p></div></div>
  <div class="step"><div class="step-n">3</div><div><h4>Sign in to the web</h4><p>Unlock the full dashboard: posters, filters and collections.</p></div></div>
</section>

<footer>
  <span>&copy; Fast Finder · Media Cloud</span>
  <span><a href="/login">Sign in</a> &nbsp;·&nbsp; <a href="https://t.me/BOT_USERNAME_PLACEHOLDER" target="_blank" rel="noopener">Open Telegram bot</a></span>
</footer>

<script>
(function(){ if(localStorage.getItem('theme')==='light')document.documentElement.classList.add('light'); })();
document.getElementById('theme-btn').addEventListener('click',function(){
  var isLight=document.documentElement.classList.toggle('light');
  localStorage.setItem('theme',isLight?'light':'dark');
});
function startSearch(){
  var q=document.getElementById('searchInput').value.trim();
  var base='https://t.me/BOT_USERNAME_PLACEHOLDER';
  window.open(q?base+'?start='+encodeURIComponent(q):base,'_blank');
}
function fillAndSearch(q){
  document.getElementById('searchInput').value=q;
  startSearch();
}
document.getElementById('searchInput').addEventListener('keydown',function(e){
  if(e.key==='Enter')startSearch();
});
</script>
</body>
</html>
""".replace("BOT_USERNAME_PLACEHOLDER", bot_username)

    return web.Response(text=html_content, content_type='text/html')


# ─────────────────────────────────────────────
# 📺 STREAM / WATCH ROUTE
# ─────────────────────────────────────────────
@routes.get("/watch/{message_id}")
async def watch_handler(request):
    try:
        return web.Response(
            text=await media_watch(int(request.match_info['message_id'])),
            content_type='text/html'
        )
    except ValueError:
        return web.Response(status=400, text="Invalid Message ID")
    except Exception as e:
        logger.error(f"Watch Error: {e}")
        return web.Response(status=500, text="Internal Server Error")


# ─────────────────────────────────────────────
# 📥 DOWNLOAD & STREAMING CORE
# ─────────────────────────────────────────────
@routes.get("/download/{message_id}")
async def download_handler(request):
    try:
        return await media_download(request, int(request.match_info['message_id']))
    except ValueError:
        return web.Response(status=400, text="Invalid Message ID")
    except Exception as e:
        logger.error(f"Download Error: {e}")
        return web.Response(status=500, text="Internal Server Error")


async def media_download(request, message_id: int):
    try:
        media_msg = await temp.BOT.get_messages(BIN_CHANNEL, message_id)
        media = getattr(media_msg, media_msg.media.value, None) if media_msg and media_msg.media else None
        if not media:
            return web.Response(status=404, text="Media Not Supported or Not Found")

        file_size = media.file_size
        file_name = getattr(media, 'file_name', None)
        if not file_name:
            file_name = (
                f"video_{secrets.token_hex(3)}.mp4"
                if getattr(media_msg, 'video', None)
                else f"file_{secrets.token_hex(3)}.bin"
            )

        mime_type = (
            getattr(media, 'mime_type', None)
            or mimetypes.guess_type(file_name)[0]
            or "application/octet-stream"
        )

        # ── Range Header Parse ──
        try:
            r_head = request.headers.get('Range')
            if r_head:
                parts_str = r_head.replace('bytes=', '').split('-')
                fb = int(parts_str[0]) if parts_str[0] else 0
                ub = int(parts_str[1]) if parts_str[1] else file_size - 1
            else:
                fb, ub = 0, file_size - 1
        except Exception:
            fb, ub = 0, file_size - 1

        # ── Clamp / Validate ──
        ub = min(ub, file_size - 1)
        if fb < 0 or ub < fb:
            return web.Response(
                status=416,
                body="416: Range Not Satisfiable",
                headers={"Content-Range": f"bytes */{file_size}"}
            )

        req_len = ub - fb + 1

        # ✅ FIX: chunk_size और offset_fix अब plain def हैं — await हटाया
        ncs    = chunk_size(req_len)
        offset = offset_fix(fb, ncs)

        # ✅ FIX: parts की सही गणना
        #    पुराना: math.ceil(req_len / ncs) — गलत था जब offset और fb में gap हो
        #    नया:   offset से ub तक का पूरा span cover करो
        first_cut = fb - offset
        last_cut  = (ub % ncs) + 1
        parts     = math.ceil((req_len + first_cut) / ncs)

        body = TGCustomYield().yield_file(
            media_msg, offset, first_cut, last_cut, parts, ncs
        )

        enc_fn = quote(file_name)

        return web.Response(
            status=206 if r_head else 200,
            body=body,
            headers={
                "Content-Type":        mime_type,
                "Content-Range":       f"bytes {fb}-{ub}/{file_size}",
                "Content-Disposition": f'attachment; filename="{enc_fn}"; filename*=UTF-8\'\'{enc_fn}',
                "Accept-Ranges":       "bytes",
                "Content-Length":      str(req_len),
            }
        )

    except Exception as e:
        logger.error(f"Stream Error: {e}")
        return web.Response(status=500, text="Server Error")
