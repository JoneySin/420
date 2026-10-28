import uuid
import random
import time
from aiohttp import web
from web.web_assets import build_page, form_wrapper
from utils import temp
from database.users_chats_db import web_db, get_local_now  # <-- समय सिंक के लिए इम्पोर्ट किया

login_routes = web.RouteTableDef()

@login_routes.get('/login')
async def login_user(req):
    content = (
        '<form action="/api/login" method="post">'
        '<label class="field-label">Email address</label><input type="email" name="email" placeholder="you@example.com" required autocomplete="email">'
        '<label class="field-label">Password</label><input type="password" name="password" placeholder="Enter your password" required autocomplete="current-password">'
        '<button class="submit-btn" type="submit">Sign in to Fast Finder</button></form>'
        '<div class="login-foot"><a href="/forgot_password">Forgot password?</a>'
        '<a href="/register" class="strong">Create an account &rarr;</a></div>'
    )
    return build_page("Sign In", form_wrapper("Welcome back", content, req.query.get('err',''), req.query.get('msg',''),
                        "Sign in to search, stream and manage your media library."), "login-bg")

@login_routes.post('/api/login')
async def api_login_user(req):
    d = await req.post()
    user = await web_db.verify_login(d.get('email'), d.get('password'))
    if user:
        # ✅ LOGIN TRACK ENGINE: डेटाबेस में यूजर का अंतिम लॉगिन टाइमस्टैम्प अभी का सेट करें
        await web_db.col.update_one(
            {"tg_id": user['tg_id']},
            {"$set": {"last_login": get_local_now()}}
        )

        s = str(uuid.uuid4())
        if not hasattr(temp, 'USER_SESSIONS'): temp.USER_SESSIONS = {}
        temp.USER_SESSIONS[s] = {'tg_id': user['tg_id'], 'expiry': time.time() + 86400 * 7}
        res = web.HTTPFound('/dashboard')
        res.set_cookie('user_session', s, max_age=86400 * 7)
        return res
    return web.HTTPFound('/login?err=Invalid Email or Password')

@login_routes.get('/register')
async def register_user(req):
    content = (
        '<form action="/api/register_step1" method="post">'
        '<label class="field-label">Telegram ID</label><input type="number" name="tg_id" placeholder="e.g. 123456789" required inputmode="numeric">'
        '<label class="field-label">Email address</label><input type="email" name="email" placeholder="you@example.com" required autocomplete="email">'
        '<label class="field-label">Password</label><input type="password" name="password" placeholder="Create a strong password" required autocomplete="new-password">'
        '<button class="submit-btn" type="submit">Send OTP via Telegram</button></form>'
        '<p class="login-foot" style="justify-content:center;color:var(--muted);">Already have an account? '
        '<a href="/login" class="strong">Sign in</a></p>'
    )
    return build_page("Create Account", form_wrapper("Create your account", content, req.query.get('err',''), "",
                        "Link your Telegram ID once and unlock a private web dashboard."), "login-bg")

@login_routes.post('/api/register_step1')
async def api_register_step1(req):
    d = await req.post()
    try: tg_id = int(d.get('tg_id'))
    except: return web.HTTPFound('/register?err=Invalid Telegram ID')
    email, password = d.get('email'), d.get('password')
    
    if await web_db.col.find_one({"$or": [{"tg_id": tg_id}, {"email": email}]}, {"_id": 1}): 
        return web.HTTPFound('/register?err=Telegram ID or Email already registered!')
        
    otp = str(random.randint(100000, 999999))
    now = time.time()
    if not hasattr(temp, 'REG_PENDING'): temp.REG_PENDING = {}
    temp.REG_PENDING[tg_id] = {'email': email, 'password': password, 'otp': otp, 'expiry': now + 300}
    try: 
        await temp.BOT.send_message(tg_id, f"🔐 **Web Registration Verification**\n\nSomeone is trying to link your Telegram ID to this email: `{email}`\n\n**Your OTP is:** `{otp}`\n\n_Valid for 5 mins._")
    except Exception: 
        return web.HTTPFound('/register?err=Failed to send OTP. Please start the Bot first in Telegram PM.')
    return web.HTTPFound(f'/verify_registration?tg_id={tg_id}')

@login_routes.get('/verify_registration')
async def verify_registration_page(req):
    tg_id = req.query.get('tg_id', '')
    if not tg_id: return web.HTTPFound('/register')
    content = (
        '<form action="/api/register_step2" method="post">'
        f'<input type="hidden" name="tg_id" value="{tg_id}">'
        '<label class="field-label">One-time password</label><input type="text" name="otp" placeholder="------" required inputmode="numeric" maxlength="6" '
        'style="letter-spacing:.5em;font-size:19px;text-align:center;font-weight:700;">'
        '<button class="submit-btn" type="submit">Verify &amp; create account</button></form>'
    )
    return build_page("Verify Registration", form_wrapper("Verify your OTP", content, req.query.get('err',''), "",
                        "Open Telegram, find our bot and copy the 6-digit code."), "login-bg")

@login_routes.post('/api/register_step2')
async def api_register_step2(req):
    d = await req.post()
    try: tg_id = int(d.get('tg_id'))
    except: return web.HTTPFound('/register?err=Invalid Request')
    otp = d.get('otp')
    if tg_id not in getattr(temp, 'REG_PENDING', {}): return web.HTTPFound('/register?err=Session expired. Try again.')
    pending = temp.REG_PENDING[tg_id]
    if time.time() > pending['expiry']:
        del temp.REG_PENDING[tg_id]
        return web.HTTPFound('/register?err=OTP Expired. Please restart registration.')
    if pending['otp'] != otp: return web.HTTPFound(f'/verify_registration?tg_id={tg_id}&err=Invalid OTP')
    success, msg = await web_db.create_user(tg_id, pending['email'], pending['password'])
    del temp.REG_PENDING[tg_id]
    if success:
        return web.HTTPFound('/login?msg=Account created successfully! Please login.')
    return web.HTTPFound(f'/register?err={msg}')

@login_routes.get('/forgot_password')
async def forgot_password(req):
    content = (
        '<form action="/api/forgot_password" method="post">'
        '<label class="field-label">Telegram ID</label><input type="number" name="tg_id" placeholder="e.g. 123456789" required inputmode="numeric">'
        '<button class="submit-btn" type="submit">Send OTP to Telegram</button></form>'
        '<hr style="border:0;border-top:1px solid var(--border);margin:24px 0;">'
        '<form action="/api/reset_password" method="post">'
        '<label class="field-label">Confirm Telegram ID</label><input type="number" name="tg_id" placeholder="e.g. 123456789" required inputmode="numeric">'
        '<label class="field-label">OTP from Telegram</label><input type="text" name="otp" placeholder="Enter 6-digit OTP" required inputmode="numeric">'
        '<label class="field-label">New password</label><input type="password" name="new_password" placeholder="Choose a new password" required autocomplete="new-password">'
        '<button class="submit-btn" type="submit">Update password</button></form>'
    )
    return build_page("Reset Password", form_wrapper("Reset your password", content, req.query.get('err',''), req.query.get('msg',''),
                        "Every reset is verified through your linked Telegram account."), "login-bg")

@login_routes.post('/api/forgot_password')
async def api_forgot_password(req):
    try: tg_id = int((await req.post()).get('tg_id'))
    except: return web.HTTPFound('/forgot_password?err=Invalid Telegram ID')
    otp = await web_db.generate_otp(tg_id)
    if otp:
        try:
            await temp.BOT.send_message(tg_id, f"🔐 **Fast Finder Password Reset**\n\nYour Password Reset OTP is: `{otp}`\n\nValid for 10 minutes. Do not share!")
            return web.HTTPFound('/forgot_password?msg=OTP sent to your Telegram!')
        except: return web.HTTPFound('/forgot_password?err=Error sending OTP. Have you started the bot?')
    return web.HTTPFound('/forgot_password?err=Telegram ID not registered!')

@login_routes.post('/api/reset_password')
async def api_reset_password(req):
    d = await req.post()
    try: tg_id = int(d.get('tg_id'))
    except: return web.HTTPFound('/forgot_password?err=Invalid Input')
    if await web_db.verify_otp_and_reset(tg_id, d.get('otp'), d.get('new_password')): return web.HTTPFound('/login?msg=Password updated successfully! Please login.')
    return web.HTTPFound('/forgot_password?err=Invalid or Expired OTP.')
