"""
setup_static_structure.py
==========================
1. Creates the new static folder structure:
   frontend/static/
   ├── css/
   │   ├── base.css         (global: variables, header, body, buttons)
   │   ├── auth.css         (login, OTP, register pages)
   │   ├── voting.css       (voter dashboard, candidate options, vote cards)
   │   └── admin.css        (admin dashboard, donut charts, state cards)
   ├── voting/
   │   ├── voting.css       (same as above - voting-specific)
   │   └── images/          (voting-related images/icons)
   └── candidates/
       └── images/          (downloaded candidate photos)

2. Downloads real politician photos from Wikipedia/Google and saves as PNG files.

Run: python -X utf8 setup_static_structure.py
"""

import os, sys, io, base64, json, time
import urllib.request, urllib.parse

# Windows UTF-8
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except:
        pass

# ─── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR    = os.path.join(BASE_DIR, 'frontend', 'static')
CAND_IMG_DIR  = os.path.join(STATIC_DIR, 'candidates', 'images')
VOTING_DIR    = os.path.join(STATIC_DIR, 'voting')
VOTING_IMG_DIR = os.path.join(VOTING_DIR, 'images')
CSS_DIR       = os.path.join(STATIC_DIR, 'css')

# ─── Create Dirs ────────────────────────────────────────────────────────────
for d in [CAND_IMG_DIR, VOTING_DIR, VOTING_IMG_DIR, CSS_DIR]:
    os.makedirs(d, exist_ok=True)
    print(f"[DIR] {d}")

# ─── Pillow Setup ────────────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_OK = True
    print("[OK]  Pillow available")
except ImportError:
    PIL_OK = False
    print("[WARN] Pillow not found - avatars will be skipped")

# ─── Candidate definitions ───────────────────────────────────────────────────
CANDIDATES = [
    {"name": "Chandra Babu Naidu", "party": "TDP",          "state": "ap",      "color": (0,  150, 50),  "wiki": "N._Chandrababu_Naidu"},
    {"name": "Jagan",              "party": "YSRCP",         "state": "ap",      "color": (0,  80,  180), "wiki": "Y._S._Jagan_Mohan_Reddy"},
    {"name": "Pawan Kalyan",       "party": "Janasena",      "state": "ap",      "color": (255,100, 0),   "wiki": "Pawan_Kalyan"},
    {"name": "Revanth Reddy",      "party": "INC",           "state": "tg",      "color": (200, 20,  20), "wiki": "A._Revanth_Reddy"},
    {"name": "KCR",                "party": "BRS",           "state": "tg",      "color": (255,180, 0),   "wiki": "K._Chandrashekar_Rao"},
    {"name": "Vijay",              "party": "TVK",           "state": "chennai", "color": (100, 20,  200),"wiki": "Vijay_(actor)"},
    {"name": "Stalin",             "party": "DMK",           "state": "chennai", "color": (180, 0,   0),  "wiki": "M._K._Stalin"},
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://en.wikipedia.org/',
}

# ─── Wikipedia thumbnail fetcher ─────────────────────────────────────────────
def get_wiki_thumbnail(page_name):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_name)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read())
        for key in ('thumbnail', 'originalimage'):
            if key in data:
                src = data[key].get('source', '')
                if src:
                    return src
    except Exception as e:
        print(f"   [wiki] {e}")
    return None

def download_image_file(url, save_path):
    """Download and process image using Pillow -> save as 300x300 JPEG."""
    try:
        h = dict(HEADERS)
        h['Accept'] = 'image/*,*/*'
        req = urllib.request.Request(url, headers=h)
        with urllib.request.urlopen(req, timeout=20) as r:
            raw = r.read()
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h2 = img.size
        min_d = min(w, h2)
        l = (w - min_d) // 2
        t = (h2 - min_d) // 3
        img = img.crop((l, t, l + min_d, t + min_d))
        img = img.resize((300, 300), Image.LANCZOS)
        img.save(save_path, format='JPEG', quality=90)
        print(f"   [SAVED] {os.path.basename(save_path)} ({os.path.getsize(save_path)//1024}KB)")
        return True
    except Exception as e:
        print(f"   [fail] {e}")
        return False

# ─── Pillow Avatar Generator ──────────────────────────────────────────────────
AVATAR_COLORS_LIST = [
    (79, 70, 229), (16, 185, 129), (245, 158, 11),
    (239, 68, 68), (139, 92, 246), (6, 182, 212), (236, 72, 153),
]

def make_avatar(name, color, save_path, size=300):
    """Generate a styled initials avatar and save as PNG."""
    if not PIL_OK:
        return False
    try:
        img = Image.new('RGB', (size, size), color)
        draw = ImageDraw.Draw(img)
        # Gradient-style inner circle
        lighter = tuple(min(255, c + 55) for c in color)
        darker  = tuple(max(0, c - 50)   for c in color)
        draw.ellipse([0,0,size-1,size-1], fill=color)
        # Subtle ring
        for i, c in enumerate([lighter, color]):
            m = (i+1)*8
            draw.ellipse([m, m, size-1-m, size-1-m], fill=c)

        # Initials
        parts    = name.replace('(','').replace(')','').split()
        initials = ''.join(p[0].upper() for p in parts[:2] if p)[:2]
        fs = size // 3
        font = None
        for fc in ['C:/Windows/Fonts/arialbd.ttf','C:/Windows/Fonts/arial.ttf',
                   'C:/Windows/Fonts/calibrib.ttf','C:/Windows/Fonts/segoeui.ttf']:
            try: font = ImageFont.truetype(fc, fs); break
            except: pass
        if font is None:
            font = ImageFont.load_default()

        bbox   = draw.textbbox((0,0), initials, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        x = (size - tw) // 2 - bbox[0]
        y = (size - th) // 2 - bbox[1]
        draw.text((x+3, y+3), initials, fill=(0,0,0,80) if hasattr(draw, 'text') else (0,0,0), font=font)
        draw.text((x, y), initials, fill=(255,255,255), font=font)

        img.save(save_path, format='PNG')
        print(f"   [AVATAR] {os.path.basename(save_path)}")
        return True
    except Exception as e:
        print(f"   [avatar err] {e}")
        return False

# ─── Download Candidate Images ────────────────────────────────────────────────
print("\n" + "="*60)
print("  DOWNLOADING CANDIDATE IMAGES")
print("="*60)

downloaded = {}
for i, cand in enumerate(CANDIDATES):
    safe_name  = cand['name'].lower().replace(' ','_').replace('(','').replace(')','')
    file_path  = os.path.join(CAND_IMG_DIR, f"{safe_name}.jpg")
    static_url = f"/static/candidates/images/{safe_name}.jpg"
    
    print(f"\n[{i+1}/{len(CANDIDATES)}] {cand['name']} ({cand['party']}) ...")
    
    success = False
    # Try Wikipedia REST API
    thumb_url = get_wiki_thumbnail(cand['wiki'])
    if thumb_url:
        print(f"   [wiki] {thumb_url[:70]}...")
        success = download_image_file(thumb_url, file_path)

    # Fallback: Pillow avatar
    if not success:
        avatar_path = file_path.replace('.jpg', '.png')
        static_url  = static_url.replace('.jpg', '.png')
        color = cand.get('color', AVATAR_COLORS_LIST[i % len(AVATAR_COLORS_LIST)])
        success = make_avatar(cand['name'], color, avatar_path)
        if success:
            file_path = avatar_path

    downloaded[cand['name']] = {
        'file': file_path,
        'static_url': static_url,
        'success': success,
    }
    time.sleep(0.3)  # Polite delay

# ─── Update Django DB with new file paths ────────────────────────────────────
print("\n" + "="*60)
print("  UPDATING DJANGO DATABASE")
print("="*60)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

try:
    import django
    django.setup()
    from apps.elections.models import Candidate

    # Map DB candidate names to downloaded images
    NAME_MAP = {
        "Chandra Babu Naidu": "Chandra Babu Naidu",
        "Jagan":              "Jagan",
        "Pawan Kalyan (Janasena)": "Pawan Kalyan",
        "Revanth Reddy":      "Revanth Reddy",
        "KCR":                "KCR",
        "Vijay":              "Vijay",
        "Stalin":             "Stalin",
    }

    updated = 0
    for cand_obj in Candidate.objects.all():
        map_name = NAME_MAP.get(cand_obj.name, cand_obj.name)
        info     = downloaded.get(map_name)
        if info and info['success']:
            # Store the /static/ URL path (not base64)
            cand_obj.photo_url = info['static_url']
            cand_obj.save()
            print(f"   [DB] {cand_obj.name} -> {info['static_url']}")
            updated += 1

    print(f"\n   Done! {updated} candidates updated in DB.")

except Exception as e:
    print(f"   [Django error] {e}")

print("\n" + "="*60)
print("  STRUCTURE COMPLETE")
print("="*60)
print(f"  candidates/images/ -> {CAND_IMG_DIR}")
print(f"  voting/            -> {VOTING_DIR}")
print(f"  voting/images/     -> {VOTING_IMG_DIR}")
print("\n  Restart Django server and refresh the admin dashboard.")
