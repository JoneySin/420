"""
Demo mocks — lets the real Fast Finder web UI run without Telegram or MongoDB.

`install()` injects lightweight stand-ins for the heavy runtime modules
(info, utils, database.*, bson, web.utils.custom_dl) into sys.modules,
so `web/*.py` can be imported and rendered completely untouched.

Everything here is fake sample data for showcasing the interface.
"""
from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import time
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
POSTER_DIR = HERE / "static" / "posters"
POSTER_FILES = sorted(POSTER_DIR.glob("*.jpg"))
POSTER_BYTES = {p.stem: p.read_bytes() for p in POSTER_FILES}

ADMIN_ID = 1
MEMBER_ID = 424242
NOW = int(time.time())


# ─────────────────────────────────────────────────────────────
# tiny in-memory "motor" collection
# ─────────────────────────────────────────────────────────────
def _get(doc, dotted):
    cur = doc
    for part in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _match(doc, query):
    if not query:
        return True
    for key, val in query.items():
        if key == "$or":
            if not any(_match(doc, sub) for sub in val):
                return False
        elif isinstance(val, dict):
            if "$regex" in val:
                if not re.search(str(val["$regex"]), str(_get(doc, key) or ""), re.I):
                    return False
            elif "$ne" in val:
                if _get(doc, key) == val["$ne"]:
                    return False
            elif "$in" in val:
                if _get(doc, key) not in val["$in"]:
                    return False
        elif str(_get(doc, key)) != str(val):
            return False
    return True


class Cursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, *args, **kwargs):
        return self

    def skip(self, n):
        self._docs = self._docs[n:]
        return self

    def limit(self, n):
        self._docs = self._docs[:n]
        return self

    async def to_list(self, length=None):
        return list(self._docs[:length]) if length else list(self._docs)

    def __aiter__(self):
        self._iter = iter(self._docs)
        return self

    async def __anext__(self):
        try:
            return next(self._iter)
        except StopIteration:
            raise StopAsyncIteration


class WriteResult:
    modified_count = 1
    matched_count = 1
    upserted_id = None


class MockCollection:
    def __init__(self, docs=None, count=None):
        self.docs = list(docs or [])
        self._count = count

    def find(self, query=None, projection=None):
        return Cursor([d for d in self.docs if _match(d, query)])

    async def find_one(self, query=None, projection=None):
        for d in self.docs:
            if _match(d, query):
                return d
        return None

    async def count_documents(self, query=None):
        if self._count is not None:
            return self._count
        return len([d for d in self.docs if _match(d, query)])

    async def insert_one(self, doc):
        self.docs.append(doc)
        return WriteResult()

    async def update_one(self, query, update, upsert=False):
        target = None
        for d in self.docs:
            if _match(d, query):
                target = d
                break
        if target is None:
            if not upsert:
                return WriteResult()
            target = {}
            self.docs.append(target)
        for op, payload in update.items():
            if op == "$set":
                target.update(payload)
            elif op == "$inc":
                for k, v in payload.items():
                    target[k] = (target.get(k) or 0) + v
        return WriteResult()

    async def delete_one(self, query):
        for i, d in enumerate(self.docs):
            if _match(d, query):
                del self.docs[i]
                break
        return WriteResult()

    async def delete_many(self, query):
        self.docs = [d for d in self.docs if not _match(d, query)]
        return WriteResult()

    def aggregate(self, pipeline):
        """Supports the single $group-by-category pipeline the stats page uses."""
        groups = {}
        for d in self.docs:
            key = d.get("category", "Uncategorized")
            groups[key] = groups.get(key, 0) + 1
        return Cursor([{"_id": k, "count": v} for k, v in groups.items()])


# ─────────────────────────────────────────────────────────────
# sample media library
# ─────────────────────────────────────────────────────────────
def _media(idx, title, size, kind, col, caption, poster):
    return {
        "_id": f"demo{idx:04d}",
        "file_ref": f"demo_ref_{idx}",
        "file_name": title,
        "file_size": size,
        "file_type": kind,
        "source_col": col,
        "thumb_url": f"TG_ID:{poster}",
        "caption": caption,
        "created_at": NOW - idx * 3600,
    }


MEDIA = [
    _media(1, "Interstellar (2014) 2160p HDR BluRay x265", 9_126_293_504, "video", "primary",
           "Interstellar 2014 4K UHD | Sci-Fi | Matthew McConaughey | Christopher Nolan", "p1"),
    _media(2, "Neon Rain (2024) 1080p WEB-DL Dual Audio", 2_415_919_104, "video", "cloud",
           "Neon Rain 2024 cyberpunk thriller | Hindi + English | 1080p", "p2"),
    _media(3, "Dune: Part Two (2024) 2160p DV HDR", 15_032_385_536, "video", "primary",
           "Dune Part Two 2024 4K Dolby Vision | Sci-Fi | Timothee Chalamet | Zendaya", "p3"),
    _media(4, "The Quiet Pines S01E04 720p HDTV", 612_368_384, "video", "archive",
           "The Quiet Pines Season 1 Episode 4 | Mystery | 720p HDTV", "p4"),
    _media(5, "Skyward (2023) 1080p BluRay Anime Film", 3_221_225_472, "video", "primary",
           "Skyward 2023 anime movie | Makoto style | 1080p BluRay | Dubbed", "p5"),
    _media(6, "Monsoon Nights (2025) 1080p WEB-DL", 1_932_735_283, "video", "cloud",
           "Monsoon Nights 2025 Bollywood drama | Hindi | 1080p | Romance", "p6"),
    _media(7, "Rooftop Protocol (2024) 1080p HDRip", 2_147_483_648, "video", "primary",
           "Rooftop Protocol 2024 action thriller | 1080p | Hindi Dubbed", "p7"),
    _media(8, "Last Train Home (2022) 720p WEB-DL", 987_842_560, "video", "archive",
           "Last Train Home 2022 romantic drama | 720p | Classic", "p8"),
    _media(9, "Interstellar (2014) Official Soundtrack FLAC", 486_539_264, "audio", "cloud",
           "Interstellar OST | Hans Zimmer | FLAC lossless | 24-bit", "p1"),
    _media(10, "Neon Rain (2024) Behind The Scenes 4K", 764_411_904, "video", "archive",
           "Neon Rain BTS featurette | 4K | Making of cyberpunk", "p2"),
    _media(11, "Dune: Part Two (2024) Subtitles Pack", 1_048_576, "document", "primary",
           "Dune Part Two subtitles | English, Hindi, Tamil | SRT pack", "p3"),
    _media(12, "Skyward (2023) Art Book PDF", 88_080_384, "document", "cloud",
           "Skyward art book | 120 pages | PDF | Concept art", "p5"),
    _media(13, "Monsoon Nights (2025) 4K HDR Trailer", 314_572_800, "video", "primary",
           "Monsoon Nights trailer 4K HDR | Bollywood 2025", "p6"),
    _media(14, "Rooftop Protocol S02E01 1080p", 1_073_741_824, "video", "cloud",
           "Rooftop Protocol Season 2 Episode 1 | action series | 1080p", "p7"),
    _media(15, "The Quiet Pines S01 Complete 720p", 4_294_967_296, "video", "primary",
           "The Quiet Pines full season 1 | 8 episodes | 720p | Mystery", "p4"),
    _media(16, "Last Train Home (2022) Commentary Track", 120_586_240, "audio", "archive",
           "Last Train Home director commentary | MP3 320kbps", "p8"),
    _media(17, "Dune: Part Two (2024) IMAX Poster Pack", 25_165_824, "image", "archive",
           "Dune Part Two posters | IMAX art | 8 images | PNG", "p3"),
    _media(18, "Skyward (2023) 720p Dubbed", 1_342_177_280, "video", "archive",
           "Skyward 2023 anime 720p Hindi dubbed", "p5"),
]

ACTOR_DOCS = [
    {"_id": "a0000000000000000000001", "name": "Aarav Mehta", "category": "actor",
     "bio": "Lead actor known for intense dramatic roles across Hindi cinema.\nRecent: Monsoon Nights, Rooftop Protocol.",
     "photo_url": "TG_ID:p6", "gallery": ["TG_ID:p6", "TG_ID:p7", "TG_ID:p8"],
     "tags": ["Bollywood", "Drama"], "created_at": NOW - 86400, "photo_updated_at": NOW - 86400,
     "social_links": {"instagram": "https://instagram.com", "youtube": "", "twitter": ""}},
    {"_id": "a0000000000000000000002", "name": "Isha Kapoor", "category": "actor",
     "bio": "Award-winning performer with a decade of work in independent cinema.",
     "photo_url": "TG_ID:p8", "gallery": ["TG_ID:p8", "TG_ID:p5"],
     "tags": ["Indie", "Romance"], "created_at": NOW - 90000, "photo_updated_at": NOW - 90000,
     "social_links": {"instagram": "", "youtube": "https://youtube.com", "twitter": ""}},
    {"_id": "a0000000000000000000003", "name": "Kabir Rao", "category": "actor",
     "bio": "Action specialist and stunt coordinator turned leading man.",
     "photo_url": "TG_ID:p7", "gallery": ["TG_ID:p7"],
     "tags": ["Action", "Thriller"], "created_at": NOW - 100000, "photo_updated_at": NOW - 100000,
     "social_links": {"instagram": "", "youtube": "", "twitter": "https://x.com"}},
    {"_id": "a0000000000000000000004", "name": "Meera Nair", "category": "actor",
     "bio": "Anime voice artist and dubbing director for South Asian releases.",
     "photo_url": "TG_ID:p5", "gallery": ["TG_ID:p5", "TG_ID:p1"],
     "tags": ["Anime", "Voice"], "created_at": NOW - 110000, "photo_updated_at": NOW - 110000,
     "social_links": {"instagram": "", "youtube": "", "twitter": ""}},
    {"_id": "a0000000000000000000005", "name": "Dev Anand Jr.", "category": "actor",
     "bio": "Classic-era inspired performer, frequent collaborator with indie studios.",
     "photo_url": "TG_ID:p3", "gallery": ["TG_ID:p3"],
     "tags": ["Classic"], "created_at": NOW - 120000, "photo_updated_at": NOW - 120000,
     "social_links": {"instagram": "", "youtube": "", "twitter": ""}},
    {"_id": "a0000000000000000000006", "name": "Streamly App", "category": "app",
     "bio": "Modded streaming app with offline downloads and subtitle sync.",
     "photo_url": "TG_ID:p4", "gallery": [], "tags": ["Android"],
     "created_at": NOW - 130000, "photo_updated_at": NOW - 130000, "social_links": {}},
    {"_id": "a0000000000000000000007", "name": "MovieIndex", "category": "website",
     "bio": "Curated database of releases, cast and crew with fast search.",
     "photo_url": "TG_ID:p2", "gallery": [], "tags": ["Database"],
     "created_at": NOW - 140000, "photo_updated_at": NOW - 140000, "social_links": {}},
    {"_id": "a0000000000000000000008", "name": "Tara Iyer", "category": "actor",
     "bio": "Breakout talent from the 2024 festival circuit.",
     "photo_url": "TG_ID:p6", "gallery": ["TG_ID:p6"],
     "tags": ["Festival"], "created_at": NOW - 150000, "photo_updated_at": NOW - 150000,
     "social_links": {"instagram": "", "youtube": "", "twitter": ""}},
]

POST_DOCS = [
    {"_id": "b0000000000000000000001", "title": "Dune: Part Two", "category": "Movies",
     "cover_image": "TG_ID:p3", "tags": ["Sci-Fi", "4K", "2024"],
     "description": "Paul Atreides unites with the Fremen while on a warpath of revenge against the conspirators who destroyed his family.",
     "videos": [], "screenshots": ["TG_ID:p3", "TG_ID:p1"], "created_at": NOW - 3600},
    {"_id": "b0000000000000000000002", "title": "Monsoon Nights", "category": "Movies",
     "cover_image": "TG_ID:p6", "tags": ["Drama", "Hindi", "2025"],
     "description": "A rainswept drama about a young man returning to the city that raised him.",
     "videos": [], "screenshots": ["TG_ID:p6"], "created_at": NOW - 7200},
    {"_id": "b0000000000000000000003", "title": "The Quiet Pines", "category": "Web Series",
     "cover_image": "TG_ID:p4", "tags": ["Mystery", "Series"],
     "description": "A small-town mystery unfolds across eight tense episodes.",
     "videos": [], "screenshots": ["TG_ID:p4"], "created_at": NOW - 10800},
    {"_id": "b0000000000000000000004", "title": "Rooftop Protocol", "category": "Web Series",
     "cover_image": "TG_ID:p7", "tags": ["Action"],
     "description": "An elite response unit works above the skyline of a restless city.",
     "videos": [], "screenshots": ["TG_ID:p7"], "created_at": NOW - 14400},
    {"_id": "b0000000000000000000005", "title": "Skyward", "category": "Movies",
     "cover_image": "TG_ID:p5", "tags": ["Anime", "2023"],
     "description": "A painterly coming-of-age story that takes to the clouds.",
     "videos": [], "screenshots": ["TG_ID:p5"], "created_at": NOW - 18000},
    {"_id": "b0000000000000000000006", "title": "Neon Rain", "category": "Movies",
     "cover_image": "TG_ID:p2", "tags": ["Cyberpunk", "Thriller"],
     "description": "A courier uncovers a conspiracy buried under the neon of a drowned city.",
     "videos": [], "screenshots": ["TG_ID:p2"], "created_at": NOW - 21600},
]


# ─────────────────────────────────────────────────────────────
# database stand-ins
# ─────────────────────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()


class WebAuthDB:
    def __init__(self):
        self.col = MockCollection([
            {"tg_id": ADMIN_ID, "email": "admin@fastfinder.dev", "password": hash_password("demo1234"),
             "last_login": "2026-10-28 09:12:00"},
            {"tg_id": MEMBER_ID, "email": "member@fastfinder.dev", "password": hash_password("demo1234"),
             "last_login": "2026-10-27 21:40:00"},
        ])

    async def verify_login(self, email, password):
        email = (email or "").strip().lower()
        if email.startswith("admin"):
            return {"tg_id": ADMIN_ID, "email": email}
        return {"tg_id": MEMBER_ID, "email": email or "member@fastfinder.dev"}

    async def create_user(self, tg_id, email, password):
        await self.col.insert_one({"tg_id": tg_id, "email": email, "password": hash_password(password)})
        return True, "ok"

    async def generate_otp(self, tg_id):
        return "123456"

    async def verify_otp_and_reset(self, tg_id, otp, new_password):
        return True

    async def update_profile(self, tg_id, new_email, new_password=None):
        data = {"email": new_email}
        if new_password:
            data["password"] = hash_password(new_password)
        await self.col.update_one({"tg_id": tg_id}, {"$set": data})


class _ClientMap:
    """Mimics `motor_client.db["CollectionName"]` access."""
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            if name == "Posts":
                self._collections[name] = MockCollection(POST_DOCS)
            else:
                self._collections[name] = MockCollection()
        return self._collections[name]

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)
        return self[name]


class UserDB:
    def __init__(self):
        self.db = _ClientMap()
        self.users = MockCollection(count=12_847)
        self.premium = MockCollection(count=412)
        self.settings = MockCollection([{"id": "global_stream_stats", "total_web_plays": 86_204}])
        self.delete_queue = MockCollection()

    async def total_users_count(self):
        return 12_847

    async def get_premium_users_count(self):
        return 412

    async def get_today_logged_in_users_count(self):
        return 268

    async def get_plan(self, uid):
        return {"premium": True, "expire": "2027-04-18"}

    async def add_to_delete_queue(self, chat_id, message_id, delay_seconds=0):
        return True

    async def track_video_play(self):
        doc = await self.settings.find_one({"id": "global_stream_stats"})
        if doc:
            doc["total_web_plays"] = doc.get("total_web_plays", 0) + 1
        return True


class FilterDB:
    async def add_to_delete_queue(self, *args, **kwargs):
        return True

    async def command(self, name, *args, **kwargs):
        # pretend a mid-sized Atlas cluster
        return {"storageSize": 289_406_976, "indexSize": 41_943_040, "objects": 8_818}

    async def track_video_play(self):
        return True


# ─────────────────────────────────────────────────────────────
# fake bot (thumbnail fetch)
# ─────────────────────────────────────────────────────────────
class MockBot:
    async def download_media(self, file_id, in_memory=False):
        key = str(file_id).replace("TG_ID:", "")
        data = POSTER_BYTES.get(key)
        if data is None:
            return None
        return io.BytesIO(data)

    async def send_message(self, *args, **kwargs):
        return True

    async def get_messages(self, *args, **kwargs):
        return None


class _Temp:
    START_TIME = time.time()
    BOT = MockBot()
    U_NAME = "FastFinderDemoBot"
    B_NAME = "Fast Finder"
    USER_SESSIONS = {}
    REG_PENDING = {}


def install():
    """Register stub modules before any `web.*` import happens."""
    if getattr(sys, "fastfinder_demo_installed", False):
        return
    sys.fastfinder_demo_installed = True

    # ---- info ----
    info = types.ModuleType("info")
    defaults = {
        "PORT": int(os.environ.get("PORT", 8080)),
        "BIN_CHANNEL": -1001234567890,
        "URL": "http://localhost:8080",
        "ADMINS": [ADMIN_ID],
        "MAX_WEB_RESULTS": 21,
        "ACTOR_STORAGE_CHANNEL": -1001234567890,
        "THUMBNAIL_STORAGE_CHANNEL": -1001234567890,
        "BOT_TOKEN": "000000:DEMO-TOKEN",
        "IS_PREMIUM": True,
        "USE_CAPTION_FILTER": True,
        "MAX_THUMB_CACHE": 500,
        "TIME_ZONE": "Asia/Kolkata",
    }
    for k, v in defaults.items():
        setattr(info, k, v)
    info.__getattr__ = lambda name: None
    sys.modules["info"] = info

    # ---- utils ----
    utils = types.ModuleType("utils")
    utils.temp = _Temp()

    def get_size(size):
        if not size:
            return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        n = float(size)
        for unit in units:
            if n < 1024 or unit == units[-1]:
                return f"{n:.2f} {unit}" if unit != "B" else f"{int(n)} B"
            n /= 1024
        return f"{n:.2f} TB"

    async def is_premium(uid):
        return True

    utils.get_size = get_size
    utils.is_premium = is_premium
    utils.is_rate_limited = lambda *a, **k: False
    sys.modules["utils"] = utils

    # ---- database package ----
    db_pkg = types.ModuleType("database")
    db_pkg.__path__ = []
    sys.modules["database"] = db_pkg

    users_mod = types.ModuleType("database.users_chats_db")
    users_mod.db = UserDB()
    users_mod.web_db = WebAuthDB()
    users_mod.hash_password = hash_password
    users_mod.get_local_now = lambda: "2026-10-28 09:12:00"
    sys.modules["database.users_chats_db"] = users_mod
    db_pkg.users_chats_db = users_mod

    filter_mod = types.ModuleType("database.ia_filterdb")
    filter_mod.db = FilterDB()
    filter_mod.actors = MockCollection(ACTOR_DOCS)
    filter_mod.COLLECTIONS = {"primary": MockCollection(count=4820),
                              "cloud": MockCollection(count=2311),
                              "archive": MockCollection(count=1687)}

    async def get_search_results(*args, **kwargs):
        return [], "", None, None

    async def db_count_documents():
        return {"total": 8818, "primary": 4820, "cloud": 2311, "archive": 1687,
                "primary_thumb": 4610, "cloud_thumb": 2188, "archive_thumb": 1502,
                "total_thumb": 8300}

    async def get_actor_search_results(*args, **kwargs):
        return [], ""

    async def delete_single_file(*args, **kwargs):
        return True

    async def delete_actor_profile(*args, **kwargs):
        return True

    async def delete_gallery_image_by_index(*args, **kwargs):
        return True

    filter_mod.get_search_results = get_search_results
    filter_mod.db_count_documents = db_count_documents
    filter_mod.get_actor_search_results = get_actor_search_results
    filter_mod.delete_single_file = delete_single_file
    filter_mod.delete_actor_profile = delete_actor_profile
    filter_mod.delete_gallery_image_by_index = delete_gallery_image_by_index
    sys.modules["database.ia_filterdb"] = filter_mod
    db_pkg.ia_filterdb = filter_mod

    # ---- lru ----
    lru_mod = types.ModuleType("lru")

    class LRU(dict):
        def __init__(self, size=100, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.size = size

        def __setitem__(self, key, value):
            if len(self) >= self.size and key not in self:
                try:
                    del self[next(iter(self))]
                except StopIteration:
                    pass
            super().__setitem__(key, value)

    lru_mod.LRU = LRU
    sys.modules["lru"] = lru_mod

    # ---- bson ----
    bson = types.ModuleType("bson")
    bson_pkg = types.ModuleType("bson.objectid")

    class ObjectId(str):
        """Twenty-four char id stand-in (a plain str subclass)."""
        def __new__(cls, value=None):
            return super().__new__(cls, str(value if value is not None else "0" * 24))

        @property
        def binary(self):
            return str.encode(self)

    bson_pkg.ObjectId = ObjectId
    bson.objectid = bson_pkg
    sys.modules["bson"] = bson
    sys.modules["bson.objectid"] = bson_pkg

    # ---- web.utils.custom_dl (Telegram streaming internals) ----
    dl = types.ModuleType("web.utils.custom_dl")
    dl.TGCustomYield = object
    dl.chunk_size = 1024 * 1024
    dl.offset_fix = lambda offset, chunk: offset - (offset % chunk)
    sys.modules["web.utils.custom_dl"] = dl
