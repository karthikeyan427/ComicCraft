import os
import re
import time
import uuid
import logging
import requests
from urllib.parse import quote
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

STATIC_PANELS_DIR = Path("static/panels")
STATIC_PANELS_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_filename(prompt: str, max_length: int = 30) -> str:
    """Sanitizes prompt string into a safe, clean file slug."""
    clean = re.sub(r'[^a-zA-Z0-9_\- ]', '', prompt)
    clean = clean.strip().replace(' ', '_').lower()
    return clean[:max_length] or "comic_panel"


def generate_image(
    prompt: str,
    art_style: str = "Comic Book",
    panel_num: int = 1,
    output_dir: str = "static/panels"
) -> str:
    """
    Generates a comic-style illustration based on the provided prompt and art style.
    Saves image into the static/panels directory and returns the relative web URL.
    
    Generation cascade:
    1. Hugging Face Inference API (if HF_API_KEY configured)
    2. Cloud AI Generator (Pollinations Flux / Stable Diffusion - fast & high quality)
    3. High-Quality Pillow Comic Panel Generator (deterministic, offline fallback)
    """
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    timestamp = int(time.time())
    unique_id = uuid.uuid4().hex[:6]
    slug = sanitize_filename(prompt, 20)
    filename = f"panel_{panel_num}_{slug}_{timestamp}_{unique_id}.png"
    file_path = target_dir / filename

    enhanced_prompt = f"{prompt}, artistic {art_style} style, comic book panel illustration, vivid colors, dynamic composition, dramatic lighting, highly detailed graphic novel art, 8k resolution"

    # 1. Try Hugging Face API if HF_API_KEY or HF_TOKEN is present
    hf_token = os.getenv("HF_API_KEY") or os.getenv("HF_TOKEN")
    if hf_token and hf_token != "your-huggingface-api-key-here":
        try:
            hf_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
            headers = {"Authorization": f"Bearer {hf_token}"}
            payload = {"inputs": enhanced_prompt}
            response = requests.post(hf_url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                with open(file_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Generated panel {panel_num} via Hugging Face Diffusers API")
                return f"/static/panels/{filename}"
        except Exception as e:
            logger.warning(f"Hugging Face API failed: {e}. Trying cloud AI generator.")

    # 2. Try High-Quality Cloud AI Endpoint (Pollinations AI) with responsive timeout
    try:
        encoded = quote(enhanced_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=768&height=512&model=flux&seed={uuid.uuid4().int % 100000}&nologo=true"
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200 and len(resp.content) > 1000:
            with open(file_path, "wb") as f:
                f.write(resp.content)
            logger.info(f"Generated panel {panel_num} via AI Image Generator")
            return f"/static/panels/{filename}"
    except Exception as e:
        logger.warning(f"Cloud AI image generation timed out/failed: {e}. Using artistic PIL fallback.")

    # 3. Artistic Pillow Fallback (Comic panel placeholder with styled graphics)
    _create_stylized_comic_panel(file_path, prompt, art_style, panel_num)
    return f"/static/panels/{filename}"


def _create_stylized_comic_panel(file_path: Path, prompt: str, art_style: str, panel_num: int):
    """Creates a stylized comic book illustration card with comic dots, gradient and bold typography."""
    width, height = 768, 512
    img = Image.new("RGB", (width, height), color=(18, 20, 32))
    draw = ImageDraw.Draw(img)

    # Dynamic comic style color palettes
    palettes = {
        "anime": ((30, 20, 50), (230, 60, 115), (70, 190, 255)),
        "comic book": ((20, 24, 45), (255, 180, 0), (235, 50, 75)),
        "pixel art": ((15, 15, 30), (0, 230, 180), (160, 50, 240)),
        "realistic": ((25, 28, 36), (180, 140, 90), (100, 150, 200)),
        "poetic": ((20, 30, 45), (140, 120, 220), (255, 215, 120))
    }
    key = art_style.lower()
    bg_dark, accent1, accent2 = palettes.get(key, ((20, 24, 45), (255, 180, 0), (235, 50, 75)))

    # Draw gradient background
    for y in range(height):
        r = int(bg_dark[0] + (accent1[0] - bg_dark[0]) * (y / height) * 0.4)
        g = int(bg_dark[1] + (accent1[1] - bg_dark[1]) * (y / height) * 0.4)
        b = int(bg_dark[2] + (accent1[2] - bg_dark[2]) * (y / height) * 0.4)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Comic Action Rays from center
    cx, cy = width // 2, height // 2
    for angle_deg in range(0, 360, 15):
        import math
        rad = math.radians(angle_deg)
        x_end = cx + int(600 * math.cos(rad))
        y_end = cy + int(600 * math.sin(rad))
        draw.line([(cx, cy), (x_end, y_end)], fill=(accent1[0], accent1[1], accent1[2], 40), width=2)

    # Comic panel border (Bold Ink)
    border_width = 8
    draw.rectangle([border_width, border_width, width - border_width, height - border_width], outline=(255, 255, 255), width=4)
    draw.rectangle([border_width + 4, border_width + 4, width - border_width - 4, height - border_width - 4], outline=(0, 0, 0), width=border_width)

    # Panel Badge
    badge_w, badge_h = 180, 44
    draw.rectangle([20, 20, 20 + badge_w, 20 + badge_h], fill=accent1, outline=(0, 0, 0), width=3)
    
    # Try default font
    try:
        font_large = ImageFont.load_default(size=24)
        font_small = ImageFont.load_default(size=16)
    except TypeError:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    draw.text((32, 28), f"PANEL {panel_num} • {art_style.upper()}", fill=(0, 0, 0), font=font_large)

    # Center Speech/Action Banner
    banner_w, banner_h = 680, 120
    bx = (width - banner_w) // 2
    by = height - banner_h - 30
    draw.rectangle([bx, by, bx + banner_w, by + banner_h], fill=(15, 18, 25), outline=accent2, width=3)

    # Wrap prompt text
    words = prompt.split()
    line1 = " ".join(words[:10])
    line2 = " ".join(words[10:20])
    if len(words) > 20:
        line2 += "..."

    draw.text((bx + 20, by + 20), "SCENE VISUALIZATION:", fill=accent1, font=font_small)
    draw.text((bx + 20, by + 48), line1, fill=(240, 240, 250), font=font_small)
    if line2:
        draw.text((bx + 20, by + 74), line2, fill=(200, 205, 220), font=font_small)

    img.save(file_path, "PNG")
