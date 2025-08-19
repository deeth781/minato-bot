import os, sys, time, json, socket, platform, getpass
import discord
from discord.ext import commands
from colorama import Fore, Style, init
from pystyle import Colors, Colorate, Center
import threading
import discord
from discord.ext import commands, tasks
from discord import Interaction
from discord import app_commands

async def safe_send(interaction: discord.Interaction, message: str, ephemeral=False):
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=ephemeral)
        else:
            await interaction.followup.send(message, ephemeral=ephemeral)
    except discord.NotFound:
        print("[WARN] Interaction expired")

from discord import app_commands
import threading
import requests
import re
import time
import json
import os
import gc
import random
import base64
import multiprocessing

import itertools, sys, time, aiohttp, asyncio
from datetime import datetime
from colorama import Fore
from enum import Enum
from Crypto.Cipher import AES
from textwrap import shorten
from datetime import datetime, timedelta
import smtplib, ssl, time, threading, os
from email.mime.text import MIMEText

CONFIG_FILE = "config.json"


BANNER = r"""
  $$\      $$\ $$\                      $$\               
$$$\    $$$ |\__|                     $$ |              
$$$$\  $$$$ |$$\ $$$$$$$\   $$$$$$\ $$$$$$\    $$$$$$\  
$$\$$\$$ $$ |$$ |$$  __$$\  \____$$\\_$$  _|  $$  __$$\ 
$$ \$$$  $$ |$$ |$$ |  $$ | $$$$$$$ | $$ |    $$ /  $$ |
$$ |\$  /$$ |$$ |$$ |  $$ |$$  __$$ | $$ |$$\ $$ |  $$ |
$$ | \_/ $$ |$$ |$$ |  $$ |\$$$$$$$ | \$$$$  |\$$$$$$  |
\__|     \__|\__|\__|  \__| \_______|  \____/  \______/ 
                                                        
                                                        
                                                        
               🗿 Minato Discord Bot Loader 🗿
"""


def fake_type(text, delay=0.03, newline=True):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    if newline:
        print()

def fake_input(prompt):
    fake_type(prompt, delay=0.02)
    return input("» ").strip()


def load_or_create_config():
    if os.path.exists(CONFIG_FILE):
        fake_type("\n📂 Đã tìm thấy config cũ.", 0.04)
        use_old = fake_input("👉 bbi muốn dùng config cũ không? (y/n): ").lower()
        if use_old == "y":
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            fake_type("✅ Đã load config cũ thành công!\n", 0.04)
            return cfg


    fake_type("\n⚙️  Nhập config mới...", 0.04)
    token = fake_input("🔑 Nhập Token Bot: ")
    admins = [x.strip() for x in fake_input("👑 Nhập ID Admin (cách nhau dấu phẩy): ").split(",")]

    cfg = {"TOKEN": token, "ADMINS": admins}
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4)
    fake_type("💾 Đã lưu config mới vào config.json\n", 0.04)
    return cfg


os.system("cls" if os.name == "nt" else "clear")
print(Colorate.Vertical(Colors.green_to_cyan, Center.XCenter(BANNER)))
fake_type("🔥 Dcu Chào Mừng Em Đến Với Anh")

config = load_or_create_config()
TOKEN = config["TOKEN"]
ADMIN_IDS = config["ADMINS"]


INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True


bot = commands.Bot(command_prefix="/", intents=INTENTS)
tree = bot.tree

DATA_FILE = "users.json"

user_tabs = {}
TAB_LOCK = threading.Lock()
user_image_tabs = {}
IMAGE_TAB_LOCK = threading.Lock()
user_nhaymess_tabs = {}
NHAY_LOCK = threading.Lock()
user_discord_tabs = {}
DIS_LOCK = asyncio.Lock()
user_nhaydis_tabs = {}  
NHAYDIS_LOCK = asyncio.Lock()
user_treotele_tabs = {}   
TREOTELE_LOCK = threading.Lock()
SPAM_TASKS = {}  
IG_LOCK = threading.Lock()
user_treogmail_tabs = {}
TREOGMAIL_LOCK = threading.Lock()

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(interaction: discord.Interaction):
    return str(interaction.user.id) in ADMIN_IDS

def is_authorized(interaction: discord.Interaction):
    users = load_users()
    uid = str(interaction.user.id)
    if uid in users:
        exp = users[uid]
        if exp is None:
            return True
        elif datetime.fromisoformat(exp) > datetime.now():
            return True
        else:            
            _remove_user_and_kill_tabs(uid)
    return False

def _add_user(uid: str, days: int = None):
    users = load_users()
    if days:
        expire_time = (datetime.now() + timedelta(days=days)).isoformat()
        users[uid] = expire_time
    else:
        users[uid] = None
    save_users(users)

def _remove_user_and_kill_tabs(uid: str):
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
    with TAB_LOCK:
        if uid in user_tabs:
            for tab in user_tabs[uid]:
                tab["stop_event"].set()
            del user_tabs[uid]

def _get_user_list():
    users = load_users()
    result = []
    for uid, exp in users.items():
        if exp:
            remaining = datetime.fromisoformat(exp) - datetime.now()
            if remaining.total_seconds() <= 0:
                continue  
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            time_str = f"{days} ngày, {hours} giờ, {minutes} phút"
            result.append((uid, time_str))
        else:
            result.append((uid, "vĩnh viễn"))
    return result
            
async def _discord_spam_worker(session, token, channels, message, delay, start_time, discord_user_id):
    while True:
        elapsed = int((datetime.now() - start_time).total_seconds())
        ts = format_time(elapsed)
        for channel_id in channels:
            ok, err = await send_message(session, token, channel_id, message)
            if ok:
                print(Fore.LIGHTGREEN_EX + f"[DIS][{discord_user_id}]  {channel_id} | Token:{token[:20]}... | Delay:{delay}s | Up:{ts}")
            else:
                print(Fore.RED + f"[DIS][{discord_user_id}]  {channel_id}: {err}")
        await asyncio.sleep(delay)
 
def telegram_send_loop(token, chat_ids, caption, photo, delay, stop_event, discord_user_id):
    while not stop_event.is_set():
        for chat_id in chat_ids:
            if stop_event.is_set():
                break
            try:
                if photo:
                    if photo.startswith("http"):
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        data = {"chat_id": chat_id, "caption": caption, "photo": photo}
                        resp = requests.post(url, data=data, timeout=10)
                    else:
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        with open(photo, "rb") as f:
                            files = {"photo": f}
                            data = {"chat_id": chat_id, "caption": caption}
                            resp = requests.post(url, data=data, files=files, timeout=10)
                else:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {"chat_id": chat_id, "text": caption}
                    resp = requests.post(url, data=data, timeout=10)

                if resp.status_code == 200:
                    print(f"[TELE][{discord_user_id}] {token[:10]}... → {chat_id}")
                elif resp.status_code == 429:
                    retry = resp.json().get("parameters", {}).get("retry_after", 10)
                    print(f"[TELE][{discord_user_id}] Rate limit {retry}s")
                    time.sleep(retry)
                else:
                    print(f"[TELE][{discord_user_id}] Err {resp.status_code}: {resp.text[:100]}")
            except Exception as e:
                print(f"[TELE][{discord_user_id}] Conn Err: {e}")
            time.sleep(0.2)
        time.sleep(delay)           

def _ig_spam_loop(task_id, discord_user_id):
    with IG_LOCK:
        task = next((t for t in SPAM_TASKS[discord_user_id] if t["id"] == task_id), None)
    if not task:
        return

    cl       = task["client"]
    targets  = task["targets"]
    message  = task["message"]
    delay    = task["delay"]
    stop_set = task["stop_targets"]

    while True:
        for target in targets:
            if target in stop_set:
                continue
            try:
                if target.isdigit():
                    cl.direct_send(message, thread_ids=[target])
                else:
                    uid = cl.user_id_from_username(target)
                    cl.direct_send(message, thread_ids=[uid])
                print(f"[IG][{discord_user_id}] Gửi tới {target}")
            except Exception as e:
                print(f"[IG][{discord_user_id}] Lỗi {target}: {e}")
        time.sleep(delay)           

def parse_gmail_accounts(input_str: str):
    accounts = []
    for entry in re.split(r"[,/]", input_str):
        if "|" in entry:
            email, pwd = entry.split("|",1)
            accounts.append({
                "server": "smtp.gmail.com",
                "port": 465,
                "email": email.strip(),
                "password": pwd.strip(),
                "active": True
            })
    return accounts

def send_mail(smtp_info, to_email, content):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_info["server"], smtp_info["port"], context=context) as server:
        server.login(smtp_info["email"], smtp_info["password"])
        msg = MIMEText(content)
        msg["From"] = smtp_info["email"]
        msg["To"] = to_email
        msg["Subject"] = " "
        server.sendmail(smtp_info["email"], to_email, msg.as_string())

def gmail_spam_loop(tab, discord_user_id):
    smtp_list = tab["smtp_list"]
    to_email  = tab["to_email"]
    content   = tab["content"]
    delay     = tab["delay"]
    stop_evt  = tab["stop_event"]
    idx = 0
    while not stop_evt.is_set():
        active = [acc for acc in smtp_list if acc["active"]]
        if not active:
            for acc in smtp_list: acc["active"] = True
            active = smtp_list
        smtp = active[idx % len(active)]
        try:
            send_mail(smtp, to_email, content)
            print(f"[GMAIL][{discord_user_id}] ✓ {smtp['email']} → {to_email}")
        except smtplib.SMTPAuthenticationError:
            smtp["active"] = False
            print(f"[GMAIL][{discord_user_id}] ✗ Auth failed {smtp['email']}")
        except smtplib.SMTPDataError as e:
            txt = str(e)
            if "Quota" in txt or "limit" in txt:
                smtp["active"] = False
                print(f"[GMAIL][{discord_user_id}] Quota limit {smtp['email']}")
            else:
                print(f"[GMAIL][{discord_user_id}] DataErr {smtp['email']}: {e}")
        except Exception as e:
            print(f"[GMAIL][{discord_user_id}] Err {smtp['email']}: {e}")
        idx += 1
        for _ in range(int(delay)):
            if stop_evt.is_set(): break
            time.sleep(1)
        if stop_evt.is_set(): break
        time.sleep(delay - int(delay))      
                   
def get_uptime(start_time: datetime) -> str:
    elapsed = (datetime.now() - start_time).total_seconds()
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@tasks.loop(minutes=60)
async def cleanup_expired_users():
    users = load_users()
    to_remove = []
    for uid, exp in users.items():
        if exp and datetime.fromisoformat(exp) <= datetime.now():
            to_remove.append(uid)
    if to_remove:
        for uid in to_remove:
            _remove_user_and_kill_tabs(uid)


class Kem:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.init_params()

    def id_user(self):
        try:
            c_user = re.search(r"c_user=(\d+)", self.cookie).group(1)
            return c_user
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
        }
        try:
            response = requests.get('https://www.facebook.com', headers=headers)
            fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
            if not fb_dtsg_match:
                response = requests.get('https://mbasic.facebook.com', headers=headers)
                fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                if not fb_dtsg_match:
                    response = requests.get('https://m.facebook.com', headers=headers)
                    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
            else:
                raise Exception("Không thể lấy được fb_dtsg")
        except Exception as e:
            raise Exception(f"Lỗi khi khởi tạo tham số: {str(e)}")

    def gui_tn(self, recipient_id, message):
        if not message or not recipient_id:
            raise ValueError("ID Box và Nội Dung không được để trống")
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': recipient_id,
            'action_type': 'ma-type:user-generated-message',
            'body': message,
            'client': 'mercury',
            'author': f'fbid:{self.user_id}',
            'timestamp': timestamp,
            'source': 'source:chat:web',
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            'ephemeral_ttl_mode': '',
            '__user': self.user_id,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': self.fb_dtsg
        }
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'python-http/0.27.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        try:
            response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers)
            if response.status_code != 200:
                return {'success': False, 'error_description': f'Status: {response.status_code}'}
            if 'for (;;);' in response.text:
                clean = response.text.replace('for (;;);', '')
                result = json.loads(clean)
                if 'error' in result:
                    return {'success': False, 'error_description': result.get('errorDescription', 'Unknown error')}
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error_description': str(e)}

def spam_tab_worker(messenger: Kem, box_id: str, message: str, delay: float, stop_event: threading.Event, start_time: datetime, discord_user_id: str):
    success = 0
    fail = 0
    while not stop_event.is_set():
        result = messenger.gui_tn(box_id, message)
        ok = result.get("success", False)
        if ok:
            success += 1
            status = "OK"
        else:
            fail += 1
            status = "FAIL"
            stop_event.set()
        uptime = (datetime.now() - start_time).total_seconds()
        h, rem = divmod(int(uptime), 3600)
        m, s = divmod(rem, 60)
        print(f"[{messenger.user_id}] → {box_id} | {status} | Up: {h:02}:{m:02}:{s:02} | OK: {success} | FAIL: {fail}".ljust(120), end='\r')
        time.sleep(delay)
        gc.collect()
    print(f"\nTab của user {discord_user_id} với cookie {messenger.user_id} đã dừng.")

@tree.command(name="treomess", description="Treo tin nhắn Messenger")
@app_commands.describe(
    idbox="ID Box",
    cookie="Cookie Facebook",
    noidung="Nội dung cần gửi",
    delay="Delay mỗi lần gửi (giây)"
)
async def treomess(interaction: discord.Interaction, idbox: str, cookie: str, noidung: str, delay: float):
    discord_user_id = str(interaction.user.id)
    try:
        messenger = Kem(cookie)
    except Exception as e:
        return await interaction.response.send_message(f"Cookie không hợp lệ hoặc lỗi: {e}", ephemeral=True)

    stop_event = threading.Event()
    start_time = datetime.now()
    th = threading.Thread(
        target=spam_tab_worker,
        args=(messenger, idbox, noidung, delay, stop_event, start_time, discord_user_id),
        daemon=True
    )
    th.start()

    
    with TAB_LOCK:
        if discord_user_id not in user_tabs:
            user_tabs[discord_user_id] = []
        user_tabs[discord_user_id].append({
            "box_id": idbox,
            "delay": delay,
            "start": start_time,
            "stop_event": stop_event
        })

    short_content = shorten(noidung, width=1900, placeholder="...")

    await interaction.response.send_message(
        f"Đã khởi tab spam messenger cho <@{discord_user_id}>:\n"
        f"• ID Box: `{idbox}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Nội dung: `{short_content}`\n"
        f"• Thời điểm bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )

@tree.command(name="add", description="➕ Thêm user")
@app_commands.describe(user="Tag hoặc ID user", thoihan="Thời hạn (ví dụ: 7d)")
async def add(interaction: discord.Interaction, user: str, thoihan: str = None):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Từ chối truy cập",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=0xe74c3c
        )
        embed.set_footer(text="� Minato | Powered by Minato")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    user_id = user.replace("<@", "").replace(">", "").replace("!", "")
    days = None
    if thoihan and thoihan.endswith("d"):
        try:
            days = int(thoihan[:-1])
        except:
            embed = discord.Embed(
                title="⚠️ Thời hạn không hợp lệ",
                description="Phải nhập **số + d** (vd: `7d`).",
                color=0xf1c40f
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

    _add_user(user_id, days)

    embed = discord.Embed(
        title="✅ Thêm user thành công",
        description=f"👤 User: <@{user_id}>\n"
                    f"⏳ Thời hạn: **{'vĩnh viễn' if not days else f'{days} ngày'}**",
        color=0x2ecc71
    )
    embed.set_footer(text="🔥 Minato | Powered by Minato")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@tree.command(name="xoa", description="🗑 Xoá user")
@app_commands.describe(user="Tag hoặc ID user")
async def xoa(interaction: discord.Interaction, user: str):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Từ chối truy cập",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=0xe74c3c
        )
        embed.set_footer(text="🔥 Minato | Powered by Minato")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    user_id = user.replace("<@", "").replace(">", "").replace("!", "")
    _remove_user_and_kill_tabs(user_id)

    embed = discord.Embed(
        title="🗑 User đã bị xoá",
        description=f"👤 <@{user_id}> đã bị xoá quyền sử dụng bot\n"
                    f"🛑 Mọi tab của user này đã bị dừng.",
        color=0xe67e22
    )
    embed.set_footer(text="🔥 Minato | Powered by Minato")

    await interaction.response.send_message(embed=embed, ephemeral=True)
@tree.command(name="list", description="📋 Hiển thị danh sách user")
async def list_cmd(interaction: discord.Interaction):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Từ chối truy cập",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=0xe74c3c
        )
        embed.set_footer(text="� Minato | Powered by Minato")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    user_list = _get_user_list()
    if not user_list:
        embed = discord.Embed(
            title="📋 Danh sách rỗng",
            description="Hiện tại không có user nào được cấp quyền.",
            color=0xf1c40f
        )
        embed.set_footer(text="� Minato | Powered by Minato")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    embed = discord.Embed(
        title="📋 Danh sách user có quyền sử dụng bot",
        color=0x3498db
    )
    for uid, time_str in user_list:
        embed.add_field(
            name=f"👤 User: <@{uid}>",
            value=f"⏳ Thời hạn: `{time_str}`",
            inline=False
        )
    embed.set_footer(text="🔥  | Powered by Minato")

    await interaction.response.send_message(embed=embed, ephemeral=True)

from discord.ui import View, Button

@tree.command(name="tabtreomess", description="📊 Quản lý/Dừng tab treo messenger")
async def tabtreomess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=0xe74c3c
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with TAB_LOCK:
        tabs = user_tabs.get(discord_user_id, [])

    if not tabs:
        embed = discord.Embed(
            title="📭 Không có tab treo",
            description="Bạn chưa có tab treo Messenger nào đang hoạt động.",
            color=0xf1c40f
        )
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # Tạo Embed danh sách tab
    embed = discord.Embed(
        title="📊 Danh sách tab treo Messenger của bạn",
        color=0x3498db
    )
    for idx, tab in enumerate(tabs, start=1):
        uptime = get_uptime(tab["start"])
        embed.add_field(
            name=f"▶️ Tab {idx}",
            value=f"🆔 Box: `{tab['box_id']}`\n"
                  f"⏱ Delay: `{tab['delay']} giây`\n"
                  f"🕒 Uptime: `{uptime}`",
            inline=False
        )
    embed.set_footer(text="🔥 Minato | Powered by Minato")

    # Tạo View với nút Stop
    view = View(timeout=60)
    for idx, tab in enumerate(tabs, start=1):
        async def stop_callback(inter2: discord.Interaction, i=idx):
            if inter2.user.id != interaction.user.id:
                return await inter2.response.send_message("❌ Không phải tab của bạn.", ephemeral=True)

            with TAB_LOCK:
                chosen = tabs[i-1]
                chosen["stop_event"].set()
                tabs.pop(i-1)
                if not tabs:
                    del user_tabs[discord_user_id]

            stop_embed = discord.Embed(
                title="🛑 Tab đã dừng",
                description=f"Bạn đã dừng **Tab {i}** thành công!",
                color=0xe74c3c
            )
            await inter2.response.edit_message(embed=stop_embed, view=None)

        btn = Button(label=f"Dừng Tab {idx}", style=discord.ButtonStyle.red, emoji="🛑")
        btn.callback = stop_callback
        view.add_item(btn)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    
@tree.command(name="nhaymess", description="🤖 Spam nhây Facebook bằng cookie")
@app_commands.describe(
    cookies="Cookie (cách nhau dấu phẩy)",
    box_ids="ID Box (cách nhau dấu phẩy)",
    cau="Câu spam (ngăn cách bằng |, tuỳ chọn)",
    file="File .txt chứa câu (1 dòng = 1 câu, tuỳ chọn)",
    delay="Delay mỗi tin (giây)"
)
async def nhaymess(
    interaction: discord.Interaction,
    cookies: str,
    box_ids: str,
    cau: str = "",
    file: discord.Attachment = None,
    delay: float = 2.0
):
    await interaction.response.defer(ephemeral=True)
    discord_user_id = str(interaction.user.id)

    # ==== Cookies + Box ====
    cookie_list = [x.strip() for x in cookies.split(",") if x.strip()]
    id_list = [x.strip() for x in box_ids.split(",") if x.strip()]
    messengers = []
    for c in cookie_list:
        try:
            messengers.append(Kem(c))
        except Exception as e:
            print(f"[!] Cookie lỗi: {e}")

    if not messengers:
        embed = discord.Embed(
            title="❌ Cookie lỗi",
            description="Tất cả cookie bạn nhập đều **không hợp lệ**.",
            color=0xe74c3c
        )
        return await interaction.followup.send(embed=embed, ephemeral=True)

    # ==== Danh sách câu ====
    messages = []
    if cau:
        messages.extend([x.strip() for x in cau.split("|") if x.strip()])
    if file and file.filename.endswith(".txt"):
        text = (await file.read()).decode("utf-8", errors="ignore")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        messages.extend(lines)
    if not messages:
        messages = [
            "alo alo test nhây 🗿",
            "tỉnh đê 😎",
            " thức  chưa 👀",
            "tới công chuyện rồi 🤡",
            "nguuuuuuuuu"
        ]

 
    class NhayWorker:
        def __init__(self, messengers, box_ids, messages, delay, stop_event):
            self.messengers = messengers
            self.box_ids = box_ids
            self.messages = messages
            self.delay = delay
            self.stop_event = stop_event

        def run(self):
            idx = 0
            while not self.stop_event.is_set():
                msg = self.messages[idx % len(self.messages)]
                for messenger in self.messengers:
                    for box_id in self.box_ids:
                        try:
                            result = messenger.gui_tn(box_id, msg)
                            if result.get("success"):
                                print(f"[NHAY][{messenger.user_id}] → {box_id}: OK")
                            else:
                                print(f"[NHAY][{messenger.user_id}] → {box_id}: FAIL")
                        except Exception as e:
                            print(f"[NHAY][{messenger.user_id}] → {box_id}: ERROR {e}")
                        time.sleep(0.2)
                idx += 1
                time.sleep(self.delay)

    stop_event = threading.Event()
    start_time = datetime.now()
    worker = NhayWorker(messengers, id_list, messages, delay, stop_event)
    thread = threading.Thread(target=worker.run, daemon=True)
    thread.start()


    if discord_user_id not in user_nhaymess_tabs:
        user_nhaymess_tabs[discord_user_id] = []
    user_nhaymess_tabs[discord_user_id].append({
        "messengers": messengers,
        "box_ids": id_list,
        "delay": delay,
        "start_time": start_time,
        "stop_event": stop_event,
        "thread": thread,
        "messages": messages
    })

  
    def build_embed():
        uptime = str(datetime.now() - start_time).split(".")[0]
        embed = discord.Embed(
            title="✅ Tab Nhây Messenger",
            color=0x2ecc71
        )
        embed.add_field(name="👤 Người dùng", value=f"<@{discord_user_id}>", inline=False)
        embed.add_field(name="🍪 Cookies hợp lệ", value=str(len(messengers)), inline=True)
        embed.add_field(name="📝 Số câu", value=str(len(messages)), inline=True)
        embed.add_field(name="⏱ Delay", value=f"{delay} giây", inline=True)
        embed.add_field(name="🕒 Uptime", value=uptime, inline=False)
        embed.set_footer(text="� Minato | Powered by Minato")
        return embed

    view = View(timeout=120)


    async def refresh_callback(inter2: discord.Interaction):
        if inter2.user.id != interaction.user.id:
            return await inter2.response.send_message("❌ Không phải tab của bạn.", ephemeral=True)
        await inter2.response.edit_message(embed=build_embed(), view=view)

    btn_refresh = Button(label="Làm mới", style=discord.ButtonStyle.blurple, emoji="🔄")
    btn_refresh.callback = refresh_callback
    view.add_item(btn_refresh)

    await interaction.followup.send(embed=build_embed(), view=view, ephemeral=True)

from discord.ui import View, Button

@tree.command(name="tabnhaymess", description="📋 Quản lý tab nhây Messenger")
async def tabnhaymess(interaction: discord.Interaction):
    discord_user_id = str(interaction.user.id)
    tabs = user_nhaymess_tabs.get(discord_user_id, [])
    if not tabs:
        embed = discord.Embed(
            title="⚠️ Không có tab nào đang chạy",
            description="Bạn chưa mở tab nhây Messenger nào.",
            color=0xf1c40f
        )
        embed.set_footer(text="� Minato | Powered by Minato")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    def build_embed():
        embed = discord.Embed(
            title="📋 Danh sách tab nhây đang chạy",
            description=f"👤 Chủ sở hữu: <@{discord_user_id}>",
            color=0x1abc9c  # màu xanh ngọc VIP
        )
        for idx, tab in enumerate(tabs, start=1):
            elapsed = (datetime.now() - tab["start_time"]).total_seconds()
            uptime = format_time(int(elapsed))
            embed.add_field(
                name=f"#{idx} 📨 Box: {', '.join(tab['box_ids'])}",
                value=(
                    f"🍪 Accounts: `{len(tab['messengers'])}`\n"
                    f"📝 Câu spam: `{len(tab['messages'])}`\n"
                    f"⏱ Delay: `{tab['delay']}s`\n"
                    f"🕒 Uptime: `{uptime}`"
                ),
                inline=False
            )
        embed.set_footer(text="� Minato | Powered by Minato")
        embed.timestamp = datetime.now()
        return embed

    view = View(timeout=120)


    async def refresh_callback(inter2: discord.Interaction):
        if inter2.user.id != interaction.user.id:
            return await inter2.response.send_message("❌ Không phải tab của bạn.", ephemeral=True)
        await inter2.response.edit_message(embed=build_embed(), view=view)

    btn_refresh = Button(label="Làm mới", style=discord.ButtonStyle.blurple, emoji="🔄")
    btn_refresh.callback = refresh_callback
    view.add_item(btn_refresh)


    for idx, tab in enumerate(tabs):
        async def stop_callback(inter2: discord.Interaction, tab_index=idx):
            if inter2.user.id != interaction.user.id:
                return await inter2.response.send_message("❌ Không phải tab của bạn.", ephemeral=True)
            try:
                tabs[tab_index]["stop_event"].set()
                del tabs[tab_index]
                if not tabs:
                    del user_nhaymess_tabs[discord_user_id]
                embed2 = discord.Embed(
                    title="🛑 Tab đã dừng",
                    description=f"Bạn đã dừng tab số **{tab_index+1}** thành công.",
                    color=0xe74c3c
                )
                embed2.set_footer(text="� Minato | Powered by Minato")
                await inter2.response.edit_message(embed=embed2, view=None)
            except Exception as e:
                await inter2.response.send_message(f"❌ Lỗi khi dừng tab: {e}", ephemeral=True)

        btn = Button(
            label=f"Stop {idx+1}",
            style=discord.ButtonStyle.red,
            emoji="🛑"
        )
        btn.callback = stop_callback
        view.add_item(btn)

    await interaction.response.send_message(embed=build_embed(), view=view, ephemeral=True)


def format_time(seconds: int):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"

import discord
from discord import app_commands
from discord.ext import commands

class MenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=180)

    @discord.ui.select(
        placeholder="🔽 Chọn danh mục để xem lệnh...",
        options=[
            discord.SelectOption(label="📋 Quản lý quyền", value="quyen", description="Thêm, xóa, danh sách user"),
            discord.SelectOption(label="💬 Messenger", value="messenger", description="Treo/nhây tin nhắn Messenger"),
            discord.SelectOption(label="⚙️ Hệ thống", value="hethong", description="Các lệnh hệ thống bot")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        if select.values[0] == "quyen":
            embed = discord.Embed(
                title="📋 Quản lý quyền",
                description=(
                    "🔹 `/add` → Thêm user được cấp quyền (admin dùng)\n"
                    "🔹 `/xoa` → Xóa quyền user + dừng tab\n"
                    "🔹 `/list` → Xem danh sách user được cấp quyền"
                ),
                color=0xf1c40f
            )
            embed.set_image(url="https://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif")

        elif select.values[0] == "messenger":
            embed = discord.Embed(
                title="💬 Messenger",
                description=(
                    "🔹 `/treomess` → Treo tin nhắn Messenger bằng cookie + ID Box\n"
                    "🔹 `/tabtreomess` → Quản lý/Dừng tab treo Messenger\n"
                    "🔹 `/nhaymess` → Spam nhây Facebook bằng nhiều cookie/box\n"
                    "🔹 `/tabnhaymess` → Quản lý tab nhây Messenger"
                ),
                color=0x1abc9c
            )
            embed.set_image(url="By Minato ahttps://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif")  # gif chat loading

        else:
            embed = discord.Embed(
                title="⚙️ Hệ thống",
                description="🔹 `/menu` → Hiển thị menu chức năng đẹp nhất có thể",
                color=0x2ecc71
            )
            embed.set_image(url="https://i.pinimg.com/736x/69/2f/cf/692fcf035024e569f6938d53e4c0a1c0.jpg")

        embed.set_footer(text="⚡ Chọn thêm danh mục bên dưới để xem chi tiết ⚡")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="📜 Show All", style=discord.ButtonStyle.secondary)
    async def show_all(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📖 TẤT CẢ CHỨC NĂNG",
            description="By Minato `",
            color=0x9b59b6
        )
        embed.add_field(
            name="📋 Quản lý quyền",
            value="`/add` | `/xoa` | `/list`",
            inline=False
        )
        embed.add_field(
            name="💬 Messenger",
            value="`/treomess` | `/tabtreomess` | `/nhaymess` | `/tabnhaymess`",
            inline=False
        )
        embed.add_field(
            name="⚙️ Hệ thống",
            value="`/menu`",
            inline=False
        )
        embed.set_image(url="https://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif")
        embed.set_footer(text="⚡ Menu hiển thị toàn bộ lệnh ⚡")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="🔄 Refresh", style=discord.ButtonStyle.primary)
    async def refresh(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✨ MENU  BOT ✨",
            description="By Minato `",
            color=0x00ffcc
        )
        embed.set_thumbnail(url="https://i.pinimg.com/736x/4b/f0/2e/4bf02e712d44aefb991dd49977fe3551.jpg")
        embed.set_image(url="https://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif")
        embed.set_footer(text="⚡ Chọn danh mục bên dưới để xem chi tiết ⚡")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="❌ Đóng", style=discord.ButtonStyle.danger)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()

# Slash command menu
@tree.command(name="menu", description="Hiển thị danh sách chức năng của bot")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="✨ MENU CHỨC NĂNG BOT ✨",
        description="By Minato `",
        color=0x00ffcc
    )
    embed.set_thumbnail(url="https://i.pinimg.com/736x/69/2f/cf/692fcf035024e569f6938d53e4c0a1c0.jpg")
    embed.set_image(url="https://i.pinimg.com/originals/5d/2c/44/5d2c44694918947aede42306cb7154d0.gif")
    embed.set_footer(text="⚡ Chọn danh mục bên dưới để xem chi tiết ⚡")

    view = MenuView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Slash commands loaded! Logged in as {bot.user}")
bot.run(TOKEN)