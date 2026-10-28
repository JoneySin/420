# Fast Finder — Web UI demo

A clickable preview of the redesigned web UI. It runs the **real** route modules
from `web/` (dashboard, posts, actors, stats, profile, login, landing) against
in-memory sample data, so you can browse every screen without Telegram, MongoDB
or the bot process.

```
pip install aiohttp orjson
python demo/demo_app.py          # → http://localhost:8080
```

Quick starts:

| URL | What it shows |
| --- | --- |
| `/demo` | **Start here** — a gallery linking every screen |
| `/` | Public landing page (search → Telegram deep link) |
| `/login` | Sign-in screen (any email/password works) |
| `/demo/login?role=admin` | One-click admin session → dashboard |
| `/demo/login?role=user` | One-click member session (no stats access) |
| `/dashboard` | Library search: hero, quick chips, poster grid, filters |
| `/posts` | Curated posts catalog |
| `/actors` | Directory of actors / apps / websites |
| `/actor/<id>` | Profile with tabs, gallery and linked media |
| `/stats` | Admin analytics dashboard |
| `/profile` | Account settings |
| `/watch/<id>` | Player page (simulated playback) |

A small floating **Demo** pill is injected into every page so you can switch
between the admin and member views at any time.

## What the demo fakes

Everything here lives only in `demo/` and is never imported by `bot.py`:

* `mocks.py` — installs stand-ins for `info`, `utils.temp`, `database.*`, `bson`
  and `web.utils.custom_dl` **before** anything from `web/` is imported.
  It also ships the sample media library, actor profiles, posts and counters,
  plus a `MockBot` that serves poster bytes for thumbnail endpoints.
* `demo_app.py` — assembles an `aiohttp` app out of the real route tables
  (skipping only the Telegram-dependent handlers, which it replaces with
  sample-data versions), serves `demo/static/`, and adds the demo bar.
* `static/posters/*.jpg` — AI-generated sample key-art used as thumbnails.

## Notes

* Sample art is generated imagery; titles, captions and numbers are fictional.
* The player page simulates playback — real streaming is served by
  `web/stream_routes.py` from Telegram.
* Delete this folder and nothing in production changes.
