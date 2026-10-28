from aiohttp import web
from web.web_assets import build_page, get_auth, form_wrapper, MAX_WEB_RESULTS, require_active_plan
from utils import temp

dashboard_routes = web.RouteTableDef()

# ─────────────────────────────────────────────────────────────────────────────
# 🎨 DASHBOARD SPECIFIC CSS (सिर्फ सर्च बार और ड्रॉपडाउन के लिए, कार्ड्स ग्लोबल हैं)
# ─────────────────────────────────────────────────────────────────────────────
# ── inline icons used by the search toolbar ──
ICON_SEARCH = '<svg class="s-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>'
ICON_SEARCH_BTN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round"><circle cx="11" cy="11" r="6.5"/><path d="m16 16 4.5 4.5"/></svg>'
ICON_FOLDER = '<svg class="cdd-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7.5A2.5 2.5 0 0 1 5.5 5h3.1c.6 0 1.2.2 1.6.7l1 1.3h7.3A2.5 2.5 0 0 1 21 9.5v7A2.5 2.5 0 0 1 18.5 19h-13A2.5 2.5 0 0 1 3 16.5Z"/></svg>'
ICON_IMAGE = '<svg class="cdd-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4.5" width="18" height="15" rx="2.5"/><circle cx="8.5" cy="10" r="1.6"/><path d="m4 17 5-4.5 4 3.5 3-2.5 4 3.5"/></svg>'

CARD_CSS = """<style>
/* ═══════════════════════════════════════════════════════════════════
   DASHBOARD — search experience
   (global tokens, cards and grid live in web_assets.py)
   ═══════════════════════════════════════════════════════════════════ */

/* ── hero ─────────────────────────────────────────────────── */
.dash-hero{padding:clamp(22px,4vw,40px) 2px 20px;max-width:760px}
.dash-hero .page-title{font-size:clamp(26px,4.4vw,40px);line-height:1.08}
.dash-hero .page-sub{font-size:14.5px;margin-top:10px;max-width:52ch}
.quick-chips{display:flex;flex-wrap:wrap;gap:8px;margin-top:18px}
.quick-chips .tag{font-size:12px;padding:7px 14px;background:var(--card);box-shadow:var(--shadow-1)}
.quick-chips .tag:hover{box-shadow:0 10px 22px -10px rgba(229,9,20,.9)}

/* ── search toolbar ───────────────────────────────────────── */
.toolbar{display:flex;gap:10px;align-items:center;position:relative;z-index:30}
.toolbar .search-wrap{flex:1;min-width:0}
.toolbar .search-input{
  height:52px;
  padding-left:46px;
  padding-right:96px;
  background:var(--card);
  border:1px solid var(--border);
  border-radius:var(--radius-pill);
  font-size:15px;
  font-weight:500;
  box-shadow:var(--shadow-1);
}
.toolbar .search-input:focus{border-color:rgba(229,9,20,.55);box-shadow:var(--shadow-1),var(--ring)}
.s-icon{position:absolute;left:17px;top:50%;transform:translateY(-50%);width:18px;height:18px;color:var(--muted);pointer-events:none}
.kbd-hint{
  position:absolute;
  right:16px;
  top:50%;
  transform:translateY(-50%);
  display:inline-flex;
  align-items:center;
  gap:4px;
  font-size:10.5px;
  font-weight:700;
  color:var(--muted);
  pointer-events:none;
  letter-spacing:.04em;
}
.kbd-hint kbd{
  font-family:inherit;
  background:var(--bg3);
  border:1px solid var(--border);
  border-bottom-width:2px;
  border-radius:6px;
  padding:1px 6px;
  font-size:10px;
  color:var(--text);
}
.search-btn{height:52px;padding:0 28px;border-radius:var(--radius-pill);font-size:14.5px;position:relative;overflow:hidden}
.search-btn svg{width:17px;height:17px}
.search-btn::after{content:'';position:absolute;inset:0;background:rgba(255,255,255,0);border-radius:inherit;pointer-events:none}
.search-btn.ripple-go::after{animation:btnRipple .45s ease-out forwards}
@keyframes btnRipple{0%{background:rgba(255,255,255,.30);transform:scale(.6)}100%{background:rgba(255,255,255,0);transform:scale(1.65)}}

/* ── filter row ───────────────────────────────────────────── */
.filters{
  display:flex;
  align-items:center;
  gap:8px;
  flex-wrap:wrap;
  margin-top:14px;
  padding-bottom:6px;
}
.filters .results-info{padding:0;margin-left:auto}
.cdd-wrap{position:relative;user-select:none;flex:0 0 auto}
.cdd-btn{
  display:inline-flex;
  align-items:center;
  gap:8px;
  background:var(--card);
  color:var(--text);
  border:1px solid var(--border);
  border-radius:var(--radius-pill);
  padding:9px 34px 9px 14px;
  font-size:12px;
  font-weight:700;
  font-family:inherit;
  cursor:pointer;
  white-space:nowrap;
  box-shadow:var(--shadow-1);
  transition:border-color .16s,background .16s,box-shadow .16s;
}
.cdd-btn:hover{border-color:var(--border-2);background:var(--bg3)}
.cdd-btn.open{border-color:rgba(229,9,20,.5);box-shadow:var(--ring)}
.cdd-btn .cdd-ico{width:15px;height:15px;color:var(--muted);flex-shrink:0}
.cdd-arrow{
  position:absolute;
  right:13px;
  top:50%;
  transform:translateY(-50%);
  pointer-events:none;
  font-size:8px;
  color:var(--muted);
  transition:transform .2s;
}
.cdd-btn.open + .cdd-arrow{transform:translateY(-50%) rotate(180deg)}
.cdd-menu{
  position:absolute;
  top:calc(100% + 8px);
  left:0;
  min-width:210px;
  background:var(--bg2);
  border:1px solid var(--border-2);
  border-radius:14px;
  overflow:hidden;
  z-index:9999;
  box-shadow:var(--shadow-2);
  animation:cddIn .16s ease;
  padding:5px;
}
@keyframes cddIn{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:translateY(0)}}
.cdd-item{
  display:flex;
  align-items:center;
  gap:9px;
  padding:10px 11px;
  font-size:12.5px;
  font-weight:600;
  color:var(--text);
  cursor:pointer;
  border-radius:9px;
  transition:background .13s;
}
.cdd-item:hover{background:var(--bg3)}
.cdd-item.selected{color:var(--text);background:var(--accent-soft)}
.cdd-radio{
  width:17px;
  height:17px;
  border-radius:50%;
  border:2px solid var(--border-2);
  margin-left:auto;
  flex-shrink:0;
  display:flex;
  align-items:center;
  justify-content:center;
  transition:border-color .15s;
}
.cdd-item.selected .cdd-radio{border-color:var(--accent)}
.cdd-radio-dot{width:7px;height:7px;border-radius:50%;background:var(--accent);display:none}
.cdd-item.selected .cdd-radio-dot{display:block}

/* results header */
.results-head{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  flex-wrap:wrap;
  padding:22px 2px 14px;
}
.results-title{font-size:13px;font-weight:800;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:9px}
.results-title::before{content:'';width:3px;height:14px;border-radius:2px;background:var(--accent)}
.results-count{font-size:12.5px;font-weight:700;color:var(--muted)}
.results-count b{color:var(--text)}
@media(max-width:560px){
  .kbd-hint{display:none}
  .toolbar .search-input{padding-right:18px}
  .toolbar{flex-wrap:wrap}
  .toolbar .search-wrap{flex:1 1 100%}
  .toolbar .search-btn{flex:1 1 100%}
  .dash-hero .page-title{font-size:27px}
}

/* ── trending rail ────────────────────────────────────────── */
.rail{margin:26px 0 4px}
.rail[style*="none"]{display:none}
.rail-head{display:flex;align-items:baseline;gap:10px;margin-bottom:12px}
.rail-head h2{font-size:17px;font-weight:800;letter-spacing:-.01em}
.rail-note{font-size:11.5px;color:var(--muted);font-weight:600}
.rail-scroll{
  display:grid;
  grid-auto-flow:column;
  grid-auto-columns:minmax(196px,196px);
  gap:12px;
  overflow-x:auto;
  padding-bottom:8px;
  scroll-snap-type:x mandatory;
  scrollbar-width:thin;
}
.rail-scroll::-webkit-scrollbar{height:6px}
.rail-card{
  display:flex;
  flex-direction:column;
  text-decoration:none;
  border-radius:14px;
  overflow:hidden;
  border:1px solid var(--border);
  background:var(--card);
  scroll-snap-align:start;
  transition:transform .2s,border-color .2s,box-shadow .2s;
  box-shadow:0 2px 8px rgba(0,0,0,.22);
}
.rail-card:hover{transform:translateY(-4px);border-color:rgba(229,9,20,.45);box-shadow:0 18px 36px -18px rgba(0,0,0,.85)}
.rail-thumb{display:block;position:relative;aspect-ratio:16/9;background:var(--bg3);overflow:hidden}
.rail-thumb img{width:100%;height:100%;object-fit:cover;transition:transform .35s}
.rail-card:hover .rail-thumb img{transform:scale(1.05)}
.rail-thumb img.broken{opacity:0}
.rail-pill{
  position:absolute;top:7px;left:7px;font-size:9px;font-weight:800;letter-spacing:.05em;
  padding:3px 7px;border-radius:6px;border:1px solid rgba(255,255,255,.16);
  background:rgba(10,10,14,.7);color:#fff;-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px);
}
.rail-pill.primary{color:#6ee7a0;border-color:rgba(34,197,94,.4)}
.rail-pill.cloud{color:#9ecbff;border-color:rgba(96,165,250,.4)}
.rail-pill.archive{color:#fdc08a;border-color:rgba(251,146,60,.4)}
.rail-body{display:flex;flex-direction:column;gap:3px;padding:9px 10px 11px}
.rail-name{font-size:11.8px;font-weight:600;line-height:1.4;color:var(--text);
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.rail-sub{font-size:10.5px;color:var(--muted);font-weight:600;letter-spacing:.02em}
@media(max-width:560px){
  .rail-scroll{grid-auto-columns:minmax(164px,164px);gap:10px}
}
</style>
"""

# ─────────────────────────────────────────────────────────────────────────────
# 🎬 JS ENGINE — Smart Double Pre-fetching Engine Live Live
# ─────────────────────────────────────────────────────────────────────────────
JS_ENGINE = """
var curQ='',curOff=0,nextOff='',curCol='all',curPage=1;
var pMode=localStorage.getItem('posterMode')||'tg';
var LIMIT_VAL = __LIMIT_PLACEHOLDER__;

function closeCdds(){
    document.getElementById('cddColMenu').style.display='none';
    document.getElementById('cddColBtn').classList.remove('open');
    document.getElementById('cddModeMenu').style.display='none';
    document.getElementById('cddModeBtn').classList.remove('open');
}
function toggleCdd(which,e){
    if(e){e.stopPropagation();}
    var menuId=which==='col'?'cddColMenu':'cddModeMenu';
    var btnId=which==='col'?'cddColBtn':'cddModeBtn';
    var otherId=which==='col'?'cddModeMenu':'cddColMenu';
    var otherBtnId=which==='col'?'cddModeBtn':'cddColBtn';
    var menu=document.getElementById(menuId);
    var btn=document.getElementById(btnId);
    var isOpen=menu.style.display!=='none';
    document.getElementById(otherId).style.display='none';
    document.getElementById(otherBtnId).classList.remove('open');
    if(isOpen){menu.style.display='none';btn.classList.remove('open');}
    else{menu.style.display='block';btn.classList.add('open');}
}
function pickCol(val,label,el,e){
    if(e){e.stopPropagation();}
    curCol=val;
    document.getElementById('cddColLabel').textContent=label;
    document.querySelectorAll('#cddColMenu .cdd-item').forEach(function(i){i.classList.remove('selected');});
    el.classList.add('selected');
    document.getElementById('cddColMenu').style.display='none';
    document.getElementById('cddColBtn').classList.remove('open');
    if(curQ)doSearch(0);
}
function pickMode(val,label,el,e){
    if(e){e.stopPropagation();}
    pMode=val;
    localStorage.setItem('posterMode',pMode);
    document.getElementById('cddModeLabel').textContent=label;
    document.querySelectorAll('#cddModeMenu .cdd-item').forEach(function(i){i.classList.remove('selected');});
    el.classList.add('selected');
    document.getElementById('cddModeMenu').style.display='none';
    document.getElementById('cddModeBtn').classList.remove('open');
    if(curQ)doSearch(curOff);
}
document.addEventListener('click',function(e){
    if(!e.target.closest('.cdd-wrap')){closeCdds();}
});
document.querySelectorAll('.cdd-menu').forEach(function(m){
    m.addEventListener('click',function(e){e.stopPropagation();});
});
function changeCol(val){curCol=val;if(curQ)doSearch(0);}

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
            div.innerHTML = '<span style="font-size:11px;color:var(--muted);">थंबनेल लोड नहीं हुआ</span>';
            box.appendChild(div);
        }
    }
}

function triggerRipple(btn){btn.classList.remove('ripple-go');void btn.offsetWidth;btn.classList.add('ripple-go');setTimeout(function(){btn.classList.remove('ripple-go');},460);}

async function doSearch(o){
    var q=document.getElementById('q').value.trim();
    if(!q){showToast('Please enter a movie name','error');return;}
    curQ=q;curOff=o;if(o===0)curPage=1;

    var rail=document.getElementById('trending');
    if(rail)rail.style.display='none';
    var resDiv=document.getElementById('results');
    resDiv.className='res-grid mode-'+pMode;
    resDiv.innerHTML='<div class="spin-wrap"><div class="spinner"></div><span>Searching...</span></div>';

    try{
        var r=await fetch('/api/search?q='+encodeURIComponent(q)+'&offset='+o+'&col='+curCol+'&mode='+pMode);
        if(!r.ok){showToast('Error fetching','error');return;}
        var d=await r.json();
        if(d.error){showToast(d.error,'error');return;}
        var rc=document.getElementById('resCount');
        if(!d.results||!d.results.length){
            if(rc)rc.innerHTML='';
            resDiv.innerHTML='<div class="empty"><div class="empty-icon">&#128533;</div><p><b>No titles found for \\u201c'+q+'\\u201d</b><br>Try a shorter keyword, another spelling, or switch collection.</p></div>';
            document.getElementById('pageBox').style.display='none';return;
        }
        if(rc)rc.innerHTML='<b>'+d.results.length+'</b> result'+(d.results.length===1?'':'s')+' for \\u201c'+q+'\\u201d';
        var h='';
        d.results.forEach(function(f){
            var sc=(f.source||'primary').toLowerCase();
            if(!['primary','cloud','archive'].includes(sc))sc='primary';

            var encName = encodeURIComponent(f.name || '').replace(/'/g, "%27").replace(/"/g, "%22");
            var encCap = encodeURIComponent(f.caption || '').replace(/'/g, "%27").replace(/"/g, "%22");

            var adminBtns='';
            if(d.is_admin){
                adminBtns='<div class="poster-admin">'+
                    '<button class="btn-edit" onclick="event.stopPropagation();editFile(\\''+f.file_id+'\\',\\''+f.raw_collection+'\\',\\''+encName+'\\', \\''+encCap+'\\')">&#9999; Edit</button>'+
                    '<button class="btn-del" onclick="event.stopPropagation();deleteFile(\\''+f.file_id+'\\',\\''+f.raw_collection+'\\')">&#128465; Delete</button>'+
                '</div>';
            }

            var posterHtml='';
            if(pMode!=='none'){
                posterHtml='<div class="poster-box" id="poster-box-'+f.file_id+'" onclick="toggleAdminBtns(this.closest(\\'.file-card\\'),event)">'+
                    '<img src="'+f.tg_thumb+'" id="img-poster-'+f.file_id+'" class="fc-poster" onload="this.classList.add(\\'loaded\\')" onerror="handleThumbError(\\''+f.file_id+'\\')" loading="lazy" decoding="async">'+
                    '<div class="poster-top">'+
                        '<span class="type-chip">'+f.type.toUpperCase()+'</span>'+
                        '<span class="size-chip">'+f.size+'</span>'+
                        '<span class="source-pill '+sc+'"><span class="source-dot"></span>'+sc.toUpperCase()+'</span>'+
                    '</div>'+
                    '<span class="fc-play"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></span>'+
                    adminBtns+
                '</div>';
            }

            var textInfo='';
            if(pMode==='none'){
                textInfo='<div class="fc-text-info" onclick="toggleAdminBtns(this.closest(\\'.file-card\\'),event)">'+
                    '<span class="tc-type">'+f.type.toUpperCase()+'</span>'+
                    '<span class="tc-size">'+f.size+'</span>'+
                    '<span class="source-pill '+sc+'" style="margin-left:auto"><span class="source-dot"></span>'+sc.toUpperCase()+'</span>'+
                '</div>';
                if(d.is_admin){
                    textInfo+='<div class="text-admin-row">'+
                        '<button class="btn-edit" onclick="event.stopPropagation();editFile(\\''+f.file_id+'\\',\\''+f.raw_collection+'\\',\\''+encName+'\\', \\''+encCap+'\\')">&#9999; Edit</button>'+
                        '<button class="btn-del" onclick="event.stopPropagation();deleteFile(\\''+f.file_id+'\\',\\''+f.raw_collection+'\\')">&#128465; Delete</button>'+
                    '</div>';
                }
            }

            h+='<div class="file-card card-enter">'+
                posterHtml+
                textInfo+
                '<div class="fc-body">'+
                    '<div class="fc-name" id="name-title-'+f.file_id+'" onclick="window.open(\\''+f.watch+'\\',\\'_blank\\')">'+f.name+'</div>'+
                '</div>'+
            '</div>';
        });
        resDiv.innerHTML=h;
        staggerCards(resDiv);
        nextOff=d.next_offset;
        document.getElementById('pageBox').style.display='flex';
        document.getElementById('pBtn').disabled=(o===0);
        document.getElementById('nBtn').disabled=!nextOff;
        document.getElementById('pgInfo').textContent='Page '+curPage;

        if(nextOff) {
            fetch('/api/search?q='+encodeURIComponent(q)+'&offset='+nextOff+'&col='+curCol+'&mode='+pMode);
        }
    }catch(e){showToast('Network error','error');}
}

function next(){if(nextOff){curPage++;doSearch(nextOff);scrollTo(0,0);}}
function prev(){if(curPage>1){curPage--;doSearch(Math.max(0,curOff-LIMIT_VAL));scrollTo(0,0);}}

async function loadTrending(){
    var rail=document.getElementById('trending');
    if(!rail)return;
    try{
        var r=await fetch('/api/search?q=2024&offset=0&col=all&mode=tg');
        if(!r.ok)return;
        var d=await r.json();
        if(!d.results||!d.results.length){rail.style.display='none';return;}
        var cards=d.results.slice(0,8).map(function(f){
            var sc=(f.source||'primary').toLowerCase();
            if(['primary','cloud','archive'].indexOf(sc)<0)sc='primary';
            return '<a class="rail-card" href="'+f.watch+'" target="_blank" rel="noopener">'+
                '<span class="rail-thumb"><img src="'+f.tg_thumb+'" alt="" loading="lazy" onerror="this.style.opacity=0">'+
                    '<span class="rail-pill '+sc+'">'+f.source+'</span></span>'+
                '<span class="rail-body"><span class="rail-name">'+f.name+'</span>'+
                    '<span class="rail-sub">'+f.size+' · '+f.type+'</span></span>'+
            '</a>';
        }).join('');
        rail.innerHTML='<div class="rail-head"><h2>Trending now</h2><span class="rail-note">Fresh in the library</span></div>'+
            '<div class="rail-scroll">'+cards+'</div>';
    }catch(e){ rail.style.display='none'; }
}

function quickSearch(term){
    var q=document.getElementById('q');
    if(!q)return;
    q.value=term;
    doSearch(0);
}
document.addEventListener('keydown',function(e){
    if(e.key!=='/'||e.ctrlKey||e.metaKey||e.altKey)return;
    var t=e.target.tagName;
    if(t==='INPUT'||t==='TEXTAREA'||t==='SELECT'||e.target.isContentEditable)return;
    var q=document.getElementById('q');
    if(q){e.preventDefault();q.focus();q.select();}
});

document.addEventListener('DOMContentLoaded',function(){
    loadTrending();
    var q=document.getElementById('q');if(q)q.addEventListener('keydown',function(e){if(e.key==='Enter')doSearch(0);});
    if(pMode==='none'){
        var mItems=document.querySelectorAll('#cddModeMenu .cdd-item');
        mItems.forEach(function(i){i.classList.remove('selected');if(i.dataset.val===pMode)i.classList.add('selected');});
        document.getElementById('cddModeLabel').textContent='\u26a1 Text Only (Fastest)';
    }
});
""".replace("__LIMIT_PLACEHOLDER__", str(MAX_WEB_RESULTS))

# ─────────────────────────────────────────────────────────────────────────────
# 🏠 SEARCH ZONE HTML
# ─────────────────────────────────────────────────────────────────────────────
SEARCH_ZONE = (
    '<div class="search-zone">'
        '<div class="dash-hero">'
            '<div class="page-eyebrow">Instant library search</div>'
            '<h1 class="page-title">What do you want to watch?</h1>'
            '<p class="page-sub">Titles, people, genres and qualities \u2014 searched live across every collection.</p>'
            '<div class="quick-chips">'
                '<button class="tag" onclick="quickSearch(\'Action\')">Action</button>'
                '<button class="tag" onclick="quickSearch(\'Comedy\')">Comedy</button>'
                '<button class="tag" onclick="quickSearch(\'Thriller\')">Thriller</button>'
                '<button class="tag" onclick="quickSearch(\'Anime\')">Anime</button>'
                '<button class="tag" onclick="quickSearch(\'4K\')">4K UHD</button>'
                '<button class="tag" onclick="quickSearch(\'Sci-Fi\')">Sci-Fi</button>'
            '</div>'
        '</div>'
        '<div class="toolbar">'
            '<div class="search-wrap">'
                + ICON_SEARCH +
                '<input class="search-input" id="q" type="text" placeholder="Search movies, series, actors\u2026" autocomplete="off" spellcheck="false">'
                '<span class="kbd-hint"><kbd>/</kbd> to focus</span>'
            '</div>'
            '<button class="search-btn" id="searchBtn" onclick="doSearch(0);triggerRipple(this)">'
                + ICON_SEARCH_BTN + 'Search'
            '</button>'
        '</div>'
        '<div class="filters">'
            '<div class="cdd-wrap" id="cddColWrap">'
                '<button type="button" class="cdd-btn" id="cddColBtn" onclick="toggleCdd(\'col\',event)">'
                    + ICON_FOLDER +
                    '<span id="cddColLabel">All Collections</span>'
                '</button>'
                '<span class="cdd-arrow">&#9660;</span>'
                '<div class="cdd-menu" id="cddColMenu" style="display:none">'
                    '<div class="cdd-item selected" data-val="all" onclick="pickCol(\'all\',\'All Collections\',this,event)">All Collections<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                    '<div class="cdd-item" data-val="primary" onclick="pickCol(\'primary\',\'Primary\',this,event)">Primary<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                    '<div class="cdd-item" data-val="cloud" onclick="pickCol(\'cloud\',\'Cloud\',this,event)">Cloud<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                    '<div class="cdd-item" data-val="archive" onclick="pickCol(\'archive\',\'Archive\',this,event)">Archive<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                '</div>'
            '</div>'
            '<div class="cdd-wrap" id="cddModeWrap">'
                '<button type="button" class="cdd-btn" id="cddModeBtn" onclick="toggleCdd(\'mode\',event)">'
                    + ICON_IMAGE +
                    '<span id="cddModeLabel">Poster view</span>'
                '</button>'
                '<span class="cdd-arrow">&#9660;</span>'
                '<div class="cdd-menu" id="cddModeMenu" style="display:none">'
                    '<div class="cdd-item selected" data-val="tg" onclick="pickMode(\'tg\',\'Poster view\',this,event)">Poster view<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                    '<div class="cdd-item" data-val="none" onclick="pickMode(\'none\',\'Text only (fastest)\',this,event)">Text only (fastest)<span class="cdd-radio"><span class="cdd-radio-dot"></span></span></div>'
                '</div>'
            '</div>'
            '<div class="results-info" id="resInfo"><span class="results-count" id="resCount"></span></div>'
        '</div>'
        '<section class="rail" id="trending" aria-label="Trending titles"></section>'
        '<div class="main" style="padding:0 0 10px;">'
            '<div id="results" class="res-grid">'
                '<div class="empty">'
                    '<div class="empty-icon">&#128269;</div>'
                    '<p><b>Start your search.</b><br>Type a title above, or tap a quick chip to explore.</p>'
                '</div>'
            '</div>'
            '<div class="pagination" id="pageBox" style="display:none;">'
                '<button class="pg-btn" id="pBtn" onclick="prev()" disabled>Previous</button>'
                '<span class="pg-info" id="pgInfo">Page 1</span>'
                '<button class="pg-btn" id="nBtn" onclick="next()">Next</button>'
            '</div>'
        '</div>'
    '</div>'
    '<div class="toast" id="toast"></div>'
)

# ✅ OPTIMIZATION 1: Pre-compile the entire body string ONCE when the app starts.
DASHBOARD_BODY = CARD_CSS + SEARCH_ZONE + f"<script>{JS_ENGINE}</script>"


@dashboard_routes.get('/dashboard')
async def dash(req):
    role, tg_id = await get_auth(req)
    if not role:
        return web.HTTPFound('/login')
    if not await require_active_plan(role, tg_id):
        return web.HTTPFound('/premium_expired')

    return build_page("Home - Fast Finder", DASHBOARD_BODY, "", "dash", role)


@dashboard_routes.get('/logout')
async def logout(req):
    s_user = req.cookies.get('user_session')
    if s_user and hasattr(temp, 'USER_SESSIONS') and s_user in temp.USER_SESSIONS:
        del temp.USER_SESSIONS[s_user]
    res = web.HTTPFound('/login')
    res.del_cookie('user_session')
    return res


@dashboard_routes.get('/premium_expired')
async def premium_expired(req):
    role, tg_id = await get_auth(req)
    if not role:
        return web.HTTPFound('/login')
    content = (
        '<div style="text-align:center;">'
        '<div style="font-size:50px;margin-bottom:15px;">&#9203;</div>'
        '<p style="color:var(--muted);margin-bottom:30px;">Your access to Fast Finder Web has expired. '
        'Please renew your plan via our Telegram Bot.</p>'
        '<div class="scard red" style="text-align:left;margin-bottom:25px;padding:15px;">'
        '<div class="scard-label">How to Renew?</div>'
        '<div class="scard-sub" style="color:var(--text)">1. Go to Telegram Bot</div>'
        '<div class="scard-sub" style="color:var(--text)">2. Use command <b>/plan</b></div>'
        '<div class="scard-sub" style="color:var(--text)">3. Pay & Activate instantly</div>'
        '</div>'
        f'<a href="https://t.me/{temp.U_NAME}" class="submit-btn" style="text-decoration:none;display:block;">Open Telegram Bot</a>'
        '<a href="/logout" style="display:block;margin-top:20px;color:var(--muted);text-decoration:none;">Sign Out</a>'
        '</div>'
    )
    return build_page("Premium Expired", form_wrapper("Premium Expired", content), "login-bg")


# ✅ OPTIMIZATION 2: Koyeb Health Check Route
@dashboard_routes.get('/health')
async def koyeb_health_check(req):
    return web.json_response({"status": "alive", "platform": "koyeb"})
