import ast
import contextlib
import html as htmllib
import io
import json
import logging
import os
import re
import shutil
import sqlite3
import sys
import threading
import time
import tokenize
import uuid
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import quote
import requests
import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException

def O0OOO0OO00O0():
    O00O00OO000O = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    try:
        with open(O00O00OO000O, encoding='utf-8') as OOOOO000O000:
            for O0000OOO0OOO in OOOOO000O000:
                O0000OOO0OOO = O0000OOO0OOO.strip()
                if O0000OOO0OOO and (not O0000OOO0OOO.startswith('#')) and ('=' in O0000OOO0OOO):
                    O0OOO0OOOOO0, OOOO000OOO0O = O0000OOO0OOO.split('=', 1)
                    os.environ.setdefault(O0OOO0OOOOO0.strip(), OOOO000OOO0O.strip().strip('"').strip("'"))
    except OSError:
        pass
O0OOO0OO00O0()
OOO00O0O0O00 = os.environ.get('BOT_TOKEN', '8635733010:AAESueKqFjJbfMF7Seh7r2Fja85AlWzBcFE').strip()
OO0O0O00O0O0 = {int(O0OO00O000OO) for O0OO00O000OO in re.findall('-?\\d+', os.environ.get('OWNER_IDS', '8097573260'))}
O0O0O000O00O = os.environ.get('OWNER_USERNAME', '').strip()
OOO0O0O00000 = os.environ.get('PIXELDRAIN_API_KEY', 'ba25a1e6-cf4c-4b0e-864d-29451886d7df').strip()
O0OO0O00OOOO = os.environ.get('PIXELDRAIN_BACKUP_API_KEY', '8395cc99-be3a-4d1b-a175-b0f31dcf936f').strip()
O0000O0O0OO0 = os.environ.get('PIXELDRAIN_API_URL', 'https://pixeldrain.com/api').rstrip('/')
if not OOO00O0O0O00:
    raise SystemExit('BOT_TOKEN missing')
if not OOO0O0O00000:
    raise SystemExit('PIXELDRAIN_API_KEY missing')
SELF_STATE_ARCHIVE_NAME = 'self_state_main_bot.zip'
O0OO0OOO0O0O = float(os.environ.get('AUTO_SELF_SYNC_SECONDS', '3600'))
O0000OO0OO00 = 20 * 1024 * 1024
MAX_HOSTED_PER_USER = 1
O000OOOOO0OO = 20 * 1024 * 1024
OO00OOO000O0 = 35 * 1024 * 1024
PAGE_SIZE = 8
ALLOWED_DATA_EXTENSIONS = ('.zip', '.json', '.db', '.sqlite', '.sqlite3', '.txt', '.csv', '.ini', '.yaml', '.yml', '.dat', '.session')
O00OOOO0000O = os.path.dirname(os.path.abspath(__file__))
O0OOO0OOO000 = os.path.join(O00OOOO0000O, 'data')
OO0000O00OOO = os.path.abspath(os.environ.get('BOT_SHARED_DIR', O0OOO0OOO000))
O0O0OOO0OOO0 = os.path.join(O0OOO0OOO000, 'uploads')
OO0OOO00OO0O = os.path.join(O0OOO0OOO000, 'user_data_archives')
O000O0000O00 = os.path.join(OO0000O00OOO, 'logs')
OO00OO0O00OO = os.path.join(O0OOO0OOO000, 'backups')
O0O00OOOO0O0 = os.path.join(O0OOO0OOO000, 'suspicious')
OOOO00OOO00O = os.path.join(O0OOO0OOO000, 'runtime')
OOO0OO0O0000 = os.path.abspath(os.environ.get('BOT_DB_PATH', os.path.join(OO0000O00OOO, 'bot.db')))
for O0O0OOOOOOOO in (O0OOO0OOO000, OO0000O00OOO, O0O0OOO0OOO0, OO0OOO00OO0O, O000O0000O00, OO00OO0O00OO, O0O00OOOO0O0, OOOO00OOO00O, os.path.dirname(OOO0OO0O0000)):
    os.makedirs(O0O0OOOOOOOO, exist_ok=True)
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(name)s | %(message)s', level=logging.INFO, handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(O0OOO0OOO000, 'bot.log'), encoding='utf-8')])
O0OOO0000OO0 = logging.getLogger('hostbot.main')
OOO000O00O0O = time.time()

def OOO0O00OOO00():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def OOO0O0O0O0OO(OOO0000O00O0):
    return htmllib.escape(str(OOO0000O00O0 if OOO0000O00O0 is not None else ''), quote=False)

def O0O0O00O000O(OOOOOOO0O000):
    OOOOOOO0O000 = float(OOOOOOO0O000 or 0)
    for OOOOOO0O0OOO in ('B', 'KB', 'MB', 'GB'):
        if OOOOOOO0O000 < 1024 or OOOOOO0O0OOO == 'GB':
            return f'{OOOOOOO0O000:.0f} {OOOOOO0O0OOO}' if OOOOOO0O0OOO == 'B' else f'{OOOOOOO0O000:.2f} {OOOOOO0O0OOO}'
        OOOOOOO0O000 /= 1024
    return f'{OOOOOOO0O000:.2f} GB'

def O0O0000OOOO0(OO000OOOOO0O):
    OO000OOOOO0O = int(max(0, OO000OOOOO0O))
    O0O0O0OO0O00, OOO0O00000OO = divmod(OO000OOOOO0O, 86400)
    OOOOO0O0O0O0, OOO0O00000OO = divmod(OOO0O00000OO, 3600)
    O0OOOOO0O00O, OOOO00000000 = divmod(OOO0O00000OO, 60)
    O0O0O0O0OOOO = []
    if O0O0O0OO0O00:
        O0O0O0O0OOOO.append(f'{O0O0O0OO0O00}ي')
    if OOOOO0O0O0O0:
        O0O0O0O0OOOO.append(f'{OOOOO0O0O0O0}س')
    if O0OOOOO0O00O:
        O0O0O0O0OOOO.append(f'{O0OOOOO0O00O}د')
    if not O0O0O0O0OOOO:
        O0O0O0O0OOOO.append(f'{OOOO00000000}ث')
    return ' '.join(O0O0O0O0OOOO)

def OOO0O0OO0OO0(O000OO0O0O0O, OO00OO00OO00, width=10):
    OO000O0OO0OO = 0 if not OO00OO00OO00 else min(1.0, O000OO0O0O0O / OO00OO00OO00)
    OOOO0O0000O0 = round(OO000O0OO0OO * width)
    return '▰' * OOOO0O0000O0 + '▱' * (width - OOOO0O0000O0) + f' {OO000O0OO0OO * 100:.0f}%'

def O0OO0O00000O(OO00000OO000):
    O0OOO0000OOO = os.path.basename(OO00000OO000 or 'script.py')
    O0OOO0000OOO = re.sub('[^\\w.\\-]', '_', O0OOO0000OOO, flags=re.UNICODE)[:80].strip('._') or 'script'
    if not O0OOO0000OOO.lower().endswith('.py'):
        O0OOO0000OOO += '.py'
    return O0OOO0000OOO

def O00O0O00OOO0(O0OO00O0OO0O):
    OO00OOO00O00 = os.path.basename(O0OO00O0OO0O or 'data.bin')
    OO00OOO00O00 = re.sub('[^\\w.\\-]', '_', OO00OOO00O00, flags=re.UNICODE)[:100].strip('._') or 'data.bin'
    return OO00OOO00O00

def O00000OO00OO(OO00OO0OO0O0):
    return OO00OO0OO0O0 in OO0O0O00O0O0

def O000O00OO00O(OOOO00OO0000):
    return 1 if int(OOOO00OO0000) % 2 == 1 else 2

def O0O00O0OOOOO(O00OOOO00OO0, O0OOO0000O0O):
    O0O0OOOOOO00 = O000O00OO00O(O00OOOO00OO0)
    return [f'w{O0O0OOOOOO00}_udata_{int(O00OOOO00OO0)}_{int(O0OOO0000O0O)}.zip', f'udata_{int(O00OOOO00OO0)}_{int(O0OOO0000O0O)}.zip']
O0O00000O0OO = ThreadPoolExecutor(max_workers=16)

def O0000OOO00O0(O0OOOOOO000O, *O0000O00O000):

    def OOOO00OO0OOO():
        try:
            O0OOOOOO000O(*O0000O00O000)
        except Exception:
            O0OOO0000OO0.exception('background task failed')
    O0O00000O0OO.submit(OOOO00OO0OOO)
PD_TIMEOUT = (15, 600)
O0000OOOOOO0 = re.compile('^run_(\\d+)_(\\d+)\\.py$')

def O00OOO0OOO0O(OOOO000O0O00):
    return f"{O0000O0O0OO0}/file/{quote(str(OOOO000O0O00), safe='')}"

def O00OOOO000OO(O0O00000O0O0, remote_name=None, api_key=None):
    OO0O0O00O00O = (api_key or OOO0O0O00000).strip()
    if not OO0O0O00O00O or not os.path.isfile(O0O00000O0O0):
        return None
    OOOO0OO00000 = O00OOO0OOO0O(remote_name or os.path.basename(O0O00000O0O0))
    for O0O00000OOOO in range(1, 4):
        try:
            with open(O0O00000O0O0, 'rb') as OO0O000O0OO0:
                OOO000OO0O0O = requests.put(OOOO0OO00000, data=OO0O000O0OO0, auth=('', OO0O0O00O00O), timeout=PD_TIMEOUT)
            if OOO000OO0O0O.status_code in (200, 201):
                O00O00O0OO00 = OOO000OO0O0O.json()
                if O00O00O0OO00.get('success', True) is not False and O00O00O0OO00.get('id'):
                    return str(O00O00O0OO00['id'])
            if 400 <= OOO000OO0O0O.status_code < 500 and OOO000OO0O0O.status_code != 429:
                return None
        except Exception as e:
            O0OOO0000OO0.warning('pd_upload error (%s/3): %s', O0O00000OOOO, e)
        time.sleep(2 * O0O00000OOOO)
    return None

def OOOOO0OOO0OO(O00OO0O000O0, OO00O0O0000O, OO000OOOO000, O0O0OOO00OOO):
    if not O0OO0O00OOOO or not os.path.isfile(O00OO0O000O0):
        return None
    OOOOO0O0OOO0 = f'archive_{int(OO00O0O0000O)}_{int(OO000OOOO000)}_{O0OO0O00000O(O0O0OOO00OOO)}'
    return O00OOOO000OO(O00OO0O000O0, OOOOO0O0OOO0, O0OO0O00OOOO)

def O000O000OO0O(O00O0O000O00, O0OOO00O00OO, api_key=None):
    OOOO00OOO0O0 = (api_key or OOO0O0O00000).strip()
    if not OOOO00OOO0O0 or not O00O0O000O00:
        return False
    O00OOOOOO00O = f'{O0OOO00O00OO}.{uuid.uuid4().hex}.pdpart'
    for OOOOO00O0000 in range(1, 4):
        try:
            os.makedirs(os.path.dirname(os.path.abspath(O0OOO00O00OO)), exist_ok=True)
            with requests.get(O00OOO0OOO0O(O00O0O000O00), auth=('', OOOO00OOO0O0), stream=True, timeout=PD_TIMEOUT) as O00OO0OOOOOO:
                if O00OO0OOOOOO.status_code == 200:
                    with open(O00OOOOOO00O, 'wb') as O0000O000OO0:
                        for O000OOO00O0O in O00OO0OOOOOO.iter_content(chunk_size=256 * 1024):
                            if O000OOO00O0O:
                                O0000O000OO0.write(O000OOO00O0O)
                    os.replace(O00OOOOOO00O, O0OOO00O00OO)
                    return True
                if 400 <= O00OO0OOOOOO.status_code < 500 and O00OO0OOOOOO.status_code != 429:
                    return False
        except Exception as e:
            O0OOO0000OO0.warning('pd_download error (%s/3): %s', OOOOO00O0000, e)
        finally:
            if os.path.exists(O00OOOOOO00O):
                with contextlib.suppress(OSError):
                    os.remove(O00OOOOOO00O)
        time.sleep(2 * OOOOO00O0000)
    return False

def OOOO0O0OOO00(OO0O0OO0O0OO, api_key=None):
    O0O0OO0O00O0 = (api_key or OOO0O0O00000).strip()
    if not O0O0OO0O00O0 or not OO0O0OO0O0OO:
        return True
    try:
        OO0O0O0O000O = requests.delete(O00OOO0OOO0O(OO0O0OO0O0OO), auth=('', O0O0OO0O00O0), timeout=(15, 60))
        if OO0O0O0O000O.status_code in (200, 204, 404):
            return True
    except Exception:
        pass
    return False

def O000O0O0O000(api_key=None):
    OOO0O00O0OOO = (api_key or OOO0O0O00000).strip()
    if not OOO0O00O0OOO:
        return []
    OOO0OO0OOOO0 = requests.get(f'{O0000O0O0OO0}/user/files', auth=('', OOO0O00O0OOO), timeout=(10, 30))
    if OOO0OO0OOOO0.status_code == 401:
        raise RuntimeError('Pixeldrain 401')
    OOO0OO0OOOO0.raise_for_status()
    return [OOOO00OOOO0O for OOOO00OOOO0O in OOO0OO0OOOO0.json().get('files') or [] if OOOO00OOOO0O.get('id') and OOOO00OOOO0O.get('name')]

def O0OO0OOO0O00(OO0O0O0000OO, api_key=None):
    OO000OO0O0O0 = (api_key or OOO0O0O00000).strip()
    if not OO0O0O0000OO:
        return False
    try:
        OOO0O0O0O00O = requests.get(O00OOO0OOO0O(OO0O0O0000OO) + '/info', auth=('', OO000OO0O0O0), timeout=(10, 30))
        if OOO0O0O0O00O.status_code == 200:
            return True
        if OOO0O0O0O00O.status_code == 404:
            return False
    except Exception:
        pass
    return None

def OOOOOO000000(O00O0OO0OOOO, api_key=None):
    O0OO0OOO0OO0 = True
    try:
        for O0OOO00O0O0O in O000O0O0O000(api_key):
            if O0OOO00O0O0O.get('name') == O00O0OO0OOOO:
                if not OOOO0O0OOO00(str(O0OOO00O0O0O['id']), api_key):
                    O0OO0OOO0OO0 = False
    except Exception:
        O0OO0OOO0OO0 = False
    return O0OO0OOO0OO0

def OO0OO000OO00():
    if os.path.isfile(OOO0OO0O0000) and os.path.getsize(OOO0OO0O0000) > 4096:
        return
    O0OO000OO0OO, OO00000000O0 = (None, None)
    for OOO00000000O in (O0OO0O00OOOO, OOO0O0O00000):
        if not OOO00000000O:
            continue
        with contextlib.suppress(Exception):
            O0O00O000OOO = [OO00OO0OO000 for OO00OO0OO000 in O000O0O0O000(OOO00000000O) if OO00OO0OO000['name'] == SELF_STATE_ARCHIVE_NAME]
            if O0O00O000OOO:
                OOO00000OOO0 = max(O0O00O000OOO, key=lambda it: str(it.get('date_upload') or ''))
                O0OO000OO0OO = str(OOO00000OOO0['id'])
                OO00000000O0 = OOO00000000O
                break
    if not O0OO000OO0OO:
        return
    OO0OOOO0OO0O = os.path.join(OOOO00OOO00O, f'restore_main_{uuid.uuid4().hex}.zip')
    try:
        if O000O000OO0O(O0OO000OO0OO, OO0OOOO0OO0O, OO00000000O0) and zipfile.is_zipfile(OO0OOOO0OO0O):
            with zipfile.ZipFile(OO0OOOO0OO0O, 'r') as OO0OO0O00O00:
                for OOO0OOOO00OO in OO0OO0O00O00.infolist():
                    if OOO0OOOO00OO.is_dir():
                        continue
                    O00OO00OO0O0 = OOO0OOOO00OO.filename.replace('\\', '/').lstrip('/')
                    OOOOOOOO0000 = [O0OO0O0OO00O for O0OO0O0OO00O in O00OO00OO0O0.split('/') if O0OO0O0OO00O and O0OO0O0OO00O not in ('.', '..')]
                    if not OOOOOOOO0000:
                        continue
                    if O00OO00OO0O0 == 'bot.db':
                        for O00O000OOOOO in ('-wal', '-shm'):
                            with contextlib.suppress(OSError):
                                os.remove(OOO0OO0O0000 + O00O000OOOOO)
                        with open(OOO0OO0O0000, 'wb') as OOO0O0O00OO0:
                            OOO0O0O00OO0.write(OO0OO0O00O00.read(OOO0OOOO00OO.filename))
                    elif OOOOOOOO0000[0] in ('uploads', 'user_data_archives', 'suspicious'):
                        OOO00O000O0O = os.path.join(O0OOO0OOO000, *OOOOOOOO0000)
                        os.makedirs(os.path.dirname(OOO00O000O0O), exist_ok=True)
                        with open(OOO00O000O0O, 'wb') as OOO0O0O00OO0:
                            OOO0O0O00OO0.write(OO0OO0O00O00.read(OOO0OOOO00OO.filename))
            O0OOO0000OO0.info('✅ Restored main bot state from online (%s)', O0OO000OO0OO)
    except Exception as e:
        O0OOO0000OO0.warning('Failed to restore main bot state: %s', e)
    finally:
        with contextlib.suppress(OSError):
            if os.path.exists(OO0OOOO0OO0O):
                os.remove(OO0OOOO0OO0O)
OO0OO000OO00()
O0OOO0OOOO00 = threading.RLock()
O000OO00O0OO = sqlite3.connect(OOO0OO0O0000, check_same_thread=False, isolation_level=None)
O000OO00O0OO.row_factory = sqlite3.Row
O000OO00O0OO.execute('PRAGMA busy_timeout=30000')
O000OO00O0OO.execute('PRAGMA journal_mode=DELETE')
O000OO00O0OO.execute('PRAGMA synchronous=FULL')
O000OO00O0OO.executescript("\nCREATE TABLE IF NOT EXISTS users(\n    user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,\n    joined_at TEXT, last_seen TEXT,\n    banned INTEGER DEFAULT 0, ban_reason TEXT, active INTEGER DEFAULT 1,\n    panel_msg_id INTEGER DEFAULT NULL, max_files INTEGER DEFAULT 1);\nCREATE TABLE IF NOT EXISTS files(\n    id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,\n    file_name TEXT NOT NULL, path TEXT NOT NULL, size INTEGER DEFAULT 0,\n    status TEXT DEFAULT 'pending', desired_run INTEGER DEFAULT 0, pid INTEGER,\n    uploaded_at TEXT, approved_at TEXT, approved_by INTEGER,\n    last_start TEXT, scan_note TEXT, pd_id TEXT, backup_pd_id TEXT,\n    data_pd_id TEXT, data_backup_pd_id TEXT,\n    auto_restart INTEGER DEFAULT 1, content BLOB);\nCREATE TABLE IF NOT EXISTS channels(\n    id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT NOT NULL UNIQUE,\n    title TEXT, link TEXT, added_at TEXT);\nCREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY, value TEXT);\n")
for OO0O00OO00O0 in ('ALTER TABLE files ADD COLUMN pd_id TEXT', 'ALTER TABLE files ADD COLUMN backup_pd_id TEXT', 'ALTER TABLE files ADD COLUMN data_pd_id TEXT', 'ALTER TABLE files ADD COLUMN data_backup_pd_id TEXT', 'ALTER TABLE files ADD COLUMN auto_restart INTEGER DEFAULT 1', 'ALTER TABLE files ADD COLUMN content BLOB', 'ALTER TABLE users ADD COLUMN panel_msg_id INTEGER DEFAULT NULL', 'ALTER TABLE users ADD COLUMN max_files INTEGER DEFAULT 1'):
    with contextlib.suppress(sqlite3.OperationalError):
        O000OO00O0OO.execute(OO0O00OO00O0)

def OOO0O0OO000O(O00O0000O000, args=()):
    with O0OOO0OOOO00:
        return O000OO00O0OO.execute(O00O0000O000, args).lastrowid

def OO0OOOOO0OOO(OO0O00OOOOO0, args=()):
    with O0OOO0OOOO00:
        OO00O00OOO0O = O000OO00O0OO.execute(OO0O00OOOOO0, args).fetchone()
        return dict(OO00O00OOO0O) if OO00O00OOO0O else None

def OOOOOO0O0O00(O000O0O000OO, args=()):
    with O0OOO0OOOO00:
        return [dict(OOO0OO00O0O0) for OOO0OO00O0O0 in O000OO00O0OO.execute(O000O0O000OO, args).fetchall()]

def O0000000O00O(O00000O00000, default=None):
    O000OO00OOOO = OO0OOOOO0OOO('SELECT value FROM settings WHERE key=?', (O00000O00000,))
    return O000OO00OOOO['value'] if O000OO00OOOO else default

def O00OOO0O0OO0(O000OOOO0O0O, O00OOOO0OO00):
    OOO0O0OO000O('INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (O000OOOO0O0O, str(O00OOOO0OO00)))

def OOO00OOOO0OO():
    return O0000000O00O('protection', '1') == '1'

def OOO00OO000O0(OOOO0OO0000O):
    OO0O00OOO000 = OOO0O00OOO00()
    OOO0O0OO000O('INSERT INTO users(user_id,username,first_name,joined_at,last_seen,active,max_files) VALUES(?,?,?,?,?,1,?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name, last_seen=excluded.last_seen, active=1', (OOOO0OO0000O.id, OOOO0OO0000O.username, OOOO0OO0000O.first_name or '', OO0O00OOO000, OO0O00OOO000, MAX_HOSTED_PER_USER))
    return O00OO0O00OOO(OOOO0OO0000O.id)

def O00OO0O00OOO(OO000OO0OOO0):
    return OO0OOOOO0OOO('SELECT * FROM users WHERE user_id=?', (OO000OO0OOO0,))

def O0OO0O00OO0O(O0O000000O00):
    if O00000OO00OO(O0O000000O00):
        return 999
    O0O00O0O00OO = O00OO0O00OOO(O0O000000O00)
    return max(1, int(O0O00O0O00OO and O0O00O0O00OO.get('max_files') or MAX_HOSTED_PER_USER))

def O0OOOOOOO0O0(OO00O0OOO00O, uid=None):
    if not OO00O0OOO00O:
        return str(uid)
    if OO00O0OOO00O.get('username'):
        return '@' + OO00O0OOO00O['username']
    return OO00O0OOO00O.get('first_name') or str(OO00O0OOO00O['user_id'])

def O0000O0O0000(O0000OOOOOOO, uid=None):
    if not O0000OOOOOOO:
        return f'<code>{uid}</code>'
    OO0O00000OO0 = OOO0O0O0O0OO(O0000OOOOOOO.get('first_name') or O0000OOOOOOO.get('username') or O0000OOOOOOO['user_id'])
    return f"""<a href="tg://user?id={O0000OOOOOOO['user_id']}">{OO0O00000OO0}</a>"""
_SELECT_FILE_COLS = 'id, user_id, file_name, path, size, status, desired_run, pid, uploaded_at, approved_at, approved_by, last_start, scan_note, pd_id, backup_pd_id, data_pd_id, data_backup_pd_id, auto_restart'

def O0OOO0O00O0O(O000000OOO00):
    return OO0OOOOO0OOO(f'SELECT {_SELECT_FILE_COLS} FROM files WHERE id=?', (O000000OOO00,))

def OO0000O0O0OO(OOOOO00O00O0):
    return OOOOOO0O0O00(f'SELECT {_SELECT_FILE_COLS} FROM files WHERE user_id=? ORDER BY id DESC', (OOOOO00O00O0,))

def O000000O000O(O00O0OO0O000):
    OO0O0O0O0OOO = OO0OOOOO0OOO('SELECT COALESCE(SUM(size),0) AS s FROM files WHERE user_id=?', (O00O0OO0O000,))
    return int(OO0O0O0O0OOO['s'])

def O0OOO00OOOO0(O00OOOOOOO0O):
    OO0000OO0O00 = OO0OOOOO0OOO("SELECT COUNT(*) AS c FROM files WHERE user_id=? AND status='approved'", (O00OOOOOOO0O,))
    return int(OO0000OO0O00['c'])

def OO00000000OO(O00O00O0O0O0):
    O00O0OO0O00O = OO0OOOOO0OOO("SELECT COUNT(*) AS c FROM files WHERE user_id=? AND status='pending'", (O00O00O0O0O0,))
    return int(O00O0OO0O00O['c']) > 0
O000O0000000 = threading.Lock()

def O00000O0OOOO():
    if not O000O0000000.acquire(blocking=False):
        return False
    O00000OO0OO0 = os.path.join(OOOO00OOO00O, f'self_db_{uuid.uuid4().hex}.sqlite')
    OOO00O0O0O0O = os.path.join(OOOO00OOO00O, f'self_main_{uuid.uuid4().hex}.zip')
    try:
        with O0OOO0OOOO00:
            OOO00O00OO00 = sqlite3.connect(O00000OO0OO0)
            try:
                O000OO00O0OO.backup(OOO00O00OO00)
            finally:
                OOO00O00OO00.close()
        with zipfile.ZipFile(OOO00O0O0O0O, 'w', zipfile.ZIP_DEFLATED) as O00OOO0OO0OO:
            if os.path.isfile(O00000OO0OO0):
                O00OOO0OO0OO.write(O00000OO0OO0, arcname='bot.db')
            for O000OO0000O0 in (O0O0OOO0OOO0, OO0OOO00OO0O):
                if os.path.isdir(O000OO0000O0):
                    for O000OO00000O, OO0OO00OO000, O00O00000OOO in os.walk(O000OO0000O0):
                        for O0O0OO00OOO0 in O00O00000OOO:
                            O000O0O0OO0O = os.path.join(O000OO00000O, O0O0OO00OOO0)
                            OOO00OO00O00 = os.path.relpath(O000O0O0OO0O, O0OOO0OOO000)
                            with contextlib.suppress(OSError):
                                if os.path.getsize(O000O0O0OO0O) <= 35 * 1024 * 1024:
                                    O00OOO0OO0OO.write(O000O0O0OO0O, arcname=OOO00OO00O00)
        for OO0OO0OO00OO in (OOO0O0O00000, O0OO0O00OOOO):
            if not OO0OO0OO00OO:
                continue
            OOO00O0OO0O0 = O00OOOO000OO(OOO00O0O0O0O, SELF_STATE_ARCHIVE_NAME, OO0OO0OO00OO)
            if OOO00O0OO0O0:
                with contextlib.suppress(Exception):
                    for OOO0000OO00O in O000O0O0O000(OO0OO0OO00OO):
                        if OOO0000OO00O['name'] == SELF_STATE_ARCHIVE_NAME and str(OOO0000OO00O['id']) != OOO00O0OO0O0:
                            OOOO0O0OOO00(str(OOO0000OO00O['id']), OO0OO0OO00OO)
        return True
    except Exception as e:
        O0OOO0000OO0.warning('sync_self_state_online failed: %s', e)
        return False
    finally:
        for O000O0OO0000 in (O00000OO0OO0, OOO00O0O0O0O):
            if os.path.exists(O000O0OO0000):
                with contextlib.suppress(OSError):
                    os.remove(O000O0OO0000)
        O000O0000000.release()

def OOOOOO0OOOOO():
    while True:
        time.sleep(max(60.0, O0OO0OOO0O0O))
        with contextlib.suppress(Exception):
            O00000O0OOOO()

def O0OO0OO00OO0():
    O00O00000O0O = os.path.join(OO00OO0O00OO, f'botdb_{datetime.now():%Y%m%d_%H%M%S}.sqlite')
    with O0OOO0OOOO00:
        OO000OOOOO00 = sqlite3.connect(O00O00000O0O)
        try:
            O000OO00O0OO.backup(OO000OOOOO00)
        finally:
            OO000OOOOO00.close()
    O0000OOO00O0(O00000O0OOOO)
    OOOOO000O0OO = O00OOOO000OO(O00O00000O0O, os.path.basename(O00O00000O0O), O0OO0O00OOOO or OOO0O0O00000)
    return (O00O00000O0O, OOOOO000O0OO)

def O00OOOOO00O0(O00O0OOO000O):
    with contextlib.suppress(OSError):
        os.remove(O00O0OOO000O)
O00OOO00O000 = telebot.TeleBot(OOO00O0O0O00, parse_mode='HTML', threaded=True, num_threads=10)

def OO00O0OO0OOO(O00OOOOOOOO0, cb_data=None, url_link=None):
    return types.InlineKeyboardButton(text=O00OOOOOOOO0, callback_data=cb_data, url=url_link)

def OOOO0O0OOO0O(*O000O00O0O00):
    OOOO0OO000OO = types.InlineKeyboardMarkup()
    for O0OOO000O0O0 in O000O00O0O00:
        if O0OOO000O0O0:
            OOOO0OO000OO.row(*O0OOO000O0O0)
    return OOOO0OO000OO

def O0O0OO00O00O(O000OOO00000, OOOOO000OOOO, markup=None, reply_id=None):
    try:
        return O00OOO00O000.send_message(O000OOO00000, OOOOO000OOOO, reply_markup=markup, disable_web_page_preview=True, reply_to_message_id=reply_id)
    except ApiTelegramException as e:
        O0OOO0000OO0.warning('send_message(%s) failed: %s', O000OOO00000, e)
    except Exception:
        O0OOO0000OO0.exception('send_message(%s) crashed', O000OOO00000)
    return None

def OOO0O00O0OO0(O0OOO0OO0O0O, O0O0O0O0OO00):
    OOO0O0OO000O('UPDATE users SET panel_msg_id=? WHERE user_id=?', (int(O0O0O0O0OO00), int(O0OOO0OO0O0O)))

def OO0O00OOO0OO(O0OO00O000O0):
    O0O000O0000O = OO0OOOOO0OOO('SELECT panel_msg_id FROM users WHERE user_id=?', (int(O0OO00O000O0),))
    return int(O0O000O0000O['panel_msg_id']) if O0O000O0000O and O0O000O0000O.get('panel_msg_id') else None

def OO0OOOOOO000(O0000OO00OOO, O00O00O0OOO0, OOO00000OO0O, markup=None, force_new=False):
    O0O0OO000O00 = OO0O00OOO0OO(O0000OO00OOO)
    if O0O0OO000O00 and (not force_new):
        try:
            O00OOO00O000.edit_message_text(OOO00000OO0O, O00O00O0OOO0, O0O0OO000O00, reply_markup=markup, disable_web_page_preview=True)
            return O0O0OO000O00
        except ApiTelegramException as e:
            if 'message is not modified' in str(e).lower():
                return O0O0OO000O00
            with contextlib.suppress(Exception):
                O00OOO00O000.delete_message(O00O00O0OOO0, O0O0OO000O00)
    O00O000O00OO = O0O0OO00O00O(O00O00O0OOO0, OOO00000OO0O, markup)
    if O00O000O00OO:
        OOO0O00O0OO0(O0000OO00OOO, O00O000O00OO.message_id)
        return O00O000O00OO.message_id
    return None

def O000O0OOO0O0(OOOO0OOOO00O, O00O000O0000, markup=None):
    OOOO00OOOOOO = OOOO0OOOO00O.from_user.id
    O00OOO000OO0 = OOOO0OOOO00O.message.chat.id
    OOO00OO00O0O = OOOO0OOOO00O.message.message_id
    try:
        O00OOO00O000.edit_message_text(O00O000O0000, O00OOO000OO0, OOO00OO00O0O, reply_markup=markup, disable_web_page_preview=True)
        OOO0O00O0OO0(OOOO00OOOOOO, OOO00OO00O0O)
    except ApiTelegramException as e:
        if 'message is not modified' in str(e).lower():
            return
        OO0OOOOOO000(OOOO00OOOOOO, O00OOO000OO0, O00O000O0000, markup, True)
    except Exception:
        O0OOO0000OO0.exception('show() failed')

def O000OO0OOO00(O0O0OOO0O0OO, text=None, alert=False):
    with contextlib.suppress(Exception):
        O00OOO00O000.answer_callback_query(O0O0OOO0O0OO.id, text, show_alert=alert)

def OO000O0O00O0(O0O0OO0O000O, markup=None):
    for O0O000O0O000 in OO0O0O00O0O0:
        O0O0OO00O00O(O0O000O0O000, O0O0OO0O000O, markup)

def OO00000O0OOO():
    return OOOOOO0O0O00('SELECT * FROM channels ORDER BY id')

def O0000O0OOOO0(OO00O0OOOO0O):
    OO00OOOO0O00 = []
    for O0O0OO0000OO in OO00000O0OOO():
        try:
            OO0OOOO0O0O0 = O00OOO00O000.get_chat_member(O0O0OO0000OO['chat_id'], OO00O0OOOO0O)
            OO0000O0O00O = OO0OOOO0O0O0.status in ('member', 'administrator', 'creator') or (OO0OOOO0O0O0.status == 'restricted' and getattr(OO0OOOO0O0O0, 'is_member', True))
            if not OO0000O0O00O:
                OO00OOOO0O00.append(O0O0OO0000OO)
        except Exception:
            pass
    return OO00OOOO0O00

def O00O0O000000(OOO0OOO0OOOO, OO00OOOO0OO0, O00O000O0O0O):
    if O00000OO00OO(OOO0OOO0OOOO):
        return True
    if O0000000O00O('maintenance', '0') == '1':
        OO0OOOOOO000(OOO0OOO0OOOO, OO00OOOO0OO0, '🛠 <b>البوت في وضع الصيانة حالياً، حاول لاحقاً.</b>')
        return False
    if O00O000O0O0O and O00O000O0O0O.get('banned'):
        OO0OOOOOO000(OOO0OOO0OOOO, OO00OOOO0OO0, '🚫 <b>تم حظرك من استخدام البوت.</b>')
        return False
    OOOO0000OO00 = O0000O0OOOO0(OOO0OOO0OOOO)
    if OOOO0000OO00:
        O000O00OO0OO = []
        for OO0OO00000O0 in OOOO0000OO00:
            if OO0OO00000O0.get('link'):
                O000O00OO0OO.append([OO00O0OO0OOO(f"📢 {OO0OO00000O0['title'] or 'قناة البوت'}", None, OO0OO00000O0['link'])])
        O000O00OO0OO.append([OO00O0OO0OOO('✅ تحققت من اشتراكي', 'u:chk')])
        OO0OOOOOO000(OOO0OOO0OOOO, OO00OOOO0OO0, '📢 <b>الاشتراك الإجباري</b>\n━━━━━━━━━━━━━━\nللاستفادة من البوت يجب الاشتراك في القنوات التالية أولاً، ثم اضغط <b>تحققت من اشتراكي</b> 👇', OOOO0O0OOO0O(*O000O00OO0OO))
        return False
    return True
CRITICAL_REGEX = [('\\brm\\s+-[a-zA-Z]*[rR][a-zA-Z]*\\s+[\'\\"]?(/|~|\\*|\\$HOME)', 'أمر حذف خطير (rm -rf)'), (':\\(\\)\\s*\\{\\s*:\\s*\\|\\s*:\\s*&\\s*\\}\\s*;\\s*:', 'Fork Bomb'), ('\\bdd\\s+if=', 'أمر dd خطير'), ('\\bmkfs(\\.\\w+)?\\b', 'تهيئة أقراص (mkfs)'), ('\\b(shutdown|reboot|poweroff|halt)\\b\\s*(-[a-zA-Z]+|now)', 'إيقاف/إعادة تشغيل السيرفر'), ('\\b(nc|ncat|netcat)\\b[^\\n]{0,40}\\s-[a-z]*e\\b', 'Reverse Shell (netcat)'), ('/dev/tcp/', 'Reverse Shell (/dev/tcp)'), ('/etc/(passwd|shadow|sudoers)', 'الوصول لملفات النظام الحساسة'), ('stratum\\+tcp|xmrig|minerd|cpuminer', 'تعدين عملات')]
ALLOWED_PIP = {'telebot': 'pyTelegramBotAPI', 'telegram': 'python-telegram-bot', 'aiogram': 'aiogram', 'telethon': 'telethon', 'pyrogram': 'pyrogram', 'tgcrypto': 'tgcrypto', 'requests': 'requests', 'httpx': 'httpx', 'aiohttp': 'aiohttp', 'bs4': 'beautifulsoup4', 'lxml': 'lxml', 'flask': 'flask', 'PIL': 'pillow', 'numpy': 'numpy', 'pandas': 'pandas', 'yaml': 'pyyaml', 'dotenv': 'python-dotenv', 'pymongo': 'pymongo', 'psutil': 'psutil', 'openpyxl': 'openpyxl', 'schedule': 'schedule', 'yt_dlp': 'yt-dlp', 'cryptography': 'cryptography', 'redis': 'redis', 'arabic_reshaper': 'arabic-reshaper', 'bidi': 'python-bidi', 'pytz': 'pytz', 'dateutil': 'python-dateutil', 'tqdm': 'tqdm', 'colorama': 'colorama', 'qrcode': 'qrcode', 'gtts': 'gTTS', 'deep_translator': 'deep-translator', 'fake_useragent': 'fake-useragent'}
O0OOO000000O = set(getattr(sys, 'stdlib_module_names', ())) | {'__future__'}

def OOO00O0OO000(OOOOOO000OOO):
    try:
        O0OO0OO0OO0O = [OOOOO000OOO0 for OOOOO000OOO0 in tokenize.generate_tokens(io.StringIO(OOOOOO000OOO).readline) if OOOOO000OOO0.type != tokenize.COMMENT]
        return tokenize.untokenize(O0OO0OO0OO0O)
    except Exception:
        return OOOOOO000OOO

def OOOO00O00O00(OO000OOO00OO, O0OO000OO0O0):
    O000OO0OO00O = {'ok': True, 'critical': [], 'warnings': [], 'imports': [], 'syntax_error': None}
    try:
        with open(OO000OOO00OO, 'rb') as O00O0OOO0000:
            OOO0O00OOOOO = O00O0OOO0000.read()
        if b'\x00' in OOO0O00OOOOO:
            O000OO0OO00O.update(ok=False, critical=['الملف ثنائي/مشفّر وليس نص بايثون'])
            return O000OO0OO00O
        O00000O00OO0 = OOO0O00OOOOO.decode('utf-8', errors='replace')
        try:
            O0OOOO000O0O = ast.parse(O00000O00OO0)
        except SyntaxError as e:
            O000OO0OO00O.update(ok=False, syntax_error=f'سطر {e.lineno}: {e.msg}')
            return O000OO0OO00O
        OO0O00OOOO00 = set()
        OOO00O00O0OO = []
        OOO0O0OO00O0 = []
        for OO0000OO000O in ast.walk(O0OOOO000O0O):
            if isinstance(OO0000OO000O, ast.Import):
                for O0O0O000O000 in OO0000OO000O.names:
                    OO0O00OOOO00.add(O0O0O000O000.name.split('.')[0])
            elif isinstance(OO0000OO000O, ast.ImportFrom):
                if OO0000OO000O.level == 0 and OO0000OO000O.module:
                    OO0O00OOOO00.add(OO0000OO000O.module.split('.')[0])
        O000OO0OO00O['imports'] = sorted(OO0O00OOOO00)
        O000OO0OO00O['warnings'] = OOO00O00O0OO
        if O00000OO00OO(O0OO000OO0O0) or not OOO00OOOO0OO():
            return O000OO0OO00O
        O0OO0OOO0OOO = OOO00O0OO000(O00000O00OO0)
        for OOO0O0OOOOO0, O0O0000OOO0O in CRITICAL_REGEX:
            if re.search(OOO0O0OOOOO0, O0OO0OOO0OOO, re.IGNORECASE):
                if O0O0000OOO0O not in OOO0O0OO00O0:
                    OOO0O0OO00O0.append(O0O0000OOO0O)
        if OOO0O0OO00O0:
            O000OO0OO00O.update(ok=False, critical=OOO0O0OO00O0)
        return O000OO0OO00O
    except Exception as e:
        O000OO0OO00O.update(ok=False, critical=[f'تعذّر فحص الملف: {e}'])
        return O000OO0OO00O
PUBLISH_POLL_SECONDS = 3.0
O00O0O0O0O00 = threading.RLock()
OOO000O000OO = threading.Event()
_main_file_locks = {}
O0000O00O0O0 = threading.Lock()

def OO0OO000O00O(O00OO0O00000):
    with O0000O00O0O0:
        return _main_file_locks.setdefault(int(O00OO0O00000), threading.RLock())

def OOO00O00OOOO():
    OOO000O000OO.set()

def O0OO0O0O0OO0(OOO00OOO0O0O):
    O0OO0OO0OO00 = os.path.join(O0O0OOO0OOO0, str(int(OOO00OOO0O0O)))
    os.makedirs(O0OO0OO0OO00, exist_ok=True)
    return O0OO0OO0OO00

def O0OOOOOOO0OO(OOOOOOO000O0, OO00OOO0000O):
    return os.path.join(OO0OOO00OO0O, f'userdata_{int(OOOOOOO000O0)}_{int(OO00OOO0000O)}.zip')

def OOO0O0OOO000(OOOO00O00OOO, OO0OOOO0OOO0, O000OO00OO0O):
    O0OOO0000O00 = []
    os.makedirs(os.path.dirname(os.path.abspath(O000OO00OO0O)), exist_ok=True)
    if zipfile.is_zipfile(OOOO00O00OOO):
        try:
            with zipfile.ZipFile(OOOO00O00OOO, 'r') as OOOOOO0O00OO, zipfile.ZipFile(O000OO00OO0O, 'w', zipfile.ZIP_DEFLATED) as OO0O0OOOO0O0:
                O0O000OOO00O = 0
                for O00OOO0O0000 in OOOOOO0O00OO.infolist():
                    if O00OOO0O0000.is_dir():
                        continue
                    OO0OOOOOOOOO = O00OOO0O0000.filename.replace('\\', '/').lstrip('/')
                    O00O00O00O0O = [OOO0O0000OO0 for OOO0O0000OO0 in OO0OOOOOOOOO.split('/') if OOO0O0000OO0 and OOO0O0000OO0 not in ('.', '..')]
                    if not O00O00O00O0O:
                        continue
                    O00OO00OOO00 = '/'.join(O00O00O00O0O)
                    if O00OO00OOO00.lower().endswith('.py') and O00OO00OOO00.startswith('run_'):
                        continue
                    O0O000OOO00O += O00OOO0O0000.file_size
                    if O0O000OOO00O > 120 * 1024 * 1024:
                        return (False, 'حجم البيانات كبير جداً.', [])
                    O00OO0O0O0OO = OOOOOO0O00OO.read(O00OOO0O0000.filename)
                    OO0O0OOOO0O0.writestr(O00OO00OOO00, O00OO0O0O0OO)
                    O0OOO0000O00.append(O00OO00OOO00)
                    if len(O00O00O00O0O) > 1 and O00O00O00O0O[-1] not in O0OOO0000O00:
                        OO0O0OOOO0O0.writestr(O00O00O00O0O[-1], O00OO0O0O0OO)
                        O0OOO0000O00.append(O00O00O00O0O[-1])
            if not O0OOO0000O00:
                return (False, 'ملف الـ ZIP فارغ.', [])
            return (True, f'تم استيعاب أرشيف البيانات ({len(O0OOO0000O00)} ملف).', O0OOO0000O00)
        except Exception as e:
            return (False, f'ملف الـ ZIP غير صالح: {e}', [])
    else:
        O00O000O00O0 = O00O0O00OOO0(OO0OOOO0OOO0)
        try:
            with zipfile.ZipFile(O000OO00OO0O, 'w', zipfile.ZIP_DEFLATED) as OO0O0OOOO0O0:
                OO0O0OOOO0O0.write(OOOO00O00OOO, arcname=O00O000O00O0)
            return (True, f'تم تجهيز ملف البيانات ({O00O000O00O0}).', [O00O000O00O0])
        except Exception as e:
            return (False, f'تعذّر حزم ملف البيانات: {e}', [])

def OO0OO00O000O(O0O0OOO0O000, O0O0OO0O0OOO, OO0O000OOOO0):
    if not os.path.isfile(OO0O000OOOO0):
        return (None, None)
    OOOO0OOOOO0O = None
    for OO0OO0OO0O00 in O0O00O0OOOOO(O0O0OOO0O000, O0O0OO0O0OOO):
        OOOOOO000000(OO0OO0OO0O00)
        O00OO00000OO = O00OOOO000OO(OO0O000OOOO0, OO0OO0OO0O00, OOO0O0O00000)
        if O00OO00000OO and (not OOOO0OOOOO0O):
            OOOO0OOOOO0O = O00OO00000OO
    O0O0O0O0O0O0 = None
    if O0OO0O00OOOO:
        OOO0OOO0O00O = f'bk_w{O000O00OO00O(O0O0OOO0O000)}_udata_{int(O0O0OOO0O000)}_{int(O0O0OO0O0OOO)}.zip'
        OOOOOO000000(OOO0OOO0O00O, O0OO0O00OOOO)
        O0O0O0O0O0O0 = O00OOOO000OO(OO0O000OOOO0, OOO0OOO0O00O, O0OO0O00OOOO)
    OOO0O0OO000O('UPDATE files SET data_pd_id=?, data_backup_pd_id=? WHERE id=?', (OOOO0OOOOO0O, O0O0O0O0O0O0, int(O0O0OOO0O000)))
    return (OOOO0OOOOO0O, O0O0O0O0O0O0)

def O0O000000000(OO0OO0O0OOOO, O00OO0OO0OO0, wait=25.0):
    OO0OO0O0OOOO, O00OO0OO0OO0 = (int(OO0OO0O0OOOO), int(O00OO0OO0OO0))
    O0OOOO0O0O0O = f'ubackup_{OO0OO0O0OOOO}_{O00OO0OO0OO0}.zip'
    OOOOOO00OO00 = f'ubackupreq_{OO0OO0O0OOOO}_{O00OO0OO0OO0}.txt'
    OOOO0O0OO0OO = os.path.join(OOOO00OOO00O, f'backup_{OO0OO0O0OOOO}_{O00OO0OO0OO0}_{int(time.time())}.zip')
    try:
        OOOOOO000000(O0OOOO0O0O0O)
        O0O00O0000O0 = OO00OOO000OO(b'1', OOOOOO00OO00)
        if not O0O00O0000O0:
            return None
        OOO00O00000O = time.time() + wait
        while time.time() < OOO00O00000O:
            time.sleep(1.5)
            try:
                OOO0O0000OOO = [OOOO000OO000 for OOOO000OO000 in O000O0O0O000() if OOOO000OO000['name'] == O0OOOO0O0O0O]
            except Exception:
                OOO0O0000OOO = []
            if OOO0O0000OOO:
                OO000O00OOO0 = max(OOO0O0000OOO, key=lambda it: str(it.get('date_upload') or ''))
                if O000O000OO0O(str(OO000O00OOO0['id']), OOOO0O0OO0OO):
                    for OOO000O0OO0O in OOO0O0000OOO:
                        OOOO0O0OOO00(str(OOO000O0OO0O['id']))
                    OOOOOOO00O00 = O0OOOOOOO0OO(OO0OO0O0OOOO, O00OO0OO0OO0)
                    with contextlib.suppress(OSError):
                        shutil.copy2(OOOO0O0OO0OO, OOOOOOO00O00)
                    return OOOO0O0OO0OO
        OOOO0O0OOO00(O0O00O0000O0)
        for O0OO00OO00OO in O0O00O0OOOOO(OO0OO0O0OOOO, O00OO0OO0OO0):
            with contextlib.suppress(Exception):
                OOO0O0000OOO = [OOOOOO0OO0O0 for OOOOOO0OO0O0 in O000O0O0O000() if OOOOOO0OO0O0['name'] == O0OO00OO00OO]
                if OOO0O0000OOO:
                    O0OOO00OO00O = max(OOO0O0000OOO, key=lambda it: str(OOO000O0OO0O.get('date_upload') or ''))
                    if O000O000OO0O(str(O0OOO00OO00O['id']), OOOO0O0OO0OO):
                        return OOOO0O0OO0OO
        OOOOOOO00O00 = O0OOOOOOO0OO(OO0OO0O0OOOO, O00OO0OO0OO0)
        if os.path.isfile(OOOOOOO00O00) and os.path.getsize(OOOOOOO00O00) > 0:
            shutil.copy2(OOOOOOO00O00, OOOO0O0OO0OO)
            return OOOO0O0OO0OO
        return None
    except Exception:
        return None

def O0O000OO0000(OO0O0O0OOOOO, uid=None):
    if isinstance(OO0O0O0OOOOO, dict):
        return f"run_{int(OO0O0O0OOOOO['id'])}_{int(OO0O0O0OOOOO['user_id'])}.py"
    return f'run_{int(OO0O0O0OOOOO)}_{int(uid)}.py'

def OO00OOO00OO0(OOO0O0000O0O):
    OO0OOOOOOO00 = O0OOO0O00O0O(OOO0O0000O0O)
    return bool(OO0OOOOOOO00 and OO0OOOOOOO00.get('status') == 'approved' and (int(OO0OOOOOOO00.get('desired_run') or 0) == 1))

def OO0O0000O0OO(O0OO0OOO00O0):
    if not O0OO0OOO00O0:
        return False
    OOO0OOOO000O = int(O0OO0OOO00O0['id'])
    with OO0OO000O00O(OOO0OOOO000O):
        O0OO0O00O000 = O0OO0OOO00O0.get('path') or os.path.join(O0OO0O0O0OO0(O0OO0OOO00O0['user_id']), O0OO0O00000O(O0OO0OOO00O0['file_name']))
        if os.path.isfile(O0OO0O00O000) and os.path.getsize(O0OO0O00O000) > 0:
            O0OO0OOO00O0['path'] = O0OO0O00O000
            return True
        O0O000OO0OOO = OO0OOOOO0OOO('SELECT content, pd_id, backup_pd_id FROM files WHERE id=?', (OOO0OOOO000O,))
        if O0O000OO0OOO and O0O000OO0OOO.get('content'):
            os.makedirs(os.path.dirname(os.path.abspath(O0OO0O00O000)), exist_ok=True)
            with open(O0OO0O00O000, 'wb') as O0OO0OOOOOO0:
                O0OO0OOOOOO0.write(O0O000OO0OOO['content'])
            OOO0O0OO000O('UPDATE files SET path=? WHERE id=?', (O0OO0O00O000, OOO0OOOO000O))
            O0OO0OOO00O0['path'] = O0OO0O00O000
            return True
        OO00OO0OOO0O = O0O000OO0OOO and O0O000OO0OOO.get('pd_id') or O0OO0OOO00O0.get('pd_id')
        if OO00OO0OOO0O and O000O000OO0O(str(OO00OO0OOO0O), O0OO0O00O000):
            with contextlib.suppress(OSError):
                with open(O0OO0O00O000, 'rb') as O0OO0OOOOOO0:
                    OOO0O0OO000O('UPDATE files SET path=?, content=? WHERE id=?', (O0OO0O00O000, sqlite3.Binary(O0OO0OOOOOO0.read()), OOO0OOOO000O))
            O0OO0OOO00O0['path'] = O0OO0O00O000
            return True
        O0O0000O0O00 = O0O000OO0OOO and O0O000OO0OOO.get('backup_pd_id') or O0OO0OOO00O0.get('backup_pd_id')
        if O0O0000O0O00 and O000O000OO0O(str(O0O0000O0O00), O0OO0O00O000, O0OO0O00OOOO):
            with contextlib.suppress(OSError):
                with open(O0OO0O00O000, 'rb') as O0OO0OOOOOO0:
                    OOO0O0OO000O('UPDATE files SET path=?, content=? WHERE id=?', (O0OO0O00O000, sqlite3.Binary(O0OO0OOOOOO0.read()), OOO0OOOO000O))
            O0OO0OOO00O0['path'] = O0OO0O00O000
            return True
        return False

def OO00OOO000OO(OO0O0000O0O0, O0000O00O00O, api_key=None):
    O0O00OO00000 = os.path.join(OOOO00OOO00O, f'tmp_{uuid.uuid4().hex}')
    try:
        with open(O0O00OO00000, 'wb') as OO0O0000OOOO:
            OO0O0000OOOO.write(OO0O0000O0O0)
        return O00OOOO000OO(O0O00OO00000, O0000O00O00O, api_key)
    finally:
        with contextlib.suppress(OSError):
            os.remove(O0O00OO00000)

def O000000O0OO0(O00O00OO0O0O, delete_after=False):
    try:
        O0O0O0OOO0OO = [OO0000O0OO00 for OO0000O0OO00 in O000O0O0O000() if OO0000O0OO00['name'] == O00O00OO0O0O]
    except Exception:
        return None
    if not O0O0O0OOO0OO:
        return None
    OO00O0O000O0 = max(O0O0O0OOO0OO, key=lambda it: str(it.get('date_upload') or ''))
    OOOOO0O0000O = os.path.join(OOOO00OOO00O, f'tmp_{uuid.uuid4().hex}')
    try:
        if not O000O000OO0O(str(OO00O0O000O0['id']), OOOOO0O0000O):
            return None
        with open(OOOOO0O0000O, 'rb') as OOOO0OOOO000:
            OO0OOOO00OOO = OOOO0OOOO000.read(2 * 1024 * 1024).decode('utf-8', errors='replace')
        if delete_after:
            for O0O0O0O0OOO0 in O0O0O0OOO0OO:
                OOOO0O0OOO00(str(O0O0O0O0OOO0['id']))
        return OO0OOOO00OOO
    finally:
        with contextlib.suppress(OSError):
            os.remove(OOOOO0O0000O)

def O0OOO000OO0O(OO000O000O00, OOO0O00O00OO):
    O0O000OOO0O0 = f'autorestart_{int(OO000O000O00)}.txt'
    if OOO0O00O00OO:
        OOOOOO000000(O0O000OOO0O0)
        OO00OOO000OO(b'1', O0O000OOO0O0)
    else:
        OOOOOO000000(O0O000OOO0O0)

def OO00OOOOO00O(O0O0O00O0000, force_reupload=False):
    with O00O0O0O0O00, OO0OO000O00O(O0O0O00O0000):
        OO00O0OOOOOO = O0OOO0O00O0O(O0O0O00O0000)
        if not OO00O0OOOOOO:
            return (False, 'الملف غير موجود.')
        if OO00O0OOOOOO.get('status') != 'approved':
            return (False, 'الملف غير معتمد بعد.')
        if not OO0O0000O0OO(OO00O0OOOOOO):
            return (False, 'تعذّر العثور على أصل الملف.')
        if not OO00O0OOOOOO.get('backup_pd_id') and O0OO0O00OOOO:
            O0OO0O000OO0 = OOOOO0OOO0OO(OO00O0OOOOOO['path'], O0O0O00O0000, OO00O0OOOOOO['user_id'], OO00O0OOOOOO['file_name'])
            if O0OO0O000OO0:
                OOO0O0OO000O('UPDATE files SET backup_pd_id=? WHERE id=?', (O0OO0O000OO0, O0O0O00O0000))
        O0OOOOO00O0O = O0OOOOOOO0OO(O0O0O00O0000, OO00O0OOOOOO['user_id'])
        if os.path.isfile(O0OOOOO00O0O) and (force_reupload or not OO00O0OOOOOO.get('data_pd_id')):
            OO0OO00O000O(O0O0O00O0000, OO00O0OOOOOO['user_id'], O0OOOOO00O0O)
        O0O00O0OOO00 = O0O000OO0000(OO00O0OOOOOO)
        O0000OO0O0OO = OO00O0OOOOOO.get('pd_id')
        if O0000OO0O0OO and (not force_reupload) and (O0OO0OOO0O00(O0000OO0O0OO) is True):
            OOO0O0OO000O('UPDATE files SET desired_run=1, pid=NULL WHERE id=?', (O0O0O00O0000,))
            return (True, 'الملف يعمل حالياً على الخادم.')
        if O0000OO0O0OO:
            OOOO0O0OOO00(str(O0000OO0O0OO))
        OOOOOO000000(O0O00O0OOO00)
        OO0OOO0O00O0 = O00OOOO000OO(OO00O0OOOOOO['path'], O0O00O0OOO00)
        if not OO0OOO0O00O0:
            return (False, 'جاري إعادة المحاولة تلقائياً...')
        OOO0O0OO000O('UPDATE files SET desired_run=1, pd_id=?, pid=NULL, last_start=? WHERE id=?', (OO0OOO0O00O0, OOO0O00OOO00(), O0O0O00O0000))
        O0OOO000OO0O(O0O0O00O0000, bool(OO00O0OOOOOO.get('auto_restart', 1)))
        return (True, f'تم توجيه الملف للتشغيل على خادم العمل رقم ({O000O00OO00O(O0O0O00O0000)}).')

def O0000O0O000O(O0OOO0O0O000):
    with O00O0O0O0O00, OO0OO000O00O(O0OOO0O0O000):
        O00OO00O0OOO = O0OOO0O00O0O(O0OOO0O0O000)
        if not O00OO00O0OOO:
            return False
        O00OOO0OOOO0 = O0O000OO0000(O00OO00O0OOO)
        O0O000OOOO0O = O00OO00O0OOO.get('pd_id')
        OOO00OOO0O00 = True
        if O0O000OOOO0O and (not OOOO0O0OOO00(str(O0O000OOOO0O))):
            OOO00OOO0O00 = False
        if not OOOOOO000000(O00OOO0OOOO0):
            OOO00OOO0O00 = False
        if OOO00OOO0O00:
            OOO0O0OO000O('UPDATE files SET pd_id=NULL, pid=NULL WHERE id=?', (O0OOO0O0O000,))
        return OOO00OOO0O00

def O0000O0000OO(OOOO0OO0O0O0):
    O00OO0O0O00O = O0OOO0O00O0O(OOOO0OO0O0O0)
    if not O00OO0O0O00O:
        return (False, 'الملف غير موجود.')
    if O00OO0O0O00O.get('status') != 'approved':
        return (False, 'الملف لم تتم الموافقة عليه بعد.')
    O0O0OO000000 = O00OO0O00OOO(O00OO0O0O00O['user_id'])
    if O0O0OO000000 and O0O0OO000000.get('banned'):
        return (False, 'المستخدم محظور.')
    if O0000000O00O('maintenance', '0') == '1' and (not O00000OO00OO(O00OO0O0O00O['user_id'])):
        return (False, 'التشغيل متوقف مؤقتاً أثناء الصيانة.')
    OOO0O0OO000O("UPDATE files SET desired_run=1, pid=NULL WHERE id=? AND status='approved'", (OOOO0OO0O0O0,))
    OO000OO0OOOO, OOO00OOO0OO0 = OO00OOOOO00O(OOOO0OO0O0O0, True)
    OOO00O00OOOO()
    return (OO000OO0OOOO, OOO00OOO0OO0)

def OOO0O00O0O0O(O000O000OO00):
    OOO0000OO0OO = O0OOO0O00O0O(O000O000OO00)
    if not OOO0000OO0OO or OOO0000OO0OO.get('status') != 'approved':
        return (False, 'الملف غير موجود أو غير معتمد.')
    OOOO000000O0 = O00OO0O00OOO(OOO0000OO0OO['user_id'])
    if OOOO000000O0 and OOOO000000O0.get('banned'):
        return (False, 'المستخدم محظور.')
    OOO0O0OO000O("UPDATE files SET desired_run=1, pid=-1 WHERE id=? AND status='approved'", (O000O000OO00,))
    O00O0000000O, OOOOOO0OO000 = OO00OOOOO00O(O000O000OO00, True)
    OOO00O00OOOO()
    return (O00O0000000O, OOOOOO0OO000)

def OO0O0O000OOO(O00O0000OOO0):
    O000OOO0OO0O = O0OOO0O00O0O(O00O0000OOO0)
    if not O000OOO0OO0O:
        return False
    O000O0O00O00 = bool(int(O000OOO0OO0O.get('desired_run') or 0) or O000OOO0OO0O.get('pd_id'))
    OOO0O0OO000O('UPDATE files SET desired_run=0, pid=NULL WHERE id=?', (O00O0000OOO0,))
    O0000O0O000O(O00O0000OOO0)
    OOO00O00OOOO()
    return O000O0O00O00

def O00OOOOO00OO(OO00O00OO0O0):
    with O00O0O0O0O00, OO0OO000O00O(OO00O00OO0O0):
        OOO00O0OO00O = O0OOO0O00O0O(OO00O00OO0O0)
        if not OOO00O0OO00O:
            return
        O0O0OOOO0000 = O0O000OO0000(OOO00O0OO00O)
        if OOO00O0OO00O.get('pd_id'):
            OOOO0O0OOO00(str(OOO00O0OO00O['pd_id']))
        if OOO00O0OO00O.get('data_pd_id'):
            OOOO0O0OOO00(str(OOO00O0OO00O['data_pd_id']))
        OOOOOO000000(O0O0OOOO0000)
        for OO00000OOOOO in O0O00O0OOOOO(OO00O00OO0O0, OOO00O0OO00O['user_id']):
            OOOOOO000000(OO00000OOOOO)
        OOOOOO000000(f'dep_{int(OO00O00OO0O0)}.json')
        OOOOOO000000(f'autorestart_{int(OO00O00OO0O0)}.txt')
        if OOO00O0OO00O.get('path') and os.path.isfile(OOO00O0OO00O['path']):
            with contextlib.suppress(OSError):
                os.remove(OOO00O0OO00O['path'])
        O00OO0O00OO0 = O0OOOOOOO0OO(OO00O00OO0O0, OOO00O0OO00O['user_id'])
        if os.path.isfile(O00OO0O00OO0):
            with contextlib.suppress(OSError):
                os.remove(O00OO0O00OO0)
        OOO0O0OO000O('DELETE FROM files WHERE id=?', (int(OO00O00OO0O0),))
    OOO00O00OOOO()

def O00O0O000O0O():
    for OOO0O0OOOO00 in OOOOOO0O0O00("SELECT * FROM library_requests WHERE status='approved' ORDER BY id LIMIT 10"):
        O0OOOO00O0OO, O00000OO00O0 = (int(OOO0O0OOOO00['id']), int(OOO0O0OOOO00['user_id']))
        O00OO0OO000O = O00OO0O00OOO(O00000OO00O0)
        if O00OO0OO000O and O00OO0OO000O.get('banned'):
            OOO0O0OO000O("UPDATE library_requests SET status='rejected',result='banned' WHERE id=?", (O0OOOO00O0OO,))
            continue
        OO000000O000 = str(OOO0O0OOOO00['packages']).encode('utf-8')
        O000OOOO0OOO = OO00OOO000OO(OO000000O000, f'lib_w1_{O0OOOO00O0OO}_{O00000OO00O0}.txt')
        O00000OOOOO0 = OO00OOO000OO(OO000000O000, f'lib_w2_{O0OOOO00O0OO}_{O00000OO00O0}.txt')
        if O000OOOO0OOO or O00000OOOOO0:
            OOO0O0OO000O("UPDATE library_requests SET status='sent' WHERE id=? AND status='approved'", (O0OOOO00O0OO,))

def OOOOO00OOO0O(O0O0OO0O0O00):
    O0OOO0O000OO = O0000000O00O('auto_libs', '1') != '1'
    O00OOO00O0O0 = 'flag_noautolibs.txt' in O0O0OO0O0O00
    if O0OOO0O000OO and (not O00OOO00O0O0):
        OO00OOO000OO(b'1', 'flag_noautolibs.txt')
    elif not O0OOO0O000OO and O00OOO00O0O0:
        for O0OO0000O00O in O0O0OO0O0O00['flag_noautolibs.txt']:
            OOOO0O0OOO00(str(O0OO0000O00O['id']))

def O0OO00O00000():
    with O00O0O0O0O00:
        O0OOOO00OOOO = O000O0O0O000()
        OO00OO0O0OO0 = {}
        for O0OOOOOO0O0O in O0OOOO00OOOO:
            OO00OO0O0OO0.setdefault(O0OOOOOO0O0O['name'], []).append(O0OOOOOO0O0O)
        O00O0OOOO0OO = {str(OO00OOO0OO00['id']) for OO00OOO0OO00 in O0OOOO00OOOO}
        O0O00OO0000O = {int(O00O0OO000O0['user_id']) for O00O0OO000O0 in OOOOOO0O0O00('SELECT user_id FROM users WHERE banned=1')}
        O00000OOO000 = O0000000O00O('maintenance', '0') == '1'
        OO00O0O00OOO = OOOOOO0O0O00(f'SELECT {_SELECT_FILE_COLS} FROM files')
        OOOO0OO0OOO0 = set()
        for OOO00O00OO0O in OO00O0O00OOO:
            OO0O00000O00 = int(OOO00O00OO0O['id'])
            OO0O0O0O00OO = int(OOO00O00OO0O['user_id'])
            OOO0OOOOO0O0 = OOO00O00OO0O.get('status') == 'approved' and int(OOO00O00OO0O.get('desired_run') or 0) == 1 and (OO0O0O0O00OO not in O0O00OO0000O) and (not (O00000OOO000 and (not O00000OO00OO(OO0O0O0O00OO))))
            OOOOO0OOO00O = str(OOO00O00OO0O['pd_id']) if OOO00O00OO0O.get('pd_id') else None
            O0OO0O0O0000 = int(OOO00O00OO0O.get('pid') or 0) == -1
            if OOO0OOOOO0O0:
                if O0OO0O0O0000 or not OOOOO0OOO00O or (OOOOO0OOO00O not in O00O0OOOO0OO and O0OO0OOO0O00(OOOOO0OOO00O) is False):
                    O0OO0OOOOOOO, O00000000OO0 = OO00OOOOO00O(OO0O00000O00, True)
                    if O0OO0OOOOOOO:
                        OOO0O0O00O0O = O0OOO0O00O0O(OO0O00000O00)
                        if OOO0O0O00O0O and OOO0O0O00O0O.get('pd_id'):
                            OOOO0OO0OOO0.add(str(OOO0O0O00O0O['pd_id']))
                else:
                    OOOO0OO0OOO0.add(OOOOO0OOO00O)
            elif OOOOO0OOO00O:
                O0000O0O000O(OO0O00000O00)
        for O0OOOOOO0O0O in O0OOOO00OOOO:
            O0OO000OOO00 = O0000OOOOOO0.match(O0OOOOOO0O0O['name'])
            if not O0OO000OOO00:
                continue
            OOOO00O0O0OO = str(O0OOOOOO0O0O['id'])
            if OOOO00O0O0OO not in OOOO0OO0OOO0:
                OOOO0O0OOO00(OOOO00O0O0OO)
        O00O0O000O0O()
        OOOOO00OOO0O(OO00OO0O0OO0)

def O0O0O00O00O0():
    while True:
        try:
            O0OO00O00000()
        except requests.RequestException as e:
            O0OOO0000OO0.warning('Primary cloud unreachable: %s', e)
        except Exception:
            O0OOO0000OO0.exception('publisher cycle failed')
        OOO000O000OO.wait(PUBLISH_POLL_SECONDS)
        OOO000O000OO.clear()
_hb_cache = [0.0, {'w1': None, 'w2': None}]

def O0OO000O000O():
    if time.time() - _hb_cache[0] < 8:
        return _hb_cache[1]
    OO000OO0O000 = {'w1': None, 'w2': None}
    try:
        O0000O0O0OOO = time.time()
        for OOO0O00OOOO0 in O000O0O0O000():
            OO00OOOOOO0O = OOO0O00OOOO0['name']
            if OO00OOOOOO0O.startswith('hb_w1') or OO00OOOOOO0O.startswith('hb_worker_1'):
                OOOO00OO0O00 = datetime.fromisoformat(str(OOO0O00OOOO0.get('date_upload')).replace('Z', '+00:00')).timestamp()
                OOOO000000OO = max(0.0, O0000O0O0OOO - OOOO00OO0O00)
                if OO000OO0O000['w1'] is None or OOOO000000OO < OO000OO0O000['w1']:
                    OO000OO0O000['w1'] = OOOO000000OO
            elif OO00OOOOOO0O.startswith('hb_w2') or OO00OOOOOO0O.startswith('hb_worker_2'):
                OOOO00OO0O00 = datetime.fromisoformat(str(OOO0O00OOOO0.get('date_upload')).replace('Z', '+00:00')).timestamp()
                OOOO000000OO = max(0.0, O0000O0O0OOO - OOOO00OO0O00)
                if OO000OO0O000['w2'] is None or OOOO000000OO < OO000OO0O000['w2']:
                    OO000OO0O000['w2'] = OOOO000000OO
    except Exception:
        pass
    _hb_cache[0], _hb_cache[1] = (time.time(), OO000OO0O000)
    return OO000OO0O000

def OO0000O0O0O0(OO000OO0O00O, wait=20.0):
    OO000OO0O00O = int(OO000OO0O00O)
    O0OOO0000000, O0OO00O0OOOO = (f'log_{OO000OO0O00O}.txt', f'logreq_{OO000OO0O00O}.txt')
    try:
        OOOOOO000000(O0OOO0000000)
        O0OO00OO0OO0 = OO00OOO000OO(b'1', O0OO00O0OOOO)
        if not O0OO00OO0OO0:
            return None
        O00O0O0O0O0O = time.time() + wait
        while time.time() < O00O0O0O0O0O:
            time.sleep(1.5)
            O00O0O00OO00 = O000000O0OO0(O0OOO0000000, True)
            if O00O0O00OO00 is not None:
                return O00O0O00OO00
        OOOO0O0OOO00(O0OO00OO0OO0)
        return None
    except Exception:
        return None

def OO00OO0OO0OO(O0OOOO0000O0, wait=15.0):
    O0OOOO0000O0 = int(O0OOOO0000O0)
    O0OOOO00000O, O000O00OO000 = (f'stat_{O0OOOO0000O0}.json', f'statreq_{O0OOOO0000O0}.txt')
    try:
        OOOOOO000000(O0OOOO00000O)
        OO0000000OOO = OO00OOO000OO(b'1', O000O00OO000)
        if not OO0000000OOO:
            return None
        OO0OOO00OOO0 = time.time() + wait
        while time.time() < OO0OOO00OOO0:
            time.sleep(1.2)
            O0OOO0O0OO0O = O000000O0OO0(O0OOOO00000O, True)
            if O0OOO0O0OO0O is not None:
                return json.loads(O0OOO0O0OO0O)
        OOOO0O0OOO00(OO0000000OOO)
        return None
    except Exception:
        return None

def O00O0OO00O00(O000O0OO00OO):
    return bool(OO00OOO000OO(b'1', f'clearlog_{int(O000O0OO00OO)}.txt'))

def O00O0O0OO0O0(O00O000OO00O, O0OOO0OO0000):
    OOO0O0OO000O("UPDATE library_requests SET status='approved',decided_by=? WHERE id=? AND status='pending'", (int(O0OOO0OO0000), int(O00O000OO00O)))
    OOO00O00OOOO()

def O0O0OO0OOOOO(OOO00OO00OO0, OO0000000O0O):
    OOOO0OOOOO00 = O0OO0O00OO0O(OOO00OO00OO0)
    O0O0O000O0OO = O0OOO00OOOO0(OOO00OO00OO0)
    OO00OOOO00O0 = O000000O000O(OOO00OO00OO0)
    OO000OOO000O = f'👋 <b>أهلاً بك في بوت الاستضافة المزدوج</b> يا {OOO0O0O0O0OO(OO0000000O0O)}\n━━━━━━━━━━━━━━\n🚀 استضف ملفات البايثون الخاصة بك وشغّلها على مدار الساعة مع حفظ تلقائي للداتا كل ساعة.\n\n🗂 ملفاتك المستضافة: <b>{O0O0O000O0OO} / {OOOO0OOOOO00}</b>\n💾 مساحتك المتاحة: <b>{O0O0O00O000O(OO00OOOO00O0)} / {O0O0O00O000O(O0000OO0OO00)}</b>\n━━━━━━━━━━━━━━\n💡 يمكنك إرسال ملف <code>.py</code> مباشرة في أي وقت أو الاختيار من الأزرار 👇'
    OO00OO00O000 = [[OO00O0OO0OOO('📤 رفع ملف', 'u:up'), OO00O0OO0OOO('📁 ملفي', 'u:my')], [OO00O0OO0OOO('📊 حسابي', 'u:acc'), OO00O0OO0OOO('🏓 حالة الخوادم', 'u:ping')], [OO00O0OO0OOO('📚 مكتباتي', 'x:libs'), OO00O0OO0OOO('➕ تثبيت مكتبة', 'x:add')], [OO00O0OO0OOO('❓ المساعدة', 'u:help')]]
    if O0O0O000O00O:
        OO00OO00O000.append([OO00O0OO0OOO('💬 تواصل مع الإدارة', None, 'https://t.me/' + O0O0O000O00O.lstrip('@'))])
    if O00000OO00OO(OOO00OO00OO0):
        OO00OO00O000.append([OO00O0OO0OOO('👑 لوحة تحكم المالك', 'adm:home')])
    return (OO000OOO000O, OOOO0O0OOO0O(*OO00OO00O000))

def OOOOO0OO0OOO(OO00OOOOOOO0):
    O0O00O0OOO0O = O0OO0O00OO0O(OO00OOOOOOO0)
    return f'❓ <b>طريقة الاستخدام والمميزات</b>\n━━━━━━━━━━━━━━\n1️⃣ أرسل ملف <code>.py</code> مباشرة، وسيعرض عليك البوت خيار رفع ملف سجل الداتا (نسخة احتياطية) إن وجد.\n2️⃣ يتم توزيع الملفات تلقائياً بين <b>خادمي عمل مستقلين (Worker 1 & Worker 2)</b> مع إنقاذ تلقائي لو توقف أحدهما.\n3️⃣ يقوم النظام <b>برفع نسخة احتياطية من الداتا تلقائياً كل ساعة أونلاين</b> بحيث لا تضيع أي بيانات أبداً.\n4️⃣ من قسم <b>ملفي</b> يمكنك:\n   • ▶️ تشغيل / ⏹ إيقاف / 🔄 إعادة تشغيل الملف.\n   • 📦 <b>سحب نسخة احتياطية للداتا</b> أو 📤 <b>رفع واستعادة داتا</b>.\n\n📌 الحد الأقصى للملفات: <b>{O0O00O0OOO0O}</b> • المساحة: <b>{O0O0O00O000O(O0000OO0OO00)}</b>'

def O0OOO00O0O00(O0O00OO000OO):
    OOO0O000O0O0 = O000000O000O(O0O00OO000OO)
    OO0OOO00O00O = O0OOO00OOOO0(O0O00OO000OO)
    O0OOOOO00000 = O0OO0O00OO0O(O0O00OO000OO)
    O0O0O000OOOO = OO00000000OO(O0O00OO000OO)
    O00OO00O0OO0 = f'📊 <b>معلومات حسابي</b>\n━━━━━━━━━━━━━━\n🆔 المعرف: <code>{O0O00OO000OO}</code>\n🗂 الملفات المستضافة: <b>{OO0OOO00O00O}/{O0OOOOO00000}</b>' + (' • ⏳ لديك طلب قيد المراجعة' if O0O0O000OOOO else '') + f'\n💾 المساحة المستهلكة: <b>{O0O0O00O000O(OOO0O000O0O0)} / {O0O0O00O000O(O0000OO0OO00)}</b>\n{OOO0O0OO0OO0(OOO0O000O0O0, O0000OO0OO00)}'
    return (O00OO00O0OO0, OOOO0O0OOO0O([OO00O0OO0OOO('📁 ملفي', 'u:my'), OO00O0OO0OOO('📤 رفع ملف', 'u:up')], [OO00O0OO0OOO('🔙 رجوع للقائمة', 'u:menu')]))

def OOO0O0OO0O0O(OO0OO0O0OO00):
    if OO0OO0O0OO00['status'] == 'pending':
        return '⏳'
    if not OO00OOO00OO0(OO0OO0O0OO00['id']):
        return '🔴'
    if int(OO0OO0O0OO00.get('pid') or 0) == -1:
        return '🔄'
    return '🟢' if OO0OO0O0OO00.get('pd_id') else '🟡'

def O00000OOO0OO(OOO000O000O0):
    if OOO000O000O0['status'] == 'pending':
        return '⏳ بانتظار الموافقة'
    if not OO00OOO00OO0(OOO000O000O0['id']):
        return '🔴 متوقف'
    if int(OOO000O000O0.get('pid') or 0) == -1:
        return '🔄 جاري إعادة التشغيل...'
    if OOO000O000O0.get('pd_id'):
        return f"🟢 يعمل الآن (خادم العمل {O000O00OO00O(OOO000O000O0['id'])})"
    if O0000000O00O('maintenance', '0') == '1' and (not O00000OO00OO(OOO000O000O0['user_id'])):
        return '🛠 متوقف مؤقتاً للصيانة'
    return '🟡 جاري التجهيز للتشغيل...'

def OO0O00O0000O(O000OOOOO000, O0OO0OO00OOO, note=None):
    OO0000O0OOO0 = O0OOO0O00O0O(O000OOOOO000)
    if not OO0000O0OOO0:
        return None
    O00O0000OO0O = O00000OO00OO(O0OO0OO00OOO)
    OO0OOO000O00 = O00OO0O00OOO(OO0000O0OOO0['user_id'])
    OO00000O00OO = bool(OO0000O0OOO0.get('auto_restart', 1))
    O0OOO0OOO0O0 = bool(OO0000O0OOO0.get('data_pd_id') or os.path.isfile(O0OOOOOOO0OO(O000OOOOO000, OO0000O0OOO0['user_id'])))
    O0O00OOOO00O = O000O00OO00O(O000OOOOO000)
    OO00000O0000 = []
    if note:
        OO00000O0000 += [note, '━━━━━━━━━━━━━━']
    OO00000O0000 += [f"📁 <b>{('تفاصيل الملف' if O00O0000OO0O else 'إدارة ملفي المستضاف')}</b>", '━━━━━━━━━━━━━━', f"📄 اسم الملف: <code>{OOO0O0O0O0OO(OO0000O0OOO0['file_name'])}</code>", f"📦 الحجم: <b>{O0O0O00O000O(OO0000O0OOO0['size'])}</b>", f'🖥 خادم التشغيل المخصص: <b>Worker #{O0O00OOOO00O}</b>', f'📡 الحالة: <b>{O00000OOO0OO(OO0000O0OOO0)}</b>', f"🗄 سجل الداتا (مزامنة كل ساعة): <b>{('مربوط ومحفوظ أونلاين ✅' if O0OOO0OOO0O0 else 'تلقائي (يحفظ كل ساعة)')}</b>", f"🔁 التشغيل التلقائي عند التوقف: <b>{('مفعّل ✅' if OO00000O00OO else 'معطّل ❌')}</b>"]
    if OO0000O0OOO0['status'] == 'approved' and OO00OOO00OO0(O000OOOOO000) and OO0000O0OOO0.get('pd_id') and OO0000O0OOO0.get('last_start'):
        with contextlib.suppress(ValueError):
            O0O000OOOOOO = (datetime.now() - datetime.strptime(OO0000O0OOO0['last_start'], '%Y-%m-%d %H:%M:%S')).total_seconds()
            OO00000O0000.append(f'⏱ مدة التشغيل: <b>{O0O0000OOOO0(O0O000OOOOOO)}</b>')
    if O00O0000OO0O:
        OO00000O0000 += ['━━━━━━━━━━━━━━', f'🔢 رقم الملف: <code>#{O000OOOOO000}</code> (خادم #{O0O00OOOO00O})', f'🏷 معرف التشغيل: <code>{O0O000OO0000(OO0000O0OOO0)}</code>', f"👤 المستخدم: {O0000O0O0000(OO0OOO000O00, OO0000O0OOO0['user_id'])} (<code>{OO0000O0OOO0['user_id']}</code>)", f"🕒 تاريخ الرفع: {OOO0O0O0O0OO(OO0000O0OOO0['uploaded_at'])}"]
    OO00OO000OO0 = []
    if OO0000O0OOO0['status'] == 'pending':
        if O00O0000OO0O:
            OO00OO000OO0.append([OO00O0OO0OOO('✅ موافقة وتشغيل', f'ap:y:{O000OOOOO000}'), OO00O0OO0OOO('❌ رفض وحذف', f'ap:n:{O000OOOOO000}')])
            OO00OO000OO0.append([OO00O0OO0OOO('🚫 رفض وحظر', f'ap:b:{O000OOOOO000}'), OO00O0OO0OOO('📥 سحب الملف', f'f:get:{O000OOOOO000}')])
            OO00OO000OO0.append([OO00O0OO0OOO('📦 سحب داتا المستخدم', f'f:dbk:{O000OOOOO000}'), OO00O0OO0OOO('📤 إرفاق/استعادة داتا', f'f:drest:{O000OOOOO000}')])
        else:
            OO00OO000OO0.append([OO00O0OO0OOO('📤 إرفاق/تحديث سجل الداتا', f'f:drest:{O000OOOOO000}')])
            OO00OO000OO0.append([OO00O0OO0OOO('📝 استبدال الملف', f'f:upd:{O000OOOOO000}'), OO00O0OO0OOO('🗑 إلغاء الطلب', f'f:dl:{O000OOOOO000}')])
    else:
        if OO00OOO00OO0(O000OOOOO000):
            OO00OO000OO0.append([OO00O0OO0OOO('⏹ إيقاف', f'f:sp:{O000OOOOO000}'), OO00O0OO0OOO('🔄 إعادة تشغيل', f'f:rs:{O000OOOOO000}')])
        else:
            OO00OO000OO0.append([OO00O0OO0OOO('▶️ تشغيل الآن', f'f:st:{O000OOOOO000}'), OO00O0OO0OOO('🔄 إعادة تشغيل', f'f:rs:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('📦 سحب نسخة احتياطية للداتا', f'f:dbk:{O000OOOOO000}'), OO00O0OO0OOO('📤 رفع واستعادة داتا', f'f:drest:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('📊 استهلاك الموارد', f'f:stat:{O000OOOOO000}'), OO00O0OO0OOO(f"🔁 تلقائي: {('ON ✅' if OO00000O00OO else 'OFF ❌')}", f'f:ar:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('📜 عرض السجل', f'f:lg:{O000OOOOO000}'), OO00O0OO0OOO('📥 السجل كملف', f'f:lgdoc:{O000OOOOO000}'), OO00O0OO0OOO('🧹 مسح السجل', f'f:lgclr:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('📝 تحديث الكود', f'f:upd:{O000OOOOO000}'), OO00O0OO0OOO('📥 تحميل ملفي', f'f:get:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('🔎 فحص المكتبات', f'x:diag:{O000OOOOO000}'), OO00O0OO0OOO('🛠 إصلاح المكتبات', f'x:fix:{O000OOOOO000}')])
        OO00OO000OO0.append([OO00O0OO0OOO('🗑 حذف الملف نهائياً', f'f:dl:{O000OOOOO000}')])
    if O00O0000OO0O:
        O00O0OO00O0O = OO00O0OO0OOO('✅ فك الحظر', f"adm:unban:{OO0000O0OOO0['user_id']}") if OO0OOO000O00 and OO0OOO000O00.get('banned') else OO00O0OO0OOO('🚫 حظر المستخدم', f"adm:ban:{OO0000O0OOO0['user_id']}")
        OO00OO000OO0.append([O00O0OO00O0O, OO00O0OO0OOO('📩 مراسلته', f"adm:msg:{OO0000O0OOO0['user_id']}")])
        OO00OO000OO0.append([OO00O0OO0OOO('🔙 قائمة الملفات', 'adm:files:0:0')])
    else:
        OO00OO000OO0.append([OO00O0OO0OOO('🔙 القائمة الرئيسية', 'u:menu')])
    return ('\n'.join(OO00000O0000), OOOO0O0OOO0O(*OO00OO000OO0))

def O0OOOO0OOO00():
    OO0OOOO0O0OO = datetime.now().strftime('%Y-%m-%d')
    return {'users': OO0OOOOO0OOO('SELECT COUNT(*) c FROM users')['c'], 'new': OO0OOOOO0OOO('SELECT COUNT(*) c FROM users WHERE joined_at LIKE ?', (OO0OOOO0O0OO + '%',))['c'], 'banned': OO0OOOOO0OOO('SELECT COUNT(*) c FROM users WHERE banned=1')['c'], 'files': OO0OOOOO0OOO('SELECT COUNT(*) c FROM files')['c'], 'approved': OO0OOOOO0OOO("SELECT COUNT(*) c FROM files WHERE status='approved'")['c'], 'pending': OO0OOOOO0OOO("SELECT COUNT(*) c FROM files WHERE status='pending'")['c'], 'running': OO0OOOOO0OOO("SELECT COUNT(*) c FROM files WHERE status='approved' AND desired_run=1")['c'], 'bytes': OO0OOOOO0OOO('SELECT COALESCE(SUM(size),0) s FROM files')['s']}

def OOOO0O0O00O0():
    OO0OOO0O000O = O0OOOO0OOO00()
    OO0O00O0O000 = O0OO000O000O()
    OOOO000O0OOO = '🟢 متصل' if OO0O00O0O000['w1'] is not None and OO0O00O0O000['w1'] < 120 else '⚠️ غير متصل (السيرفر 2 ينوب عنه تلقائياً)'
    O0OO0O0OOOO0 = '🟢 متصل' if OO0O00O0O000['w2'] is not None and OO0O00O0O000['w2'] < 120 else '⚠️ غير متصل (السيرفر 1 ينوب عنه تلقائياً)'
    OOOOO0OOOO0O = f"👑 <b>لوحة تحكم المالك</b>\n━━━━━━━━━━━━━━\n👥 المستخدمون: <b>{OO0OOO0O000O['users']}</b>  (🆕 اليوم {OO0OOO0O000O['new']} • 🚫 محظور {OO0OOO0O000O['banned']})\n📂 الملفات: <b>{OO0OOO0O000O['files']}</b>  (🟢 نشط {OO0OOO0O000O['running']} • ⏳ بانتظار {OO0OOO0O000O['pending']})\n💾 المساحة المستخدمة: {O0O0O00O000O(OO0OOO0O000O['bytes'])}\n🖥 خادم العمل 1 (فردي): <b>{OOOO000O0OOO}</b>\n🖥 خادم العمل 2 (زوجي): <b>{O0OO0O0OOOO0}</b>\n⏱ مدة عمل البوت: {O0O0000OOOO0(time.time() - OOO000O00O0O)}\n━━━━━━━━━━━━━━\nاختر من الأزرار 👇"
    OOOOOOOO0O00 = f"📬 الطلبات ({OO0OOO0O000O['pending']})"
    OO0OOO0000OO = OOOO0O0OOO0O([OO00O0OO0OOO(OOOOOOOO0O00, 'adm:pend'), OO00O0OO0OOO('📂 كل الملفات', 'adm:files:0:0')], [OO00O0OO0OOO('👥 المستخدمون', 'adm:users:0'), OO00O0OO0OOO('📢 إذاعة للكل', 'adm:bc')], [OO00O0OO0OOO('📡 قنوات الاشتراك', 'adm:ch'), OO00O0OO0OOO('💾 حفظ ومزامنة الآن', 'adm:bk')], [OO00O0OO0OOO('📦 سحب كل البيانات', 'adm:full')], [OO00O0OO0OOO('⏹ إيقاف الكل', 'adm:stopall'), OO00O0OO0OOO('▶️ تشغيل الكل', 'adm:startall')], [OO00O0OO0OOO(f"🛡 الحماية: {('ON' if OOO00OOOO0OO() else 'OFF')}", 'adm:prot'), OO00O0OO0OOO('🛠 مكتبات لمستخدم', 'adm:pip')], [OO00O0OO0OOO('🧰 الإدارة المتقدمة', 'x:admin'), OO00O0OO0OOO('📦 طلبات المكتبات', 'x:requests')], [OO00O0OO0OOO('🔄 تحديث', 'adm:home'), OO00O0OO0OOO('🏠 واجهة المستخدم', 'u:menu')])
    return (OOOOO0OOOO0O, OO0OOO0000OO)

def O000OOO0O0O0(OOOO00O0O00O, OO000O000000, per=PAGE_SIZE):
    O00OOOO0OOOO = max(1, (len(OOOO00O0O00O) + per - 1) // per)
    OO000O000000 = max(0, min(OO000O000000, O00OOOO0OOOO - 1))
    return (OOOO00O0O00O[OO000O000000 * per:(OO000O000000 + 1) * per], OO000O000000, O00OOOO0OOOO)

def OOOOOOOO0OO0(OO00000O0O0O, O0O00000OO00, O0OOO00OO0OO, extra=''):
    O000O00000O0 = []
    if O0O00000OO00 > 0:
        O000O00000O0.append(OO00O0OO0OOO('◀️', f'{OO00000O0O0O}:{O0O00000OO00 - 1}{extra}'))
    O000O00000O0.append(OO00O0OO0OOO(f'{O0O00000OO00 + 1}/{O0OOO00OO0OO}', 'noop'))
    if O0O00000OO00 < O0OOO00OO0OO - 1:
        O000O00000O0.append(OO00O0OO0OOO('▶️', f'{OO00000O0O0O}:{O0O00000OO00 + 1}{extra}'))
    return O000O00000O0

def OOO0O000000O(page=0, uid_filter=0, only_pending=False):
    O00O0O0OO000, O0O0OO000OOO = (f'SELECT {_SELECT_FILE_COLS} FROM files', [])
    O0O0O000OOO0 = []
    if uid_filter:
        O0O0O000OOO0.append('user_id=?')
        O0O0OO000OOO.append(uid_filter)
    if only_pending:
        O0O0O000OOO0.append("status='pending'")
    if O0O0O000OOO0:
        O00O0O0OO000 += ' WHERE ' + ' AND '.join(O0O0O000OOO0)
    O00O0O0OO000 += ' ORDER BY id DESC'
    OOO00OO0OO0O, page, O0O000O00O00 = O000OOO0O0O0(OOOOOO0O0O00(O00O0O0OO000, tuple(O0O0OO000OOO)), page)
    OOOO0OOO00OO = '📬 <b>طلبات الموافقة</b>' if only_pending else '📂 <b>قائمة الملفات</b>'
    OOO0000OO0O0 = f'{OOOO0OOO00OO}\n━━━━━━━━━━━━━━\n' + ('لا توجد ملفات حالياً.' if not OOO00OO0OO0O else 'اضغط على ملف لإدارته 👇')
    O0OOOO0OO00O = []
    for OO000OOO0000 in OOO00OO0OO0O:
        O00OO00OOOOO = O00OO0O00OOO(OO000OOO0000['user_id'])
        O0OO00O00OO0 = O000O00OO00O(OO000OOO0000['id'])
        O0OOOO0OO00O.append([OO00O0OO0OOO(f"{OOO0O0OO0O0O(OO000OOO0000)} [W{O0OO00O00OO0}] {OO000OOO0000['file_name'][:20]} • {O0OOOOOOO0O0(O00OO00OOOOO)[:14]}", f"adm:file:{OO000OOO0000['id']}")])
    if not only_pending:
        O0OOOO0OO00O.append(OOOOOOOO0OO0('adm:files', page, O0O000O00O00, f':{uid_filter}'))
    O0OOOO0OO00O.append([OO00O0OO0OOO('🔙 لوحة التحكم', 'adm:home')])
    return (OOO0000OO0O0, OOOO0O0OOO0O(*O0OOOO0OO00O))

def OOO0OO000O0O(page=0):
    O00000OOOO00, page, O00O0O00O0OO = O000OOO0O0O0(OOOOOO0O0O00('SELECT * FROM users ORDER BY joined_at DESC'), page)
    O00OO0OO00O0 = '👥 <b>المستخدمون</b>\n━━━━━━━━━━━━━━\n' + ('لا يوجد مستخدمون.' if not O00000OOOO00 else 'اضغط على مستخدم لإدارته 👇')
    OOOO00OO000O = []
    for OO0OO000O000 in O00000OOOO00:
        OOO00OOO0OOO = '🚫' if OO0OO000O000['banned'] else '👤'
        OOOO00OO000O.append([OO00O0OO0OOO(f"{OOO00OOO0OOO} {OO0OO000O000['first_name'][:18] or OO0OO000O000['user_id']} • {OO0OO000O000['user_id']}", f"adm:user:{OO0OO000O000['user_id']}")])
    OOOO00OO000O.append(OOOOOOOO0OO0('adm:users', page, O00O0O00O0OO))
    OOOO00OO000O.append([OO00O0OO0OOO('🔙 لوحة التحكم', 'adm:home')])
    return (O00OO0OO00O0, OOOO0O0OOO0O(*OOOO00OO000O))

def O00OO0OOOOO0(OO0O000OOO0O):
    OO000O0O0O00 = O00OO0O00OOO(OO0O000OOO0O)
    if not OO000O0O0O00:
        return None
    O00O00O000OO = OOOOOO0O0O00(f'SELECT {_SELECT_FILE_COLS} FROM files WHERE user_id=?', (OO0O000OOO0O,))
    O0OO0O00O0O0 = O0OO0O00OO0O(OO0O000OOO0O)
    O000O000O00O = f"👤 <b>{O0000O0O0000(OO000O0O0O00)}</b>\n━━━━━━━━━━━━━━\n🆔 <code>{OO0O000OOO0O}</code>\n📌 اليوزر: {OOO0O0O0O0OO(O0OOOOOOO0O0(OO000O0O0O00))}\n🕒 انضم: {OOO0O0O0O0OO(OO000O0O0O00['joined_at'])}\n🗂 حد الملفات المسموح: <b>{O0OO0O00O0O0}</b>\n📂 الملفات الحالية: {len(O00O00O000OO)}\n🚫 الحالة: {('محظور' if OO000O0O0O00['banned'] else 'نشط')}"
    O00O0O00OOOO = [[OO00O0OO0OOO(f"{OOO0O0OO0O0O(OO00O0O00000)} {OO00O0O00000['file_name'][:30]}", f"adm:file:{OO00O0O00000['id']}")] for OO00O0O00000 in O00O00O000OO]
    O00O0O00OOOO.append([OO00O0OO0OOO('✅ فك الحظر', f'adm:unban:{OO0O000OOO0O}') if OO000O0O0O00['banned'] else OO00O0OO0OOO('🚫 حظر', f'adm:ban:{OO0O000OOO0O}'), OO00O0OO0OOO('📩 إرسال رسالة', f'adm:msg:{OO0O000OOO0O}')])
    O00O0O00OOOO.append([OO00O0OO0OOO('➕ زيادة حد ملفاته (VIP)', f'adm:vip:{OO0O000OOO0O}'), OO00O0OO0OOO('⏹ إيقاف ملفاته', f'x:stopuser:{OO0O000OOO0O}')])
    O00O0O00OOOO.append([OO00O0OO0OOO('🔙 المستخدمون', 'adm:users:0')])
    return (O000O000O00O, OOOO0O0OOO0O(*O00O0O00OOOO))

def OOO00O0O0OO0():
    O00O0OOO0O0O = OO00000O0OOO()
    OOO00OO0OO00 = ['📡 <b>قنوات الاشتراك الإجباري</b>\n━━━━━━━━━━━━━━']
    OOO0OOOOO0OO = []
    if not O00O0OOO0O0O:
        OOO00OO0OO00.append('لا توجد قنوات — الاشتراك الإجباري <b>غير مفعّل</b>.')
    for O0O0OOO000O0, OOOOOOO0000O in enumerate(O00O0OOO0O0O, 1):
        OOO00OO0OO00.append(f"{O0O0OOO000O0}. <b>{OOO0O0O0O0OO(OOOOOOO0000O['title'])}</b>  <code>{OOO0O0O0O0OO(OOOOOOO0000O['chat_id'])}</code>")
        OOO0OOOOO0OO.append([OO00O0OO0OOO(f'✏️ تعديل {O0O0OOO000O0}', f"adm:chedit:{OOOOOOO0000O['id']}"), OO00O0OO0OOO(f'🗑 حذف {O0O0OOO000O0}', f"adm:chdel:{OOOOOOO0000O['id']}")])
    OOO0OOOOO0OO.append([OO00O0OO0OOO('➕ إضافة قناة', 'adm:chadd')])
    OOO0OOOOO0OO.append([OO00O0OO0OOO('🔙 لوحة التحكم', 'adm:home')])
    return ('\n'.join(OOO00OO0OO00), OOOO0O0OOO0O(*OOO0OOOOO0OO))
states = {}

def O00OO0OOO000(O0O000O00OOO, O000OOO0OOO0):
    states[O0O000O00OOO] = O000OOO0OOO0

def O0OOOO00OO0O():
    return OOOO0O0OOO0O([OO00O0OO0OOO('❌ إلغاء', 'adm:cancel')])

@O00OOO00O000.message_handler(commands=['start'])
def OOO0O0000O00(O0O0OO0O00OO):
    try:
        if O0O0OO0O00OO.chat.type != 'private':
            return
        O0000OOOO0O0 = OOO00OO000O0(O0O0OO0O00OO.from_user)
        states.pop(O0O0OO0O00OO.from_user.id, None)
        with contextlib.suppress(Exception):
            O00OOO00O000.delete_message(O0O0OO0O00OO.chat.id, O0O0OO0O00OO.message_id)
        if not O00O0O000000(O0O0OO0O00OO.from_user.id, O0O0OO0O00OO.chat.id, O0000OOOO0O0):
            return
        OO0O00OOO00O, OO00OO0O0000 = O0O0OO0OOOOO(O0O0OO0O00OO.from_user.id, O0O0OO0O00OO.from_user.first_name)
        OO0OOOOOO000(O0O0OO0O00OO.from_user.id, O0O0OO0O00OO.chat.id, OO0O00OOO00O, OO00OO0O0000, True)
    except Exception:
        O0OOO0000OO0.exception('cmd_start error')

@O00OOO00O000.message_handler(commands=['help'])
def O000OOOOOOOO(O00OO0000OO0):
    try:
        OOO00OO000O0(O00OO0000OO0.from_user)
        with contextlib.suppress(Exception):
            O00OOO00O000.delete_message(O00OO0000OO0.chat.id, O00OO0000OO0.message_id)
        OO0OOOOOO000(O00OO0000OO0.from_user.id, O00OO0000OO0.chat.id, OOOOO0OO0OOO(O00OO0000OO0.from_user.id), OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    except Exception:
        O0OOO0000OO0.exception('cmd_help error')

@O00OOO00O000.message_handler(commands=['admin'])
def OO0000O00O0O(OO00O00OOO00):
    try:
        if not O00000OO00OO(OO00O00OOO00.from_user.id):
            return
        with contextlib.suppress(Exception):
            O00OOO00O000.delete_message(OO00O00OOO00.chat.id, OO00O00OOO00.message_id)
        OO00O0O0O0OO, OO00000O00O0 = OOOO0O0O00O0()
        OO0OOOOOO000(OO00O00OOO00.from_user.id, OO00O00OOO00.chat.id, OO00O0O0O0OO, OO00000O00O0)
    except Exception:
        O0OOO0000OO0.exception('cmd_admin error')

def O000O00O000O(OO0OOOO0O000, reason=''):
    if O00000OO00OO(OO0OOOO0O000):
        return
    OOO0O0OO000O('INSERT INTO users(user_id,joined_at,last_seen,banned,ban_reason) VALUES(?,?,?,1,?) ON CONFLICT(user_id) DO UPDATE SET banned=1, ban_reason=excluded.ban_reason', (OO0OOOO0O000, OOO0O00OOO00(), OOO0O00OOO00(), reason))
    for OO0OOO0O0OOO in OOOOOO0O0O00('SELECT id FROM files WHERE user_id=?', (OO0OOOO0O000,)):
        OO0O0O000OOO(OO0OOO0O0OOO['id'])
    OO0OOOOOO000(OO0OOOO0O000, OO0OOOO0O000, '🚫 <b>تم حظرك من البوت.</b>\n' + (f'السبب: {OOO0O0O0O0OO(reason)}' if reason else ''))

def O000000OOOO0(O0O00OOOOO0O):
    OOO0O0OO000O('UPDATE users SET banned=0, ban_reason=NULL WHERE user_id=?', (O0O00OOOOO0O,))
    OO0OOOOOO000(O0O00OOOOO0O, O0O00OOOOO0O, '✅ <b>تم فك الحظر عنك!</b>\nاضغط /start للبدء من جديد.')
O000O0OO0O00 = threading.Lock()

def OO00O00000OO(OO0OO0O0O0O0):
    if OO0OO0O0O0O0['warnings']:
        return '⚠️ ' + '، '.join(OO0OO0O0O0O0['warnings'][:5])
    return '✅ نظيف'

def O00OOOO0O00O(OO0O00000000, scan=None, uploader_row=None, is_update=False):
    O000O0O0OOOO = OO0O00000000['id']
    if uploader_row is None:
        uploader_row = O00OO0O00OOO(OO0O00000000['user_id'])
    OO00O0OO0OO0 = bool(OO0O00000000.get('data_pd_id') or os.path.isfile(O0OOOOOOO0OO(O000O0O0OOOO, OO0O00000000['user_id'])))
    OOO0OO0O0O0O = O000O00OO00O(O000O0O0OOOO)
    O0O0OO00OO00 = '📝 <b>طلب تحديث ملف</b>' if is_update else '📥 <b>طلب استضافة جديد</b>'
    O0O00O0OO0OO = f"{O0O0OO00OO00} <code>#{O000O0O0OOOO}</code> (خادم #{OOO0OO0O0O0O})\n━━━━━━━━━━━━━━\n👤 {O0000O0O0000(uploader_row, OO0O00000000['user_id'])} (<code>{OO0O00000000['user_id']}</code>)\n📄 <code>{OOO0O0O0O0OO(OO0O00000000['file_name'])}</code> • {O0O0O00O000O(OO0O00000000['size'])}\n🗄 سجل داتا مرفق: <b>{('نعم ✅' if OO00O0OO0OO0 else 'لا')}</b>\n🔎 الفحص: {OOO0O0O0O0OO(OO0O00000000.get('scan_note') or '✅ نظيف')}"
    OO0O0O0000O0 = OOOO0O0OOO0O([OO00O0OO0OOO('✅ موافقة وتشغيل', f'ap:y:{O000O0O0OOOO}'), OO00O0OO0OOO('❌ رفض وحذف', f'ap:n:{O000O0O0OOOO}')], [OO00O0OO0OOO('🚫 رفض وحظر', f'ap:b:{O000O0O0OOOO}'), OO00O0OO0OOO('📥 سحب الملف', f'f:get:{O000O0O0OOOO}')])
    for O00O0O00000O in OO0O0O00O0O0:
        O0O0OO00O00O(O00O0O00000O, O0O00O0OO0OO, OO0O0O0000O0)

def O0O0000OO000(O00OO0000OOO, OOOO0O00OOO0, O00O00O0OO0O):
    O0O0OOO00O00 = O00OO0000OOO.from_user.id
    with contextlib.suppress(OSError):
        os.remove(OOOO0O00OOO0)
    OO0OOOOOO000(O0O0OOO00O00, O00OO0000OOO.chat.id, f"⛔ <b>تم رفض الملف تلقائياً</b>\n━━━━━━━━━━━━━━\nالسبب: <i>{OOO0O0O0O0OO(O00O00O0OO0O['critical'][0])}</i>", OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))

def OOO000OO00OO(O0O0OO0OO0O0, OOO0O00OO00O):
    OO0O00OO0000 = O0O0OO0OO0O0.from_user.id
    O0000O0OOOOO = int(OOO0O00OO00O['fid'])
    OOOOOOO00OO0 = bool(OOO0O00OO00O.get('after_code_upload', False))
    O00OO0000O0O = bool(OOO0O00OO00O.get('is_upd', False))
    O000OOOOOO00 = O0OOO0O00O0O(O0000O0OOOOO)
    if not O000OOOOOO00 or not O0O0000000O0(OO0O00OO0000, O000OOOOOO00):
        states.pop(OO0O00OO0000, None)
        return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, '❌ الملف غير موجود.', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    O0000000O0OO = O0O0OO0OO0O0.document
    OOO00OOO00O0 = O0000000O0OO.file_name or 'data.zip'
    if not OOO00OOO00O0.lower().endswith(ALLOWED_DATA_EXTENSIONS):
        return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, '❌ <b>صيغة ملف الداتا غير مدعومة.</b>\nأرسل ملف <code>.zip, .json, .db, .sqlite</code> أو اضغط تخطي 👇', OOOO0O0OOO0O([OO00O0OO0OOO('⏭ تخطي بدون داتا', f'f:dno:{O0000O0OOOOO}:{(1 if O00OO0000O0O else 0)}')]))
    if (O0000000O0OO.file_size or 0) > OO00OOO000O0:
        return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, f'⛔ <b>حجم ملف الداتا أكبر من الحد المسموح ({O0O0O00O000O(OO00OOO000O0)}).</b>', OOOO0O0OOO0O([OO00O0OO0OOO('⏭ تخطي', f'f:dno:{O0000O0OOOOO}:{(1 if O00OO0000O0O else 0)}')]))
    OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, '⏳ <b>جاري فحص واستيعاب ملف سجل الداتا...</b>')
    O00OOOOO000O = os.path.join(OOOO00OOO00O, f'tmpdata_{OO0O00OO0000}_{uuid.uuid4().hex}_{O00O0O00OOO0(OOO00OOO00O0)}')
    OOO00O00O000 = O0OOOOOOO0OO(O0000O0OOOOO, O000OOOOOO00['user_id'])
    try:
        OO0O00OO0OOO = O00OOO00O000.get_file(O0000000O0OO.file_id)
        OOO00OOOOOO0 = O00OOO00O000.download_file(OO0O00OO0OOO.file_path)
        with open(O00OOOOO000O, 'wb') as OOOOOO0OOO0O:
            OOOOOO0OOO0O.write(OOO00OOOOOO0)
        OO0O000O0O00, OOOOOOO000OO, O0000000O0O0 = OOO0O0OOO000(O00OOOOO000O, OOO00OOO00O0, OOO00O00O000)
        if not OO0O000O0O00:
            return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, f'❌ <b>تعذّر قبول ملف الداتا:</b>\n{OOO0O0O0O0OO(OOOOOOO000OO)}', OOOO0O0OOO0O([OO00O0OO0OOO('⏭ تخطي', f'f:dno:{O0000O0OOOOO}:{(1 if O00OO0000O0O else 0)}')]))
        states.pop(OO0O00OO0000, None)
        OO0OO00O000O(O0000O0OOOOO, O000OOOOOO00['user_id'], OOO00O00O000)
        O0000OOO00O0(O00000O0OOOO)
        O000OOOOOO00 = O0OOO0O00O0O(O0000O0OOOOO)
        O0OO0O00O00O = '، '.join(O0000000O0O0[:5]) + ('...' if len(O0000000O0O0) > 5 else '')
        if OOOOOOO00OO0:
            if O00000OO00OO(OO0O00OO0000):
                OO0O00OOOO0O(O0000O0OOOOO, OO0O00OO0000)
                OO0O0OO00000 = OO0O00O0000O(O0000O0OOOOO, OO0O00OO0000, f'✅ <b>تم رفع الكود ودمج سجل الداتا ({OOO0O0O0O0OO(O0OO0O00O00O)}) وتشغيله!</b>')
                if OO0O0OO00000:
                    return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, *OO0O0OO00000)
            else:
                O00OOOO0O00O(O000OOOOOO00, None, O00OO0O00OOO(OO0O00OO0000), O00OO0000O0O)
                return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, f"✅ <b>تم استلام الكود وسجل الداتا بنجاح!</b>\n━━━━━━━━━━━━━━\n📄 الكود: <code>{OOO0O0O0O0OO(O000OOOOOO00['file_name'])}</code>\n🗄 ملفات الداتا: <code>{OOO0O0O0O0OO(O0OO0O00O00O)}</code>\n\n⏳ <b>بانتظار موافقة الإدارة</b>", OOOO0O0OOO0O([OO00O0OO0OOO('📁 عرض ملفي', f'f:view:{O0000O0OOOOO}'), OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
        else:
            if O000OOOOOO00['status'] == 'approved' and OO00OOO00OO0(O0000O0OOOOO):
                OOO0O00O0O0O(O0000O0OOOOO)
                O0000000OOOO = f'✅ <b>تم استعادة الداتا ({OOO0O0O0O0OO(O0OO0O00O00O)}) وإعادة تشغيل البوت بها!</b>'
            else:
                O0000000OOOO = f'✅ <b>تم حفظ وربط سجل الداتا ({OOO0O0O0O0OO(O0OO0O00O00O)}) بملفك بنجاح!</b>'
            OO0O0OO00000 = OO0O00O0000O(O0000O0OOOOO, OO0O00OO0000, O0000000OOOO)
            if OO0O0OO00000:
                return OO0OOOOOO000(OO0O00OO0000, O0O0OO0OO0O0.chat.id, *OO0O0OO00000)
    finally:
        if os.path.exists(O00OOOOO000O):
            with contextlib.suppress(OSError):
                os.remove(O00OOOOO000O)

@O00OOO00O000.message_handler(content_types=['document'])
def O0OO000O0OO0(OO0000OO0O0O):
    try:
        if OO0000OO0O0O.chat.type != 'private':
            return
        OOOO00O0OO00 = OO0000OO0O0O.from_user.id
        if states.get(OOOO00O0OO00, {}).get('kind') == 'bc':
            return O0O0000O0OOO(OO0000OO0O0O)
        OO0OO0OOO0OO = OOO00OO000O0(OO0000OO0O0O.from_user)
        if not O00O0O000000(OOOO00O0OO00, OO0000OO0O0O.chat.id, OO0OO0OOO0OO):
            return
        O00O0O0O0OO0(OO0000OO0O0O)
        OOOOO0O000O0 = OO0000OO0O0O.document
        with contextlib.suppress(Exception):
            O00OOO00O000.delete_message(OO0000OO0O0O.chat.id, OO0000OO0O0O.message_id)
        O0O0O0O0000O = states.get(OOOO00O0OO00, {})
        if O0O0O0O0000O.get('kind') == 'upload_user_data':
            return OOO000OO00OO(OO0000OO0O0O, O0O0O0O0000O)
        if (OOOOO0O000O0.file_name or '').lower() == 'requirements.txt':
            states.pop(OOOO00O0OO00, None)
            return O00OO00OO00O(OO0000OO0O0O)
        O0O00OOOO000 = OOOOO0O000O0.file_name or 'script.py'
        O000OOO00OOO = O00000OO00OO(OOOO00O0OO00)
        if not O0O00OOOO000.lower().endswith('.py'):
            return OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, '❌ <b>مسموح برفع ملفات بايثون (<code>.py</code>) فقط هنا.</b>\n💡 لرفع ملف داتا/نسخة احتياطية، ادخل إلى <b>ملفي</b> واضغط <b>رفع واستعادة داتا</b>.', OOOO0O0OOO0O([OO00O0OO0OOO('📁 ملفي', 'u:my'), OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
        if (OOOOO0O000O0.file_size or 0) > O000OOOOO0OO:
            return OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, f'⛔ <b>حجم الملف أكبر من الحد المسموح ({O0O0O00O000O(O000OOOOO0OO)}).</b>', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
        OO0OO0O0OOO0 = O0O0O0O0000O.get('fid') if O0O0O0O0000O.get('kind') == 'update_file' else None
        OOO0O000OO0O = O0OO0O00OO0O(OOOO00O0OO00)
        if not O000OOO00OOO and (not OO0OO0O0OOO0):
            OOOO0O000O00 = OO0000O0O0OO(OOOO00O0OO00)
            if len(OOOO0O000O00) >= OOO0O000OO0O:
                O00OO00O00OO = OOOO0O000O00[0]
                return OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, f"🚫 <b>وصلت للحد الأقصى للملفات المستضافة</b>\n━━━━━━━━━━━━━━\nملفك الحالي: <code>{OOO0O0O0O0OO(O00OO00O00OO['file_name'])}</code>\n\n💡 اضغط <b>تحديث الكود</b> لاستبداله مباشرة 👇", OOOO0O0OOO0O([OO00O0OO0OOO('📝 تحديث الكود', f"f:upd:{O00OO00O00OO['id']}"), OO00O0OO0OOO('📁 إدارة ملفي', f"f:view:{O00OO00O00OO['id']}")], [OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
        OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, '⏳ <b>جاري استلام الملف وفحصه...</b>')
        OO0O00OOO0O0 = os.path.join(OOOO00OOO00O, f'tmp_{OOOO00O0OO00}_{uuid.uuid4().hex}.py')
        try:
            OOOOOOOOO00O = O00OOO00O000.get_file(OOOOO0O000O0.file_id)
            OO0OO00O0000 = O00OOO00O000.download_file(OOOOOOOOO00O.file_path)
            with open(OO0O00OOO0O0, 'wb') as OOOOO0OOOOOO:
                OOOOO0OOOOOO.write(OO0OO00O0000)
            OOO00O000OO0 = len(OO0OO00O0000)
            OOO0OOO00O0O = OOOO00O00O00(OO0O00OOO0O0, OOOO00O0OO00)
            if OOO0OOO00O0O['syntax_error']:
                return OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, f"❌ <b>الملف يحتوي على خطأ برمجي (Syntax Error)</b>\n<code>{OOO0O0O0O0OO(OOO0OOO00O0O['syntax_error'])}</code>", OOOO0O0OOO0O([OO00O0OO0OOO('🔄 محاولة مرة أخرى', 'u:up'), OO00O0OO0OOO('🏠 القائمة', 'u:menu')]))
            if not OOO0OOO00O0O['ok']:
                O0O0000OO000(OO0000OO0O0O, OO0O00OOO0O0, OOO0OOO00O0O)
                return
            states.pop(OOOO00O0OO00, None)
            OO0O0O0OOO00 = O0OO0O00000O(O0O00OOOO000)
            O0OO0OO0O0OO = os.path.join(O0OO0O0O0OO0(OOOO00O0OO00), f'{int(time.time())}_{OO0O0O0OOO00}')
            shutil.move(OO0O00OOO0O0, O0OO0OO0O0OO)
            with O000O0OO0O00:
                if OO0OO0O0OOO0 and O0OOO0O00O0O(OO0OO0O0OOO0) and O0O0000000O0(OOOO00O0OO00, O0OOO0O00O0O(OO0OO0O0OOO0)):
                    O000OO0O00O0 = O0OOO0O00O0O(OO0OO0O0OOO0)
                    OO0O0O000OOO(OO0OO0O0OOO0)
                    if O000OO0O00O0.get('path') and os.path.isfile(O000OO0O00O0['path']):
                        with contextlib.suppress(OSError):
                            os.remove(O000OO0O00O0['path'])
                    O0OO0O0O000O = OOOOO0OOO0OO(O0OO0OO0O0OO, OO0OO0O0OOO0, OOOO00O0OO00, OO0O0O0OOO00) or O000OO0O00O0.get('backup_pd_id')
                    OOO0O0OO000O("UPDATE files SET file_name=?, path=?, size=?, status='pending', desired_run=0, pd_id=NULL, backup_pd_id=?, uploaded_at=?, scan_note=?, content=? WHERE id=?", (OO0O0O0OOO00, O0OO0OO0O0OO, OOO00O000OO0, O0OO0O0O000O, OOO0O00OOO00(), OO00O00000OO(OOO0OOO00O0O), sqlite3.Binary(OO0OO00O0000), OO0OO0O0OOO0))
                    OOO0O0O0O000 = OO0OO0O0OOO0
                    OO00O00O0OOO = True
                else:
                    OOO0O0O0O000 = OOO0O0OO000O('INSERT INTO files(user_id,file_name,path,size,status,uploaded_at,scan_note,content,auto_restart) VALUES(?,?,?,?,?,?,?,?,1)', (OOOO00O0OO00, OO0O0O0OOO00, O0OO0OO0O0OO, OOO00O000OO0, 'pending', OOO0O00OOO00(), OO00O00000OO(OOO0OOO00O0O), sqlite3.Binary(OO0OO00O0000)))
                    O0OO0O0O000O = OOOOO0OOO0OO(O0OO0OO0O0OO, OOO0O0O0O000, OOOO00O0OO00, OO0O0O0OOO00)
                    if O0OO0O0O000O:
                        OOO0O0OO000O('UPDATE files SET backup_pd_id=? WHERE id=?', (O0OO0O0O000O, OOO0O0O0O000))
                    OO00O00O0OOO = False
            O0000OOO00O0(O00000O0OOOO)
            OO00OO0OOOO0 = 1 if OO00O00O0OOO else 0
            OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, f'✅ <b>تم فحص وحفظ ملف الكود:</b> <code>{OOO0O0O0O0OO(OO0O0O0OOO00)}</code>\n🖥 <b>خادم التشغيل المخصص:</b> Worker #{O000O00OO00O(OOO0O0O0O000)}\n━━━━━━━━━━━━━━\n🗄 <b>هل لديك ملف سجل داتا (نسخة احتياطية) تريد رفعه مع الكود؟</b>', OOOO0O0OOO0O([OO00O0OO0OOO('✅ نعم، لدي ملف داتا', f'f:dyes:{OOO0O0O0O000}:{OO00OO0OOOO0}'), OO00O0OO0OOO('⏭ لا، تخطي وتشغيل', f'f:dno:{OOO0O0O0O000}:{OO00OO0OOOO0}')]))
        except Exception as e:
            O0OOO0000OO0.exception('upload failed')
            OO0OOOOOO000(OOOO00O0OO00, OO0000OO0O0O.chat.id, f'❌ <b>حدث خطأ أثناء معالجة الملف:</b>\n<code>{OOO0O0O0O0OO(str(e)[:150])}</code>', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
        finally:
            if os.path.exists(OO0O00OOO0O0):
                with contextlib.suppress(OSError):
                    os.remove(OO0O00OOO0O0)
    except Exception:
        O0OOO0000OO0.exception('on_document outer error')

def OO0O00OOOO0O(O00O0OOO0O00, O0OO0O0000OO):
    O0O00OO0O0O0 = O0OOO0O00O0O(O00O0OOO0O00)
    if not O0O00OO0O0O0:
        return '⚠️ الطلب غير موجود.'
    OOO0O0OO000O("UPDATE files SET status='approved',approved_at=?,approved_by=?,desired_run=1,pid=NULL WHERE id=?", (OOO0O00OOO00(), O0OO0O0000OO, O00O0OOO0O00))
    OO00O0O0O00O, OO0OOO000000 = OO00OOOOO00O(O00O0OOO0O00, True)
    OOO00O00OOOO()
    O0000OOO00O0(O00000O0OOOO)
    if O0O00OO0O0O0['user_id'] != O0OO0O0000OO:
        OO0OOOOOO000(O0O00OO0O0O0['user_id'], O0O00OO0O0O0['user_id'], f"🎉 <b>تمت الموافقة على ملفك!</b>\n━━━━━━━━━━━━━━\n📄 الملف: <code>{OOO0O0O0O0OO(O0O00OO0O0O0['file_name'])}</code>\n🖥 خادم العمل: <b>Worker #{O000O00OO00O(O00O0OOO0O00)}</b>\n⏳ جاري تجهيز بيئة العمل وتشغيل الملف.", OOOO0O0OOO0O([OO00O0OO0OOO('📁 إدارة ملفي', f'f:view:{O00O0OOO0O00}'), OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    return f'✅ تمت الموافقة على الملف #{O00O0OOO0O00}\n{OO0OOO000000}'

def OOOO0OO0OOOO(O00O0OOO0OO0, ban=False):
    O00OO00O0O0O = O0OOO0O00O0O(O00O0OOO0OO0)
    if not O00OO00O0O0O:
        return '⚠️ الطلب غير موجود.'
    O0OOO000OO00, O00O000OO0OO = (O00OO00O0O0O['user_id'], O00OO00O0O0O['file_name'])
    O00OOOOO00OO(O00O0OOO0OO0)
    if ban:
        O000O00O000O(O0OOO000OO00, 'رفض ملف مخالف')
        return f'🚫 تم رفض #{O00O0OOO0OO0} وحظر المستخدم.'
    OO0OOOOOO000(O0OOO000OO00, O0OOO000OO00, f'❌ <b>تم رفض ملفك:</b> <code>{OOO0O0O0O0OO(O00O000OO0OO)}</code>', OOOO0O0OOO0O([OO00O0OO0OOO('📤 رفع ملف', 'u:up'), OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    return f'❌ تم رفض #{O00O0OOO0OO0} وحذف الملف.'

def O0O0000000O0(OO000000000O, O0O0OO0OO000):
    return bool(O0O0OO0OO000) and (O00000OO00OO(OO000000000O) or O0O0OO0OO000['user_id'] == OO000000000O)

def O0000O000OOO(OO000000OOO0, O0OOOOO0OO0O, note=None):
    O0OOO0O00O00 = OO0O00O0000O(O0OOOOO0OO0O, OO000000OOO0.from_user.id, note)
    if O0OOO0O00O00:
        O000O0OOO0O0(OO000000OOO0, *O0OOO0O00O00)
    else:
        O000O0OOO0O0(OO000000OOO0, 'ℹ️ الملف لم يعد موجوداً.', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))

@O00OOO00O000.callback_query_handler(func=lambda c: True)
def OO00OOOO00OO(OOOOO00OO0O0):
    try:
        O00O0O0OO00O = OOOOO00OO0O0.from_user.id
        OO0OOOOO0000 = OOO00OO000O0(OOOOO00OO0O0.from_user)
        OOOO000OOOOO = (OOOOO00OO0O0.data or '').split(':')
        OO00O0O00OO0 = OOOO000OOOOO[0]
        if OO00O0O00OO0 == 'noop':
            return O000OO0OOO00(OOOOO00OO0O0)
        if not O00000OO00OO(O00O0O0OO00O) and OO0OOOOO0000.get('banned'):
            return O000OO0OOO00(OOOOO00OO0O0, '🚫 أنت محظور من البوت.', True)
        if OO00O0O00OO0 == 'x':
            return O000000O0O00(OOOOO00OO0O0, OOOO000OOOOO)
        if OO00O0O00OO0 in ('f', 'u') and (not O00O0O000000(O00O0O0OO00O, OOOOO00OO0O0.message.chat.id, OO0OOOOO0000)):
            return O000OO0OOO00(OOOOO00OO0O0)
        OO000O000O0O = {'u': O00OO0OOOO00, 'f': OOOOOOO0OO00, 'ap': O0OOO0OO00OO, 'adm': OOOOOOOOOOO0}.get(OO00O0O00OO0)
        if OO000O000O0O is None:
            return O000OO0OOO00(OOOOO00OO0O0, '⚠️ زر غير معروف')
        OO000O000O0O(OOOOO00OO0O0, OOOO000OOOOO, OO0OOOOO0000)
    except Exception:
        O0OOO0000OO0.exception('on_callback error')

def O00OO0OOOO00(OOO0OO00O0OO, O0OO00OO00O0, OO00O0OO000O):
    OOOO0000O000, O0OOOOOO0OOO = (OOO0OO00O0OO.from_user.id, O0OO00OO00O0[1])
    if O0OOOOOO0OOO == 'chk':
        if O0000O0OOOO0(OOOO0000O000) and (not O00000OO00OO(OOOO0000O000)):
            return O000OO0OOO00(OOO0OO00O0OO, '❌ لم تشترك في كل القنوات بعد!', True)
        O000OO0OOO00(OOO0OO00O0OO, '✅ تم التحقق بنجاح')
        return O000O0OOO0O0(OOO0OO00O0OO, *O0O0OO0OOOOO(OOOO0000O000, OOO0OO00O0OO.from_user.first_name))
    if not O00O0O000000(OOOO0000O000, OOO0OO00O0OO.message.chat.id, OO00O0OO000O):
        return O000OO0OOO00(OOO0OO00O0OO)
    O000OO0OOO00(OOO0OO00O0OO)
    states.pop(OOOO0000O000, None)
    if O0OOOOOO0OOO == 'menu':
        O000O0OOO0O0(OOO0OO00O0OO, *O0O0OO0OOOOO(OOOO0000O000, OOO0OO00O0OO.from_user.first_name))
    elif O0OOOOOO0OOO == 'up':
        O000O0OOO0O0(OOO0OO00O0OO, '📤 <b>رفع ملف</b>\n━━━━━━━━━━━━━━\nأرسل ملف <code>.py</code> الآن.\n• بعد إرسال الكود سيسألك البوت إذا كان لديك ملف سجل داتا لترفعها معه.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
    elif O0OOOOOO0OOO == 'my':
        if O00000OO00OO(OOOO0000O000):
            return O000O0OOO0O0(OOO0OO00O0OO, *OOO0O000000O(0, OOOO0000O000))
        O0OO00OOOOO0 = OO0000O0O0OO(OOOO0000O000)
        if not O0OO00OOOOO0:
            return O000O0OOO0O0(OOO0OO00O0OO, '📭 <b>لا يوجد لديك ملفات مرفوعة حالياً.</b>', OOOO0O0OOO0O([OO00O0OO0OOO('📤 رفع ملف', 'u:up')], [OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
        if len(O0OO00OOOOO0) == 1:
            return O0000O000OOO(OOO0OO00O0OO, O0OO00OOOOO0[0]['id'])
        OO0OOO0O0O00 = [[OO00O0OO0OOO(f"{OOO0O0OO0O0O(O0O0O00OOO0O)} {O0O0O00OOO0O['file_name']}", f"f:view:{O0O0O00OOO0O['id']}")] for O0O0O00OOO0O in O0OO00OOOOO0]
        OO0OOO0O0O00.append([OO00O0OO0OOO('🔙 رجوع', 'u:menu')])
        O000O0OOO0O0(OOO0OO00O0OO, '📁 <b>ملفاتي المستضافة</b>', OOOO0O0OOO0O(*OO0OOO0O0O00))
    elif O0OOOOOO0OOO == 'acc':
        O000O0OOO0O0(OOO0OO00O0OO, *O0OOO00O0O00(OOOO0000O000))
    elif O0OOOOOO0OOO == 'ping':
        OOO0O0O000OO = time.perf_counter()
        with contextlib.suppress(Exception):
            O00OOO00O000.get_me()
        OO00OO00O0O0 = int((time.perf_counter() - OOO0O0O000OO) * 1000)
        OOO00000O00O = O0OO000O000O()
        OOO000O00000 = '🟢 متصل ومستقر' if OOO00000O00O['w1'] is not None and OOO00000O00O['w1'] < 120 else '🟡 في وضع الإنقاذ التلقائي'
        OOO0OO00OOOO = '🟢 متصل ومستقر' if OOO00000O00O['w2'] is not None and OOO00000O00O['w2'] < 120 else '🟡 في وضع الإنقاذ التلقائي'
        OOOOOO0O0OO0 = OO0OOOOO0OOO("SELECT COUNT(*) c FROM files WHERE status='approved' AND desired_run=1")['c']
        OOO0OOOO0O0O = f'🏓 <b>حالة خوادم الاستضافة</b>\n━━━━━━━━━━━━━━\n⚡ سرعة الاستجابة (Ping): <b>{OO00OO00O0O0} ms</b>\n🖥 خادم العمل الأول (Worker 1): <b>{OOO000O00000}</b>\n🖥 خادم العمل الثاني (Worker 2): <b>{OOO0OO00OOOO}</b>\n🟢 الملفات النشطة حالياً: <b>{OOOOOO0O0OO0}</b>\n⏱ وقت تشغيل النظام: <b>{O0O0000OOOO0(time.time() - OOO000O00O0O)}</b>'
        O000O0OOO0O0(OOO0OO00O0OO, OOO0OOOO0O0O, OOOO0O0OOO0O([OO00O0OO0OOO('🔄 تحديث القراءة', 'u:ping')], [OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
    elif O0OOOOOO0OOO == 'help':
        O000O0OOO0O0(OOO0OO00O0OO, OOOOO0OO0OOO(OOOO0000O000), OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))

def OOOOOOO0OO00(OO000OOOO0OO, OO000OO000O0, OO0O0OO0000O):
    O0OO00OOO000, OOOOO0O00OOO = (OO000OOOO0OO.from_user.id, OO000OO000O0[1])
    O0O00OO0OOO0 = int(OO000OO000O0[2])
    O00O0O00OO0O = O0OOO0O00O0O(O0O00OO0OOO0)
    if not O0O0000000O0(O0OO00OOO000, O00O0O00OO0O):
        return O000OO0OOO00(OO000OOOO0OO, '❌ غير مسموح أو الملف غير موجود.', True)
    if OOOOO0O00OOO == 'view':
        states.pop(O0OO00OOO000, None)
        O000OO0OOO00(OO000OOOO0OO)
        return O0000O000OOO(OO000OOOO0OO, O0O00OO0OOO0)
    if OOOOO0O00OOO == 'dyes':
        O00000000O00 = bool(int(OO000OO000O0[3])) if len(OO000OO000O0) > 3 else False
        O000OO0OOO00(OO000OOOO0OO)
        O00OO0OOO000(O0OO00OOO000, {'kind': 'upload_user_data', 'fid': O0O00OO0OOO0, 'after_code_upload': True, 'is_upd': O00000000O00})
        return O000O0OOO0O0(OO000OOOO0OO, '📤 <b>أرسل ملف سجل الداتا (النسخة الاحتياطية) الآن:</b>\n━━━━━━━━━━━━━━\n• يدعم أرشيف <code>.zip</code> أو ملفات قواعد البيانات (<code>.db, .sqlite, .json, .txt</code>).', OOOO0O0OOO0O([OO00O0OO0OOO('⏭ تخطي بدون داتا', f'f:dno:{O0O00OO0OOO0}:{(1 if O00000000O00 else 0)}')]))
    if OOOOO0O00OOO == 'dno':
        O00000000O00 = bool(int(OO000OO000O0[3])) if len(OO000OO000O0) > 3 else False
        states.pop(O0OO00OOO000, None)
        O000OO0OOO00(OO000OOOO0OO)
        if O00000OO00OO(O0OO00OOO000):
            OO0O00OOOO0O(O0O00OO0OOO0, O0OO00OOO000)
            return O0000O000OOO(OO000OOOO0OO, O0O00OO0OOO0, '✅ <b>تم رفع ملفك وتشغيله مباشرة!</b>')
        else:
            O00OOOO0O00O(O00O0O00OO0O, None, OO0O0OO0000O, O00000000O00)
            return O000O0OOO0O0(OO000OOOO0OO, '✅ <b>تم استلام ملفك بنجاح وبانتظار موافقة الإدارة!</b>', OOOO0O0OOO0O([OO00O0OO0OOO('📁 عرض ملفي', f'f:view:{O0O00OO0OOO0}'), OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    if OOOOO0O00OOO == 'drest':
        O000OO0OOO00(OO000OOOO0OO)
        O00OO0OOO000(O0OO00OOO000, {'kind': 'upload_user_data', 'fid': O0O00OO0OOO0, 'after_code_upload': False, 'is_upd': False})
        return O000O0OOO0O0(OO000OOOO0OO, f"📤 <b>استعادة / تحديث داتا الملف:</b> <code>{OOO0O0O0O0OO(O00O0O00OO0O['file_name'])}</code>\n━━━━━━━━━━━━━━\nأرسل الآن ملف النسخة الاحتياطية (<code>.zip</code>) أو ملف الداتا (<code>.json, .db, .sqlite</code>).", OOOO0O0OOO0O([OO00O0OO0OOO('↩️ رجوع للملف', f'f:view:{O0O00OO0OOO0}')]))
    if OOOOO0O00OOO == 'dbk':
        O000OO0OOO00(OO000OOOO0OO, '📦 جاري سحب وضغط ملفات الداتا...')
        return O0000OOO00O0(OOO00O0O0000, OO000OOOO0OO, O0O00OO0OOO0)
    if OOOOO0O00OOO == 'ar':
        O0000O0O00OO = 0 if int(O00O0O00OO0O.get('auto_restart', 1)) else 1
        OOO0O0OO000O('UPDATE files SET auto_restart=? WHERE id=?', (O0000O0O00OO, O0O00OO0OOO0))
        O0000OOO00O0(O0OOO000OO0O, O0O00OO0OOO0, bool(O0000O0O00OO))
        O000OO0OOO00(OO000OOOO0OO, '✅ تم التحديث')
        return O0000O000OOO(OO000OOOO0OO, O0O00OO0OOO0)
    if OOOOO0O00OOO == 'upd':
        O000OO0OOO00(OO000OOOO0OO)
        O00OO0OOO000(O0OO00OOO000, {'kind': 'update_file', 'fid': O0O00OO0OOO0})
        return O000O0OOO0O0(OO000OOOO0OO, f"📝 <b>تحديث الملف:</b> <code>{OOO0O0O0O0OO(O00O0O00OO0O['file_name'])}</code>\nأرسل الملف الجديد <code>.py</code> الآن.", OOOO0O0OOO0O([OO00O0OO0OOO('↩️ إلغاء التحديث', f'f:view:{O0O00OO0OOO0}')]))
    if OOOOO0O00OOO == 'get':
        O000OO0OOO00(OO000OOOO0OO, '📥 جاري إرسال الملف...')
        if not OO0O0000O0OO(O00O0O00OO0O):
            return O000OO0OOO00(OO000OOOO0OO, '❌ تعذّر جلب الملف.', True)
        with open(O00O0O00OO0O['path'], 'rb') as O00OOOOOO0O0:
            O00OOO00O000.send_document(OO000OOOO0OO.message.chat.id, O00OOOOOO0O0, caption=f"📄 <code>{OOO0O0O0O0OO(O00O0O00OO0O['file_name'])}</code>", visible_file_name=O00O0O00OO0O['file_name'])
        return
    if OOOOO0O00OOO == 'stat':
        if not OO00OOO00OO0(O0O00OO0OOO0):
            return O000OO0OOO00(OO000OOOO0OO, '🔴 الملف متوقف حالياً.', True)
        O000OO0OOO00(OO000OOOO0OO, '📊 جاري قياس الموارد...')
        return O0000OOO00O0(OOO0000O000O, OO000OOOO0OO, O0O00OO0OOO0)
    if OOOOO0O00OOO == 'lg':
        O000OO0OOO00(OO000OOOO0OO, '⏳ جاري جلب السجل...')
        return O0000OOO00O0(O0O000OO0O00, OO000OOOO0OO, O0O00OO0OOO0, False)
    if OOOOO0O00OOO == 'lgdoc':
        O000OO0OOO00(OO000OOOO0OO, '📥 جاري تجهيز ملف السجل...')
        return O0000OOO00O0(O0O000OO0O00, OO000OOOO0OO, O0O00OO0OOO0, True)
    if OOOOO0O00OOO == 'lgclr':
        O00O0OO00O00(O0O00OO0OOO0)
        O000OO0OOO00(OO000OOOO0OO, '🧹 تم إرسال أمر مسح السجل!', True)
        return O0000O000OOO(OO000OOOO0OO, O0O00OO0OOO0, '🧹 <b>تم تفريغ سجل التشغيل.</b>')
    if OOOOO0O00OOO == 'dl':
        O000OO0OOO00(OO000OOOO0OO)
        return O000O0OOO0O0(OO000OOOO0OO, f"⚠️ <b>تأكيد حذف الملف:</b> <code>{OOO0O0O0O0OO(O00O0O00OO0O['file_name'])}</code>؟", OOOO0O0OOO0O([OO00O0OO0OOO('✅ نعم، تأكيد الحذف', f'f:dy:{O0O00OO0OOO0}'), OO00O0OO0OOO('↩️ تراجع', f'f:view:{O0O00OO0OOO0}')]))
    if OOOOO0O00OOO == 'dy':
        O0O0O0OOO00O = O00O0O00OO0O['user_id']
        O00OOOOO00OO(O0O00OO0OOO0)
        O0000OOO00O0(O00000O0OOOO)
        O000OO0OOO00(OO000OOOO0OO, '🗑 تم حذف الملف')
        if O00000OO00OO(O0OO00OOO000) and O0O0O0OOO00O != O0OO00OOO000:
            return O000O0OOO0O0(OO000OOOO0OO, *OOO0O000000O(0, 0))
        return O000O0OOO0O0(OO000OOOO0OO, '🗑 <b>تم حذف ملفك بنجاح.</b>', OOOO0O0OOO0O([OO00O0OO0OOO('📤 رفع ملف', 'u:up'), OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    if OOOOO0O00OOO in ('st', 'sp', 'rs'):
        if O00O0O00OO0O['status'] != 'approved':
            return O000OO0OOO00(OO000OOOO0OO, '⏳ الملف لم يُعتمد بعد.', True)
        O000OO0OOO00(OO000OOOO0OO, '⏳ جاري التنفيذ...')
        O0000OOO00O0(OOOOOO0OO0OO, OO000OOOO0OO, OOOOO0O00OOO, O0O00OO0OOO0)

def OOO00O0O0000(OOO00OOOOOOO, O0OO00000OO0):
    O00OO0O00O0O = O0OOO0O00O0O(O0OO00000OO0)
    if not O00OO0O00O0O:
        return
    OOO0000OOO00 = O0O000000000(O0OO00000OO0, O00OO0O00O0O['user_id'])
    if not OOO0000OOO00 or not os.path.isfile(OOO0000OOO00):
        return O0000O000OOO(OOO00OOOOOOO, O0OO00000OO0, '⚠️ <b>لا توجد ملفات داتا منشأة داخل مجلد البوت حتى الآن.</b>')
    try:
        O0O000O0O0OO = f"backup_data_{O00OO0O00O0O['user_id']}_{datetime.now():%Y%m%d_%H%M}.zip"
        with open(OOO0000OOO00, 'rb') as OO0OO00O00O0:
            O00OOO00O000.send_document(OOO00OOOOOOO.message.chat.id, OO0OO00O00O0, caption=f"📦 <b>نسخة احتياطية لبيانات البوت</b>\n📄 الملف: <code>{OOO0O0O0O0OO(O00OO0O00O0O['file_name'])}</code>", visible_file_name=O0O000O0O0OO)
        O0000O000OOO(OOO00OOOOOOO, O0OO00000OO0, '✅ <b>تم سحب وإرسال النسخة الاحتياطية للداتا بنجاح!</b>')
    finally:
        with contextlib.suppress(OSError):
            os.remove(OOO0000OOO00)

def OOO0000O000O(OOOO0OO0O000, O0OO0O0O0OOO):
    O00OO00OOOO0 = OO00OO0OO0OO(O0OO0O0O0OOO)
    if not O00OO00OOOO0:
        return O0000O000OOO(OOOO0OO0O000, O0OO0O0O0OOO, '⚠️ <b>لم يتمكن الخادم من قراءة الموارد الآن.</b>')
    OOOOOOOOOO0O = f"📊 <b>استهلاك الموارد (Worker #{O000O00OO00O(O0OO0O0O0OOO)}):</b>\n• الرام (RAM): <b>{O00OO00OOOO0.get('rss_mb', 0):.1f} MB</b>\n• المعالج (CPU): <b>{O00OO00OOOO0.get('cpu', 0):.1f}%</b>\n• مساحة المجلد: <b>{O00OO00OOOO0.get('dir_mb', 0):.2f} MB</b>\n• مدة التشغيل: <b>{O0O0000OOOO0(O00OO00OOOO0.get('uptime', 0))}</b>"
    O0000O000OOO(OOOO0OO0O000, O0OO0O0O0OOO, OOOOOOOOOO0O)

def O0O000OO0O00(O0O0000000OO, OOOO00O0O0O0, as_doc=False):
    OOOO0OO0O00O = OO0000O0O0O0(OOOO00O0O0O0)
    OOO0O0000000 = O0OOO0O00O0O(OOOO00O0O0O0)
    OOO000O0OOOO = OOO0O0000000['file_name'] if OOO0O0000000 else f'file_{OOOO00O0O0O0}.py'
    if OOOO0OO0O00O is None:
        return O0000O000OOO(O0O0000000OO, OOOO00O0O0O0, '⚠️ <b>لم يرد خادم التشغيل بالسجل.</b>')
    if as_doc:
        OOO000OO0OO0 = io.BytesIO(OOOO0OO0O00O.encode('utf-8', errors='replace'))
        OOO000OO0OO0.name = f'log_{OOOO00O0O0O0}.txt'
        O00OOO00O000.send_document(O0O0000000OO.message.chat.id, OOO000OO0OO0, caption=f'📜 سجل <code>{OOO0O0O0O0OO(OOO000O0OOOO)}</code>', visible_file_name=f'log_{OOOO00O0O0O0}.txt')
        return
    OO000O0O0O0O = OOOO0OO0O00O.strip()[-2500:]
    OO000O00OO00 = f'📜 <b>سجل تشغيل الملف:</b> <code>{OOO0O0O0O0OO(OOO000O0OOOO)}</code>\n━━━━━━━━━━━━━━\n' + (f'<pre>{OOO0O0O0O0OO(OO000O0O0O0O)}</pre>' if OO000O0O0O0O else 'لا توجد مخرجات.')
    O000O0OOO0O0(O0O0000000OO, OO000O00OO00, OOOO0O0OOO0O([OO00O0OO0OOO('🔄 تحديث السجل', f'f:lg:{OOOO00O0O0O0}'), OO00O0OO0OOO('📥 تنزيل كملف', f'f:lgdoc:{OOOO00O0O0O0}')], [OO00O0OO0OOO('🧹 مسح السجل', f'f:lgclr:{OOOO00O0O0O0}'), OO00O0OO0OOO('🔙 رجوع للملف', f'f:view:{OOOO00O0O0O0}')]))

def OOOOOO0OO0OO(OOO0OO0000O0, OOO0OO00000O, O0OOO00OO000):
    if OOO0OO00000O == 'sp':
        OOOO00000OOO = OO0O0O000OOO(O0OOO00OO000)
        O000OO00OOO0 = '⏹ <b>تم إيقاف استضافة ملفك بنجاح.</b>' if OOOO00000OOO else 'ℹ️ <b>الاستضافة متوقفة بالفعل.</b>'
    elif OOO0OO00000O == 'rs':
        OOO0O0O0OO0O, OO000OO00O00 = OOO0O00O0O0O(O0OOO00OO000)
        O000OO00OOO0 = f'🔄 <b>جاري إعادة تشغيل ملفك على خادم العمل #{O000O00OO00O(O0OOO00OO000)}...</b>' if OOO0O0O0OO0O else '⚠️ تعذّر إعادة التشغيل.'
    else:
        OOO0O0O0OO0O, OO000OO00O00 = O0000O0000OO(O0OOO00OO000)
        O000OO00OOO0 = f'▶️ <b>تم إرسال أمر التشغيل إلى خادم العمل #{O000O00OO00O(O0OOO00OO000)}...</b>' if OOO0O0O0OO0O else '⚠️ تعذّر التشغيل.'
    O0000O000OOO(OOO0OO0000O0, O0OOO00OO000, O000OO00OOO0)

def O0OOO0OO00OO(OO000O0OO0O0, OO00000OO00O, OOO0O0OO0000):
    OO0OOO0OOOOO = OO000O0OO0O0.from_user.id
    if not O00000OO00OO(OO0OOO0OOOOO):
        return O000OO0OOO00(OO000O0OO0O0, '❌ للمالك فقط', True)
    O00O0OO00OO0, OOOO00000O0O = (OO00000OO00O[1], int(OO00000OO00O[2]))
    if O00O0OO00OO0 == 'y':
        O000OO0OOO00(OO000O0OO0O0, '⏳ جاري الموافقة والتشغيل...')
        O0000OOO00O0(OO0OO000O0OO, OO000O0OO0O0, OOOO00000O0O, OO0OOO0OOOOO)
    else:
        O000OO0OOO00(OO000O0OO0O0)
        O0O00OOOOO00 = OOOO0OO0OOOO(OOOO00000O0O, O00O0OO00OO0 == 'b')
        O000O0OOO0O0(OO000O0OO0O0, O0O00OOOOO00, OOOO0O0OOO0O([OO00O0OO0OOO('📬 الطلبات', 'adm:pend'), OO00O0OO0OOO('👑 اللوحة', 'adm:home')]))

def OO0OO000O0OO(OOOOOOOO00O0, OOOO0OOO000O, OOOOOO00O000):
    O0O0O0OO0OOO = OO0O00OOOO0O(OOOO0OOO000O, OOOOOO00O000)
    O000O0OOO0O0(OOOOOOOO00O0, O0O0O0OO0OOO, OOOO0O0OOO0O([OO00O0OO0OOO('📂 إدارة الملف', f'adm:file:{OOOO0OOO000O}'), OO00O0OO0OOO('📬 الطلبات', 'adm:pend')]))

def OOOOOOOOOOO0(OO0O0O0OOO0O, OOO0O00O0O00, OO0O0OO000OO):
    O00OO000O0O0 = OO0O0O0OOO0O.from_user.id
    if not O00000OO00OO(O00OO000O0O0):
        return O000OO0OOO00(OO0O0O0OOO0O, '❌ للمالك فقط', True)
    O000OO00O00O = OOO0O00O0O00[1]
    OOO0OOO00000 = OOO0O00O0O00[2] if len(OOO0O00O0O00) > 2 else None
    O0OOO000O00O(O00OO000O0O0, 'admin:' + O000OO00O00O, OOO0OOO00000 or '')
    if O000OO00O00O == 'home':
        O000OO0OOO00(OO0O0O0OOO0O)
        states.pop(O00OO000O0O0, None)
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOOO0O0O00O0())
    if O000OO00O00O == 'cancel':
        states.pop(O00OO000O0O0, None)
        O000OO0OOO00(OO0O0O0OOO0O, 'تم الإلغاء')
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOOO0O0O00O0())
    if O000OO00O00O == 'pend':
        O000OO0OOO00(OO0O0O0OOO0O)
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOO0O000000O(0, 0, True))
    if O000OO00O00O == 'files':
        O000OO0OOO00(OO0O0O0OOO0O)
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOO0O000000O(int(OOO0OOO00000 or 0), int(OOO0O00O0O00[3]) if len(OOO0O00O0O00) > 3 else 0))
    if O000OO00O00O == 'file':
        O000OO0OOO00(OO0O0O0OOO0O)
        return O0000O000OOO(OO0O0O0OOO0O, int(OOO0OOO00000))
    if O000OO00O00O == 'users':
        O000OO0OOO00(OO0O0O0OOO0O)
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOO0OO000O0O(int(OOO0OOO00000 or 0)))
    if O000OO00O00O == 'user':
        O000OO0OOO00(OO0O0O0OOO0O)
        OO0OO000OOOO = O00OO0OOOOO0(int(OOO0OOO00000))
        return O000O0OOO0O0(OO0O0O0OOO0O, *(OO0OO000OOOO or ('❌ المستخدم غير موجود.', None)))
    if O000OO00O00O == 'vip':
        OO00O00O0OO0 = int(OOO0OOO00000)
        O00OO0OO0O0O = O0OO0O00OO0O(OO00O00O0OO0)
        O000O0O0OO00 = 1 if O00OO0OO0O0O >= 10 else O00OO0OO0O0O + 1 if O00OO0OO0O0O < 5 else 10
        OOO0O0OO000O('UPDATE users SET max_files=? WHERE user_id=?', (O000O0O0OO00, OO00O00O0OO0))
        O000OO0OOO00(OO0O0O0OOO0O, f'✅ أصبح حد ملفات المستخدم: {O000O0O0OO00}')
        OO0OO000OOOO = O00OO0OOOOO0(OO00O00O0OO0)
        return O000O0OOO0O0(OO0O0O0OOO0O, *(OO0OO000OOOO or ('تم التحديث', None)))
    if O000OO00O00O == 'ban':
        O000O00O000O(int(OOO0OOO00000), 'حظر بواسطة الإدارة')
        O000OO0OOO00(OO0O0O0OOO0O, '🚫 تم الحظر')
        OO0OO000OOOO = O00OO0OOOOO0(int(OOO0OOO00000))
        return O000O0OOO0O0(OO0O0O0OOO0O, *(OO0OO000OOOO or ('🚫 تم الحظر.', None)))
    if O000OO00O00O == 'unban':
        O000000OOOO0(int(OOO0OOO00000))
        O000OO0OOO00(OO0O0O0OOO0O, '✅ تم فك الحظر')
        OO0OO000OOOO = O00OO0OOOOO0(int(OOO0OOO00000))
        return O000O0OOO0O0(OO0O0O0OOO0O, *(OO0OO000OOOO or ('✅ تم فك الحظر.', None)))
    if O000OO00O00O == 'msg':
        O000OO0OOO00(OO0O0O0OOO0O)
        O00OO0OOO000(O00OO000O0O0, {'kind': 'dm', 'target': int(OOO0OOO00000)})
        return O000O0OOO0O0(OO0O0O0OOO0O, f'📩 أرسل الآن نص الرسالة إلى <code>{OOO0OOO00000}</code>:', O0OOOO00OO0O())
    if O000OO00O00O == 'bc':
        O000OO0OOO00(OO0O0O0OOO0O)
        O00OO0OOO000(O00OO000O0O0, {'kind': 'bc'})
        return O000O0OOO0O0(OO0O0O0OOO0O, '📢 أرسل الرسالة التي تريد إذاعتها للجميع:', O0OOOO00OO0O())
    if O000OO00O00O == 'bcgo':
        O0OO00OOO0OO = states.pop(O00OO000O0O0, None)
        if not O0OO00OOO0OO or O0OO00OOO0OO.get('kind') != 'bc_confirm':
            return O000OO0OOO00(OO0O0O0OOO0O, 'انتهت صلاحية الطلب.', True)
        O000OO0OOO00(OO0O0O0OOO0O, '🚀 بدأت الإذاعة')
        O000O0OOO0O0(OO0O0O0OOO0O, '🚀 <b>جاري الإرسال...</b>')
        return O0000OOO00O0(OO000O0OO000, O00OO000O0O0, O0OO00OOO0OO['chat_id'], O0OO00OOO0OO['msg_id'], OO0O0O0OOO0O.message.message_id)
    if O000OO00O00O == 'ch':
        O000OO0OOO00(OO0O0O0OOO0O)
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOO00O0O0OO0())
    if O000OO00O00O == 'chadd':
        O000OO0OOO00(OO0O0O0OOO0O)
        O00OO0OOO000(O00OO000O0O0, {'kind': 'chadd'})
        return O000O0OOO0O0(OO0O0O0OOO0O, '➕ أرسل معرف القناة <code>@channel</code> أو الآيدي:', O0OOOO00OO0O())
    if O000OO00O00O == 'chedit':
        O000OO0OOO00(OO0O0O0OOO0O)
        O00OO0OOO000(O00OO000O0O0, {'kind': 'chedit', 'ch_id': int(OOO0OOO00000)})
        return O000O0OOO0O0(OO0O0O0OOO0O, '✏️ أرسل المعرف الجديد للقناة:', O0OOOO00OO0O())
    if O000OO00O00O == 'chdel':
        OOO0O0OO000O('DELETE FROM channels WHERE id=?', (int(OOO0OOO00000),))
        O000OO0OOO00(OO0O0O0OOO0O, '🗑 تم الحذف')
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOO00O0O0OO0())
    if O000OO00O00O == 'bk':
        O000OO0OOO00(OO0O0O0OOO0O, '💾 جاري الحفظ والمزامنة أونلاين...')
        return O0000OOO00O0(OO00O00OOOOO, OO0O0O0OOO0O.message.chat.id)
    if O000OO00O00O == 'full':
        O000OO0OOO00(OO0O0O0OOO0O, '📦 جاري تجميع كل البيانات...')
        return O0000OOO00O0(OO00O0OO00O0, OO0O0O0OOO0O.message.chat.id)
    if O000OO00O00O == 'stopall':
        O000OO0OOO00(OO0O0O0OOO0O, '⏳ جاري إيقاف الكل...')
        return O0000OOO00O0(O00O00O000O0, OO0O0O0OOO0O)
    if O000OO00O00O == 'startall':
        O000OO0OOO00(OO0O0O0OOO0O, '⏳ جاري تشغيل الكل...')
        return O0000OOO00O0(OOOO00O0OOO0, OO0O0O0OOO0O)
    if O000OO00O00O == 'prot':
        O00OOO0O0OO0('protection', '0' if OOO00OOOO0OO() else '1')
        O000OO0OOO00(OO0O0O0OOO0O, 'تم التبديل')
        return O000O0OOO0O0(OO0O0O0OOO0O, *OOOO0O0O00O0())
    if O000OO00O00O == 'pip':
        O000OO0OOO00(OO0O0O0OOO0O)
        O00OO0OOO000(O00OO000O0O0, {'kind': 'ext_ownerlibs'})
        return O000O0OOO0O0(OO0O0O0OOO0O, '🛠 أرسل آيدي المستخدم ثم أسماء المكتبات:', O0OOOO00OO0O())

def O00O00O000O0(O00000O0000O):
    O0OOOOOOO000 = OOOOOO0O0O00("SELECT id FROM files WHERE status='approved' AND (desired_run=1 OR pd_id IS NOT NULL)")
    for OOO00OO00OOO in O0OOOOOOO000:
        OO0O0O000OOO(OOO00OO00OOO['id'])
    OOO00O00OOOO()
    O000O0OOO0O0(O00000O0000O, f'⏹ تم إيقاف <b>{len(O0OOOOOOO000)}</b> ملف بنجاح.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 اللوحة', 'adm:home')]))

def OOOO00O0OOO0(OO000000OO0O):
    O000OO000O00 = 0
    for OOOO000O00OO in OOOOOO0O0O00("SELECT id,user_id FROM files WHERE status='approved'"):
        OOO0O0OOO0O0 = O00OO0O00OOO(OOOO000O00OO['user_id'])
        if OOO0O0OOO0O0 and OOO0O0OOO0O0.get('banned'):
            continue
        OO0O0OOOO00O, OOOO000O0000 = O0000O0000OO(OOOO000O00OO['id'])
        if OO0O0OOOO00O:
            O000OO000O00 += 1
    OOO00O00OOOO()
    O000O0OOO0O0(OO000000OO0O, f'▶️ تم تشغيل <b>{O000OO000O00}</b> ملف.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 اللوحة', 'adm:home')]))

def OO0O00OOOOOO(OOOOOO000OO0):
    OO000OO00O0O = (OOOOOO000OO0 or '').strip()
    OOO0OO0OOO00 = re.search('t\\.me/([A-Za-z0-9_]{4,})', OO000OO00O0O)
    if OOO0OO0OOO00:
        return '@' + OOO0OO0OOO00.group(1)
    if re.fullmatch('-?\\d{5,}', OO000OO00O0O):
        return int(OO000OO00O0O)
    if re.fullmatch('@?[A-Za-z0-9_]{4,}', OO000OO00O0O):
        return '@' + OO000OO00O0O.lstrip('@')
    return None

def O000OOO0O0OO(O0O00O0O00O0):
    O000OO0O000O = O00OOO00O000.get_chat(O0O00O0O00O0)
    O00000O0O000 = f'https://t.me/{O000OO0O000O.username}' if O000OO0O000O.username else getattr(O000OO0O000O, 'invite_link', None)
    if not O00000O0O000:
        with contextlib.suppress(Exception):
            O00000O0O000 = O00OOO00O000.export_chat_invite_link(O000OO0O000O.id)
    return (str(O000OO0O000O.id), O000OO0O000O.title or str(O000OO0O000O.id), O00000O0O000)

@O00OOO00O000.message_handler(content_types=['text', 'photo', 'video', 'audio', 'voice', 'animation', 'sticker', 'video_note', 'contact', 'location', 'poll'])
def O0O0000O0OOO(OOO00O0OOOO0):
    try:
        if OOO00O0OOOO0.chat.type != 'private':
            return
        O0O0O0OOOO0O = OOO00O0OOOO0.from_user.id
        OOO00OO000O0(OOO00O0OOOO0.from_user)
        O0O0OOOO0O00 = states.get(O0O0O0OOOO0O)
        if O0O0OOOO0O00 and O0O0OOOO0O00.get('kind', '').startswith('ext_'):
            return OO0O0OOOO000(OOO00O0OOOO0, O0O0OOOO0O00)
        if not O0O0OOOO0O00 or not O00000OO00OO(O0O0O0OOOO0O):
            if OOO00O0OOOO0.content_type == 'text' and (not (OOO00O0OOOO0.text or '').startswith('/')):
                with contextlib.suppress(Exception):
                    O00OOO00O000.delete_message(OOO00O0OOOO0.chat.id, OOO00O0OOOO0.message_id)
                O000OO0000OO = O00OO0O00OOO(O0O0O0OOOO0O)
                if O00O0O000000(O0O0O0OOOO0O, OOO00O0OOOO0.chat.id, O000OO0000OO):
                    O0OOOOO0O0O0, O0O000O0O00O = O0O0OO0OOOOO(O0O0O0OOOO0O, OOO00O0OOOO0.from_user.first_name)
                    OO0OOOOOO000(O0O0O0OOOO0O, OOO00O0OOOO0.chat.id, O0OOOOO0O0O0, O0O000O0O00O)
            return
        OOOO0O000000 = O0O0OOOO0O00['kind']
        if OOOO0O000000 == 'bc':
            states[O0O0O0OOOO0O] = {'kind': 'bc_confirm', 'chat_id': OOO00O0OOOO0.chat.id, 'msg_id': OOO00O0OOOO0.message_id}
            OO00OOO0OOOO = OO0OOOOO0OOO('SELECT COUNT(*) c FROM users WHERE active=1 AND banned=0')['c']
            O0O0OO00O00O(O0O0O0OOOO0O, f'👆 سيتم إرسالها إلى <b>{OO00OOO0OOOO}</b> مستخدم. تأكيد؟', OOOO0O0OOO0O([OO00O0OO0OOO('✅ إرسال للجميع', 'adm:bcgo'), OO00O0OO0OOO('❌ إلغاء', 'adm:cancel')]), OOO00O0OOOO0.message_id)
            return
        O0OOOOO0O0O0 = (OOO00O0OOOO0.text or '').strip()
        if OOOO0O000000 == 'dm':
            states.pop(O0O0O0OOOO0O, None)
            O0O0OOOO0OO0 = OO0OOOOOO000(O0O0OOOO0O00['target'], O0O0OOOO0O00['target'], f'📩 <b>رسالة من الإدارة:</b>\n\n{OOO0O0O0O0OO(O0OOOOO0O0O0)}', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
            return OO0OOOOOO000(O0O0O0OOOO0O, OOO00O0OOOO0.chat.id, '✅ تم الإرسال.' if O0O0OOOO0OO0 else '❌ تعذّر الإرسال.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 اللوحة', 'adm:home')]))
        if OOOO0O000000 in ('chadd', 'chedit'):
            OOOO000O0O0O = OO0O00OOOOOO(O0OOOOO0O0O0)
            if OOOO000O0O0O is None:
                return O0O0OO00O00O(O0O0O0OOOO0O, '❌ صيغة غير صحيحة.', O0OOOO00OO0O())
            try:
                OO0O0000OO00, OOO0O00OO0OO, O0OOO00000O0 = O000OOO0O0OO(OOOO000O0O0O)
            except Exception as e:
                return O0O0OO00O00O(O0O0O0OOOO0O, f'❌ {e}', O0OOOO00OO0O())
            states.pop(O0O0O0OOOO0O, None)
            if OOOO0O000000 == 'chadd':
                OOO0O0OO000O('INSERT OR IGNORE INTO channels(chat_id,title,link,added_at) VALUES(?,?,?,?)', (OO0O0000OO00, OOO0O00OO0OO, O0OOO00000O0, OOO0O00OOO00()))
            else:
                OOO0O0OO000O('UPDATE channels SET chat_id=?, title=?, link=? WHERE id=?', (OO0O0000OO00, OOO0O00OO0OO, O0OOO00000O0, O0O0OOOO0O00['ch_id']))
            O00OO000000O = OOO00O0O0OO0()
            return OO0OOOOOO000(O0O0O0OOOO0O, OOO00O0OOOO0.chat.id, O00OO000000O[0], O00OO000000O[1])
    except Exception:
        O0OOO0000OO0.exception('on_state_message error')

def OO000O0OO000(OO0OOO000OOO, OO0OO000OOO0, O00O0OO0OO0O, OO0O00O00O00):
    O0O00OOO00OO = OOOOOO0O0O00('SELECT user_id FROM users WHERE active=1 AND banned=0')
    O00O000OO0O0 = OOO0OO0OO00O = 0
    for OOOO0OOO0000 in O0O00OOO00OO:
        try:
            O00OOO00O000.copy_message(OOOO0OOO0000['user_id'], OO0OO000OOO0, O00O0OO0OO0O)
            O00O000OO0O0 += 1
        except Exception:
            OOO0OO0OO00O += 1
        time.sleep(0.05)
    with contextlib.suppress(Exception):
        O00OOO00O000.edit_message_text(f'✅ <b>اكتملت الإذاعة</b>\nنجح: {O00O000OO0O0} • فشل: {OOO0OO0OO00O}', OO0OOO000OOO, OO0O00O00O00, reply_markup=OOOO0O0OOO0O([OO00O0OO0OOO('🔙 اللوحة', 'adm:home')]))

def OO00O00OOOOO(OOO000O00OO0):
    O00OOO000O0O = None
    try:
        O00OOO000O0O, O0OO00OOOO00 = O0OO0OO00OO0()
        with open(O00OOO000O0O, 'rb') as OO000O00O0OO:
            O00OOO00O000.send_document(OOO000O00OO0, OO000O00O0OO, caption=f'💾 نسخة قاعدة البيانات + تم حفظ حالة البوت أونلاين\n🕒 {OOO0O00OOO00()}', visible_file_name=os.path.basename(O00OOO000O0O))
    except Exception as e:
        O0O0OO00O00O(OOO000O00OO0, f'❌ فشل النسخ الاحتياطي: <code>{OOO0O0O0O0OO(str(e)[:200])}</code>')
    finally:
        if O00OOO000O0O:
            O00OOOOO00O0(O00OOO000O0O)

def OO00O0OO00O0(O0O000OO000O):
    O000O000O000 = f'{datetime.now():%Y%m%d_%H%M%S}'
    O00O0OOO0OOO = os.path.join(OO00OO0O00OO, f'export_{O000O000O000}.zip')
    try:
        with zipfile.ZipFile(O00O0OOO0OOO, 'w', zipfile.ZIP_DEFLATED) as OO00O0OOOOO0:
            O000000OOO0O, OOOO0O0O0O00 = O0OO0OO00OO0()
            OO00O0OOOOO0.write(O000000OOO0O, 'database/botdb.sqlite')
            O00OOOOO00O0(O000000OOO0O)
            for OO0000O000OO in OOOOOO0O0O00(f'SELECT {_SELECT_FILE_COLS} FROM files'):
                if OO0O0000O0OO(OO0000O000OO):
                    OO00O0OOOOO0.write(OO0000O000OO['path'], f"users/{OO0000O000OO['user_id']}/{OO0000O000OO['file_name']}")
        with open(O00O0OOO0OOO, 'rb') as OOO00O00O0O0:
            O00OOO00O000.send_document(O0O000OO000O, OOO00O00O0O0, caption=f'📦 سحب كامل للبيانات\n🕒 {OOO0O00OOO00()}', visible_file_name=os.path.basename(O00O0OOO0OOO))
    except Exception as e:
        O0O0OO00O00O(O0O000OO000O, f'❌ فشل سحب البيانات: {e}')
    finally:
        with contextlib.suppress(OSError):
            os.remove(O00O0OOO0OOO)
O000OO00O0OO.executescript("\nCREATE TABLE IF NOT EXISTS copy_outbox(\n id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER NOT NULL,\n user_id INTEGER NOT NULL, message_id INTEGER NOT NULL, file_id TEXT NOT NULL,\n file_name TEXT, caption TEXT, attempts INTEGER DEFAULT 0,\n next_try REAL DEFAULT 0, delivered INTEGER DEFAULT 0, last_error TEXT,\n UNIQUE(owner_id,user_id,message_id));\nCREATE TABLE IF NOT EXISTS library_requests(\n id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,\n packages TEXT NOT NULL, status TEXT DEFAULT 'pending', created_at TEXT,\n decided_by INTEGER, result TEXT);\nCREATE TABLE IF NOT EXISTS audit_log(\n id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id INTEGER, action TEXT,\n target TEXT, created_at TEXT);\n")

def O0OOO000O00O(OOOOO0O00000, OO000O00OOOO, target=''):
    OOO0O0OO000O('INSERT INTO audit_log(actor_id,action,target,created_at) VALUES(?,?,?,?)', (OOOOO0O00000, OO000O00OOOO, str(target)[:200], OOO0O00OOO00()))

def O00O0O0O0OO0(OO000OOO0O0O):
    O00O0OO0OO00 = OO000OOO0O0O.document
    O00OOOOOO0OO = f"📥 نسخة مستند من المستخدم: {OO000OOO0O0O.from_user.id}\nالاسم: {(O00O0OO0OO00.file_name or 'doc')[:160]}"
    for OO0OOOO000O0 in OO0O0O00O0O0:
        OOO0O0OO000O('INSERT OR IGNORE INTO copy_outbox(owner_id,user_id,message_id,file_id,file_name,caption) VALUES(?,?,?,?,?,?)', (OO0OOOO000O0, OO000OOO0O0O.from_user.id, OO000OOO0O0O.message_id, O00O0OO0OO00.file_id, O00O0OO0OO00.file_name, O00OOOOOO0OO))

def O0O0OOO0000O():
    while True:
        try:
            OO00O0OOO000 = OOOOOO0O0O00('SELECT * FROM copy_outbox WHERE delivered=0 AND next_try<=? ORDER BY id LIMIT 20', (time.time(),))
            for OO0O00O00OOO in OO00O0OOO000:
                try:
                    O00OOO00O000.send_document(OO0O00O00OOO['owner_id'], OO0O00O00OOO['file_id'], caption=OO0O00O00OOO['caption'], parse_mode=None)
                    OOO0O0OO000O('UPDATE copy_outbox SET delivered=1 WHERE id=?', (OO0O00O00OOO['id'],))
                except Exception:
                    O0OOOOO0OOO0 = OO0O00O00OOO['attempts'] + 1
                    OOO0O0OO000O('UPDATE copy_outbox SET attempts=?,next_try=? WHERE id=?', (O0OOOOO0OOO0, time.time() + 60, OO0O00O00OOO['id']))
                time.sleep(0.1)
        except Exception:
            pass
        time.sleep(3)
OOO0OO00OO0O = re.compile('[A-Za-z0-9][A-Za-z0-9._-]{0,70}(?:==[A-Za-z0-9][A-Za-z0-9.!+_-]{0,35})?\\Z')

def O00OO0000O00(OO0OOO0O00OO):
    O0OO0OOOO0O0 = []
    for O00000OOO00O in OO0OOO0O00OO.splitlines():
        O00000OOO00O = O00000OOO00O.split('#', 1)[0].strip()
        if not O00000OOO00O:
            continue
        for OOOOOO0O0000 in re.split('[\\s,]+', O00000OOO00O):
            if not OOO0OO00OO0O.fullmatch(OOOOOO0O0000):
                raise ValueError('اسم مكتبة غير صالح.')
            if OOOOOO0O0000 not in O0OO0OOOO0O0:
                O0OO0OOOO0O0.append(OOOOOO0O0000)
    if not O0OO0OOOO0O0 or len(O0OO0OOOO0O0) > 15:
        raise ValueError('أرسل من 1 إلى 15 مكتبة.')
    return O0OO0OOOO0O0

def O0OOOOOOOOOO(OO00O0000OO0):
    return re.sub('[-_.]+', '-', OO00O0000OO0.split('==', 1)[0]).lower()

def OOOO00O00O0O(OOOOO00OOO00):
    with tokenize.open(OOOOO00OOO00) as OOOOO0O0O0OO:
        OOOO000O00O0 = ast.parse(OOOOO0O0O0OO.read())
    O0OOO00O000O = set()
    for O000OOO0O000 in ast.walk(OOOO000O00O0):
        if isinstance(O000OOO0O000, ast.Import):
            O0OOO00O000O.update((O000OO0O0OOO.name.split('.')[0] for O000OO0O0OOO in O000OOO0O000.names))
        elif isinstance(O000OOO0O000, ast.ImportFrom) and (not O000OOO0O000.level) and O000OOO0O000.module:
            O0OOO00O000O.add(O000OOO0O000.module.split('.')[0])
    return {'imports': sorted(O0OOO00O000O - O0OOO000000O - {'__main__'})}

def O0OO000OOOO0(OO0O0OOOOO0O, O0OOO0OO0O00, OOOOO00000OO, repair=False):
    O000O0O0O0O0 = O0OOO0O00O0O(OOOOO00000OO)
    if not O000O0O0O0O0 or not OO0O0000O0OO(O000O0O0O0O0):
        return OO0OOOOOO000(OO0O0OOOOO0O, O0OOO0OO0O00, '❌ تعذّر قراءة الملف.', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة', 'u:menu')]))
    OO00OOO0O00O = OOOO00O00O0O(O000O0O0O0O0['path'])
    O00000000000 = ''
    if repair and O000O0O0O0O0['status'] == 'approved':
        OOOOO0OO0OO0 = sorted({ALLOWED_PIP[O0OOO0O0OOOO] for O0OOO0O0OOOO in OO00OOO0O00O['imports'] if O0OOO0O0OOOO in ALLOWED_PIP})
        if OOOOO0OO0OO0:
            O00OOO0O0O0O = OOO0O0OO000O("INSERT INTO library_requests(user_id,packages,status,created_at,decided_by) VALUES(?,?,'approved',?,?)", (O000O0O0O0O0['user_id'], json.dumps(OOOOO0OO0OO0), OOO0O00OOO00(), O000O0O0O0O0['user_id']))
            OOO00O00OOOO()
            O00000000000 = f'🛠 <b>تم إرسال أمر تثبيت المكتبات (#{O00OOO0O0O0O}).</b>\n\n'
    OO0OOO00OO00 = [O00000000000 + '🔎 <b>مكتبات الملف:</b>']
    for OO0O0O0OO0OO in OO00OOO0O00O['imports']:
        OO0OOO00OO00.append(f'• <code>{OOO0O0O0O0OO(OO0O0O0OO0OO)}</code>')
    if not OO00OOO0O00O['imports']:
        OO0OOO00OO00.append('✅ لا يحتاج مكتبات خارجية.')
    OO0OOOOOO000(OO0O0OOOOO0O, O0OOO0OO0O00, '\n'.join(OO0OOO00OO00), OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع للملف', f'f:view:{OOOOO00000OO}')]))

def O0000O0000O0(OO000O00000O, OO0O000OO000, OO00O0000OOO):
    try:
        O0O00O00OOO0 = O00OO0000O00(OO00O0000OOO)
    except ValueError as error:
        return OO0OOOOOO000(OO000O00000O, OO0O000OO000, '❌ ' + OOO0O0O0O0OO(error), OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
    OO0000O0OO0O = OOO0O0OO000O('INSERT INTO library_requests(user_id,packages,created_at) VALUES(?,?,?)', (OO000O00000O, json.dumps(O0O00O00OOO0), OOO0O00OOO00()))
    O00O00OO00OO = {O0OOOOOOOOOO(OO0OOOO00O00) for OO0OOOO00O00 in ALLOWED_PIP.values()}
    if O00000OO00OO(OO000O00000O) or (O0000000O00O('auto_libs', '1') == '1' and all((O0OOOOOOOOOO(OO0OOO0OO0O0) in O00O00OO00OO for OO0OOO0OO0O0 in O0O00O00OOO0))):
        O00O0O0OO0O0(OO0000O0OO0O, OO000O00000O)
        OO0OOOOOO000(OO000O00000O, OO0O000OO000, '⏳ <b>جاري تثبيت المكتبات المطلوبة على الخوادم...</b>', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))
    else:
        OO0OOOOOO000(OO000O00000O, OO0O000OO000, '📬 <b>تم إرسال طلب المكتبات للإدارة.</b>', OOOO0O0OOO0O([OO00O0OO0OOO('🏠 القائمة الرئيسية', 'u:menu')]))

def O00OO00OO00O(O00000OO0000):
    O0OO0O0OOOOO = O00000OO0000.from_user.id
    O0O0OOO00OO0 = O00OOO00O000.download_file(O00OOO00O000.get_file(O00000OO0000.document.file_id).file_path)
    return O0000O0000O0(O0OO0O0OOOOO, O00000OO0000.chat.id, O0O0OOO00OO0.decode('utf-8-sig', errors='replace'))

def OO00O0000O0O(O0OOOOOOOO00, O0OO0000O0OO):
    O00O0OOO00O0 = O000000O0OO0(f'libs_{O0OOOOOOOO00}.json') or ''
    if not O00O0OOO00O0:
        return OO0OOOOOO000(O0OOOOOOOO00, O0OO0000O0OO, 'ℹ️ شغّل ملفك الأول أو ثبّت مكتبة لتظهر هنا.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
    OO00OOOO000O = json.loads(O00O0OOO00O0)
    O00000OO0OOO = [f"• <code>{OOO0O0O0O0OO(O00O0O00O000.get('name'))}</code> ({OOO0O0O0O0OO(O00O0O00O000.get('version'))})" for O00O0O00O000 in OO00OOOO000O[:60]]
    OO0OOOOOO000(O0OOOOOOOO00, O0OO0000O0OO, '📚 <b>المكتبات المثبتة:</b>\n' + '\n'.join(O00000OO0OOO), OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))

def O00O0OOOOOO0():
    O0O0OO0OOO0O = f"🧰 <b>الإدارة المتقدمة</b>\n━━━━━━━━━━━━━━\n• وضع الصيانة: <b>{('مفعّل 🛠' if O0000000O00O('maintenance', '0') == '1' else 'متوقف 🟢')}</b>\n• التثبيت التلقائي للمكتبات: <b>{('مفعّل ✅' if O0000000O00O('auto_libs', '1') == '1' else 'معطّل ❌')}</b>"
    return (O0O0OO0OOO0O, OOOO0O0OOO0O([OO00O0OO0OOO('🛠 تبديل الصيانة', 'x:maintenance'), OO00O0OO0OOO('📚 التثبيت التلقائي', 'x:autolibs')], [OO00O0OO0OOO('📦 طلبات المكتبات', 'x:requests'), OO00O0OO0OOO('🔙 لوحة المالك', 'adm:home')]))

def O000000O0O00(O0O0OOO000OO, O0OO0000O0O0):
    OOO00O00O00O = O0O0OOO000OO.from_user.id
    O0000OO00000 = O0OO0000O0O0[1] if len(O0OO0000O0O0) > 1 else ''
    O0OO0000OOOO = O0OO0000O0O0[2] if len(O0OO0000O0O0) > 2 else ''
    O000OO0OOO00(O0O0OOO000OO)
    if O0000OO00000 == 'add':
        O00OO0OOO000(OOO00O00O00O, {'kind': 'ext_libraries'})
        return O000O0OOO0O0(O0O0OOO000OO, '➕ أرسل اسم المكتبة أو عدة مكتبات مفصولة بمسافة:', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', 'u:menu')]))
    if O0000OO00000 == 'libs':
        return O0000OOO00O0(OO00O0000O0O, OOO00O00O00O, O0O0OOO000OO.message.chat.id)
    if O0000OO00000 in ('diag', 'fix'):
        return O0000OOO00O0(O0OO000OOOO0, OOO00O00O00O, O0O0OOO000OO.message.chat.id, int(O0OO0000OOOO), O0000OO00000 == 'fix')
    if not O00000OO00OO(OOO00O00O00O):
        return
    if O0000OO00000 == 'admin':
        return O000O0OOO0O0(O0O0OOO000OO, *O00O0OOOOOO0())
    if O0000OO00000 in ('maintenance', 'autolibs'):
        OOO0000O0OO0 = 'maintenance' if O0000OO00000 == 'maintenance' else 'auto_libs'
        O00OOO0O0OO0(OOO0000O0OO0, '0' if O0000000O00O(OOO0000O0OO0, '0' if O0000OO00000 == 'maintenance' else '1') == '1' else '1')
        OOO00O00OOOO()
        return O000O0OOO0O0(O0O0OOO000OO, *O00O0OOOOOO0())
    if O0000OO00000 == 'stopuser':
        OOOO00OO0O0O = int(O0OO0000OOOO)
        for O0O000O0OO00 in OOOOOO0O0O00('SELECT id FROM files WHERE user_id=?', (OOOO00OO0O0O,)):
            OO0O0O000OOO(O0O000O0OO00['id'])
        return O000O0OOO0O0(O0O0OOO000OO, '⏹ تم إيقاف ملفات المستخدم.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 رجوع', f'adm:user:{OOOO00OO0O0O}')]))
    if O0000OO00000 == 'requests':
        O000O0OOO0OO = OOOOOO0O0O00("SELECT * FROM library_requests WHERE status='pending' ORDER BY id LIMIT 15")
        OO0OO0O0000O = [[OO00O0OO0OOO(f"📦 #{O0O0O0O000O0['id']} / {O0O0O0O000O0['user_id']}", f"x:libapprove:{O0O0O0O000O0['id']}")] for O0O0O0O000O0 in O000O0OOO0OO]
        OO0OO0O0000O.append([OO00O0OO0OOO('🔙 رجوع', 'x:admin')])
        return O000O0OOO0O0(O0O0OOO000OO, '📦 طلبات المكتبات (اضغط للاعتماد):', OOOO0O0OOO0O(*OO0OO0O0000O))
    if O0000OO00000 == 'libapprove':
        O00O0O0OO0O0(int(O0OO0000OOOO), OOO00O00O00O)
        return O000O0OOO0O0(O0O0OOO000OO, '✅ تم الاعتماد.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 الطلبات', 'x:requests')]))

def OO0O0OOOO000(O0OOOOO00OOO, O000O0O0OOO0):
    O00OO000OO0O = O0OOOOO00OOO.from_user.id
    with contextlib.suppress(Exception):
        O00OOO00O000.delete_message(O0OOOOO00OOO.chat.id, O0OOOOO00OOO.message_id)
    O0O00O000O00 = (O0OOOOO00OOO.text or '').strip()
    OO00O00O00OO = O000O0O0OOO0['kind']
    if OO00O00O00OO == 'ext_libraries':
        states.pop(O00OO000OO0O, None)
        return O0000O0000O0(O00OO000OO0O, O0OOOOO00OOO.chat.id, O0O00O000O00)
    if OO00O00O00OO == 'ext_ownerlibs' and O00000OO00OO(O00OO000OO0O):
        O00000OOO0O0 = O0O00O000O00.split(maxsplit=1)
        if len(O00000OOO0O0) == 2 and O00000OOO0O0[0].isdigit():
            O0O0OOOOO00O = O00OO0000O00(O00000OOO0O0[1])
            O000O00O0000 = OOO0O0OO000O('INSERT INTO library_requests(user_id,packages,created_at) VALUES(?,?,?)', (int(O00000OOO0O0[0]), json.dumps(O0O0OOOOO00O), OOO0O00OOO00()))
            states.pop(O00OO000OO0O, None)
            O00O0O0OO0O0(O000O00O0000, O00OO000OO0O)
            return OO0OOOOOO000(O00OO000OO0O, O0OOOOO00OOO.chat.id, '⏳ تم إرسال طلب تثبيت المكتبات.', OOOO0O0OOO0O([OO00O0OO0OOO('🔙 اللوحة', 'adm:home')]))

def O0O0O0OOOOOO():
    with contextlib.suppress(Exception):
        O00OOO00O000.remove_webhook()
    threading.Thread(target=O0O0OOO0000O, daemon=True).start()
    threading.Thread(target=O0O0O00O00O0, daemon=True).start()
    threading.Thread(target=OOOOOO0OOOOO, daemon=True).start()
    O0OOO0000OO0.info('✅ Main bot started (Self-Sync enabled: %s)', SELF_STATE_ARCHIVE_NAME)
    while True:
        try:
            O00OOO00O000.infinity_polling(timeout=20, long_polling_timeout=20, allowed_updates=['message', 'callback_query'])
        except Exception:
            time.sleep(5)
if __name__ == '__main__':
    O0O0O0OOOOOO()