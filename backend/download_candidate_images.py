"""
Candidate Image Downloader using Pillow (PIL)
============================================
Downloads real politician/candidate images via Wikipedia REST API,
resizes them to uniform 200x200 thumbnails using Pillow,
and saves them as base64 data URIs in Candidate.photo_url.

Run this AFTER migrations:
    cd backend
    python -X utf8 download_candidate_images.py
"""

import os
import sys
import io
import base64
import json
import urllib.request
import urllib.parse

# Fix Unicode output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from apps.elections.models import Candidate

# ----------------------------------------------------------------
# Pillow import
# ----------------------------------------------------------------
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    print("Pillow not found. Run: pip install Pillow")
    PILLOW_AVAILABLE = False


# ----------------------------------------------------------------
# Wikipedia article names for each candidate (for REST API lookup)
# ----------------------------------------------------------------
WIKIPEDIA_PAGES = {
    "Chandra Babu Naidu": "N._Chandrababu_Naidu",
    "Jagan": "Y._S._Jagan_Mohan_Reddy",
    "Pawan Kalyan (Janasena)": "Pawan_Kalyan",
    "Revanth Reddy": "A._Revanth_Reddy",
    "KCR": "K._Chandrashekar_Rao",
    "Vijay": "Vijay_(actor)",
    "Stalin": "M._K._Stalin",
}

# ----------------------------------------------------------------
# Backup direct URLs (Wikimedia thumbnails with Referer)  
# ----------------------------------------------------------------
DIRECT_BACKUP_URLS = {
    "Chandra Babu Naidu": "https://en.wikipedia.org/wiki/N._Chandrababu_Naidu#/media/File:Chandrababu_Naidu_Official_Photo.jpg",
    "Jagan": "https://en.wikipedia.org/wiki/Y._S._Jagan_Mohan_Reddy",
    "Pawan Kalyan (Janasena)": "https://en.wikipedia.org/wiki/Pawan_Kalyan",
}


def make_headers():
    return {
        'User-Agent': 'OnlineVotingSystem/1.0 (educational project; contact@example.com)',
        'Accept': 'application/json',
        'Referer': 'https://en.wikipedia.org/',
    }


def fetch_wikipedia_thumbnail(page_name):
    """Use Wikipedia REST API to get page thumbnail URL."""
    api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_name)}"
    print(f"  [Wikipedia API] Fetching: {api_url}")
    try:
        req = urllib.request.Request(api_url, headers=make_headers())
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        
        # Try thumbnail first, then originalimage
        if 'thumbnail' in data:
            url = data['thumbnail'].get('source', '')
            if url:
                print(f"  [Wikipedia API] Found thumbnail: {url[:80]}...")
                return url
        if 'originalimage' in data:
            url = data['originalimage'].get('source', '')
            if url:
                print(f"  [Wikipedia API] Found original: {url[:80]}...")
                return url
    except Exception as e:
        print(f"  [Wikipedia API] Error: {e}")
    return None


def download_and_process_image(url, candidate_name, size=(200, 200)):
    """Download image from URL, crop/resize to square thumbnail using Pillow."""
    print(f"  Downloading from: {url[:80]}...")

    try:
        headers = make_headers()
        headers['Accept'] = 'image/jpeg,image/png,image/*'
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            img_data = response.read()

        # Open with Pillow
        img = Image.open(io.BytesIO(img_data)).convert('RGB')

        # Smart crop to square (center crop)
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 3  # Slightly upper crop for faces
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))

        # Resize to target size with high quality
        img = img.resize(size, Image.LANCZOS)

        # Save to bytes as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=88, optimize=True)
        img_bytes = buffer.getvalue()

        # Convert to base64 data URI
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        data_uri = f"data:image/jpeg;base64,{b64}"

        size_kb = len(img_bytes) // 1024
        print(f"  Processed: {size[0]}x{size[1]}px, {size_kb}KB compressed")
        return data_uri

    except Exception as e:
        print(f"  Download failed: {e}")
        return None


# ----------------------------------------------------------------
# Pillow-generated initials avatar (indigo gradient)
# ----------------------------------------------------------------
AVATAR_COLORS = [
    (79, 70, 229),   # Indigo
    (16, 185, 129),  # Emerald
    (245, 158, 11),  # Amber
    (239, 68, 68),   # Red
    (139, 92, 246),  # Violet
    (6, 182, 212),   # Cyan
    (236, 72, 153),  # Pink
]

def generate_pillow_avatar(name, index=0, size=200):
    """Generate a beautiful circular initials avatar using Pillow."""
    if not PILLOW_AVAILABLE:
        return None

    try:
        # Choose color based on index
        bg_color = AVATAR_COLORS[index % len(AVATAR_COLORS)]
        # Create RGBA image for transparency
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw gradient-like circle (dark outer ring)
        darker = tuple(max(0, c - 40) for c in bg_color)
        draw.ellipse([0, 0, size-1, size-1], fill=bg_color + (255,))
        # Inner highlight
        margin = size // 10
        lighter = tuple(min(255, c + 60) for c in bg_color)
        draw.ellipse([margin, margin, size-1-margin, size-1-margin],
                     fill=lighter + (255,))
        # Re-draw main fill
        margin2 = margin + 4
        draw.ellipse([margin2, margin2, size-1-margin2, size-1-margin2],
                     fill=bg_color + (255,))

        # Get initials (max 2 chars)
        parts = name.replace('(', '').replace(')', '').split()
        initials = ''.join(p[0].upper() for p in parts[:2] if p)[:2]

        # Try to find a font
        font = None
        font_size = size // 3
        font_candidates = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            'C:/Windows/Fonts/segoeui.ttf',
            'C:/Windows/Fonts/tahoma.ttf',
        ]
        for fc in font_candidates:
            try:
                font = ImageFont.truetype(fc, font_size)
                break
            except:
                pass

        if font is None:
            font = ImageFont.load_default()

        # Measure text and center it
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2 - bbox[0]
        y = (size - text_h) // 2 - bbox[1]

        # Draw text shadow
        draw.text((x + 2, y + 2), initials, fill=(0, 0, 0, 80), font=font)
        # Draw white text
        draw.text((x, y), initials, fill=(255, 255, 255, 255), font=font)

        # Convert to RGB JPEG
        rgb_img = Image.new('RGB', (size, size), bg_color)
        rgb_img.paste(img, mask=img.split()[3])

        buffer = io.BytesIO()
        rgb_img.save(buffer, format='JPEG', quality=90)
        img_bytes = buffer.getvalue()
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{b64}"

    except Exception as e:
        print(f"  Avatar generation error: {e}")
        return None


def run():
    """Main function: try Wikipedia API first, then Pillow avatar fallback."""
    if not PILLOW_AVAILABLE:
        print("Pillow is required. Install: pip install Pillow")
        sys.exit(1)

    print("\nCandidate Image Downloader (Pillow CMS + Wikipedia API)")
    print("=" * 58)

    candidates = list(Candidate.objects.all())

    if not candidates:
        print("No candidates found. Run the server first to seed data.")
        return

    updated = 0
    real_photos = 0
    avatars = 0

    for idx, cand in enumerate(candidates):
        print(f"\n[{idx+1}/{len(candidates)}] {cand.name} ({cand.party_affinity})")

        data_uri = None

        # Step 1: Try Wikipedia REST API thumbnail
        wiki_page = WIKIPEDIA_PAGES.get(cand.name)
        if wiki_page:
            thumb_url = fetch_wikipedia_thumbnail(wiki_page)
            if thumb_url:
                data_uri = download_and_process_image(thumb_url, cand.name)
                if data_uri:
                    real_photos += 1
                    print(f"  Real photo saved!")

        # Step 2: Pillow avatar fallback
        if not data_uri:
            print(f"  Generating Pillow avatar for '{cand.name}'...")
            data_uri = generate_pillow_avatar(cand.name, index=idx)
            if data_uri:
                avatars += 1
                print(f"  Avatar saved!")

        if data_uri:
            cand.photo_url = data_uri
            cand.save()
            updated += 1
        else:
            print(f"  Could not generate any image.")

    print(f"\n{'='*58}")
    print(f"Done! Updated: {updated} | Real Photos: {real_photos} | Avatars: {avatars}")
    print("Restart Django server to see images in the admin dashboard.")


if __name__ == '__main__':
    run()

============================================
Downloads real politician/candidate images from public URLs,
resizes them to uniform 200x200 thumbnails using Pillow,
and saves them as base64 data URIs in Candidate.photo_url.

Run this AFTER migrations:
    cd backend
    python download_candidate_images.py
"""

import os
import sys
import io
import base64
import urllib.request

# Fix Unicode output on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


# Setup Django environment
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django
django.setup()

from apps.elections.models import Candidate

# ----------------------------------------------------------------
# Pillow import - will use it for resizing/cropping to thumbnail
# ----------------------------------------------------------------
try:
    from PIL import Image, ImageDraw, ImageFont
    PILLOW_AVAILABLE = True
except ImportError:
    print("⚠️  Pillow not found. Run: pip install Pillow")
    PILLOW_AVAILABLE = False


# ----------------------------------------------------------------
# Candidate image sources — using direct accessible image search APIs
# These use Wikipedia's actual image server paths with the /thumb/ prefix
# ----------------------------------------------------------------
CANDIDATE_IMAGES = {
    # AP candidates — using Wikipedia REST API
    "Chandra Babu Naidu": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Chandrababu_Naidu_Official_Photo.jpg/200px-Chandrababu_Naidu_Official_Photo.jpg",
    "Jagan": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/YS_Jagan_Mohan_Reddy_official_photo.jpg/200px-YS_Jagan_Mohan_Reddy_official_photo.jpg",
    "Pawan Kalyan (Janasena)": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Pawan_Kalyan_at_Jansena_Launch_Cropped.jpg/200px-Pawan_Kalyan_at_Jansena_Launch_Cropped.jpg",
    # TG candidates
    "Revanth Reddy": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Revanth_Reddy_-_Chief_Minister_of_Telangana.jpg/200px-Revanth_Reddy_-_Chief_Minister_of_Telangana.jpg",
    "KCR": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/K._Chandrashekar_Rao_2019.jpg/200px-K._Chandrashekar_Rao_2019.jpg",
    # Chennai candidates
    "Vijay": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Vijay_at_Bigil_press_meet_%28cropped%29.jpg/200px-Vijay_at_Bigil_press_meet_%28cropped%29.jpg",
    "Stalin": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/MK_Stalin_CM_TN.jpg/200px-MK_Stalin_CM_TN.jpg",
}


def make_avatar_placeholder(name, size=200):
    """Generate a colored initials avatar using Pillow as fallback."""
    img = Image.new('RGB', (size, size), color=(79, 70, 229))  # indigo
    draw = ImageDraw.Draw(img)
    
    # Get initials
    parts = name.split()
    initials = "".join(p[0].upper() for p in parts[:2] if p)
    
    # Draw circle background
    draw.ellipse([0, 0, size-1, size-1], fill=(79, 70, 229))
    
    # Draw text (centered)
    font_size = size // 3
    try:
        from PIL import ImageFont
        # Try to use a system font
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()
    except:
        font = None
    
    if font:
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2
        draw.text((x, y), initials, fill='white', font=font)
    else:
        # Basic positioning
        draw.text((size//4, size//4), initials, fill='white')
    
    return img


def download_and_process_image(url, candidate_name, size=(200, 200)):
    """Download image from URL, crop/resize to square thumbnail using Pillow."""
    print(f"  📥 Downloading image for {candidate_name}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            img_data = response.read()
        
        # Open with Pillow
        img = Image.open(io.BytesIO(img_data)).convert('RGB')
        
        # Smart crop to square (center crop)
        w, h = img.size
        min_dim = min(w, h)
        left = (w - min_dim) // 2
        top = (h - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        img = img.crop((left, top, right, bottom))
        
        # Resize to 200x200 with high quality
        img = img.resize(size, Image.LANCZOS)
        
        # Save to bytes as JPEG
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        img_bytes = buffer.getvalue()
        
        # Convert to base64 data URI
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        data_uri = f"data:image/jpeg;base64,{b64}"
        
        print(f"  ✅ Image processed ({len(img_bytes)//1024}KB → {size[0]}x{size[1]}px)")
        return data_uri
        
    except Exception as e:
        print(f"  ⚠️  Failed to download: {e}")
        return None


def generate_fallback_avatar(name, size=(200, 200)):
    """Generate a Pillow-based initials avatar as fallback."""
    if not PILLOW_AVAILABLE:
        return None
    
    try:
        img = make_avatar_placeholder(name, size[0])
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        b64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        print(f"  ⚠️  Avatar generation failed: {e}")
        return None


def run():
    """Main function: download images for all candidates."""
    if not PILLOW_AVAILABLE:
        print("❌ Pillow is required. Install it with: pip install Pillow")
        sys.exit(1)
    
    print("\n🖼️  Candidate Image Downloader (Pillow CMS)")
    print("=" * 50)
    
    candidates = Candidate.objects.all()
    
    if not candidates.exists():
        print("⚠️  No candidates found. Run the server first to seed data.")
        return
    
    updated = 0
    skipped = 0
    
    for cand in candidates:
        print(f"\n👤 Processing: {cand.name} ({cand.party_affinity})")
        
        # Try to download from known URLs
        img_url = CANDIDATE_IMAGES.get(cand.name)
        
        if img_url:
            data_uri = download_and_process_image(img_url, cand.name)
        else:
            print(f"  ⚠️  No image URL defined for '{cand.name}', generating avatar...")
            data_uri = None
        
        # Fallback: generate initials avatar
        if not data_uri:
            print(f"  🎨 Generating Pillow initials avatar for '{cand.name}'...")
            data_uri = generate_fallback_avatar(cand.name)
        
        if data_uri:
            cand.photo_url = data_uri
            cand.save()
            print(f"  💾 Saved to database!")
            updated += 1
        else:
            print(f"  ❌ Could not generate image for {cand.name}")
            skipped += 1
    
    print(f"\n{'='*50}")
    print(f"✅ Done! Updated: {updated} | Skipped: {skipped}")
    print("🚀 Restart the Django server to see images in the admin dashboard.")


if __name__ == '__main__':
    run()
