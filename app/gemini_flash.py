import os
import json
import logging
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def get_flash_model():
    """Initializes and returns the Gemini Flash generative model."""
    try:
        return genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        logger.warning(f"Failed to load gemini-1.5-flash, trying fallback: {e}")
        try:
            return genai.GenerativeModel("gemini-flash")
        except Exception:
            return None


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    num_panels: int = 5
) -> List[Dict]:
    """
    Generates a structured multi-panel comic outline using Google Gemini Flash.
    Each panel contains:
    - panel_number: int (1 to num_panels)
    - title: str
    - scene_description: str (atmospheric setting and character action)
    - image_prompt: str (descriptive text to feed into the image generator in the requested art style)
    """
    num_panels = num_panels or 5
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if api_key and api_key != "your_gemini_api_key_here":
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "response_mime_type": "application/json",
                }
            )

            system_prompt = f"""
You are a master comic book director and storyboard artist.
Create a structured {num_panels}-panel comic outline based on the user's idea.

Story Idea: "{story_prompt}"
Main Character: "{character_name}"
Setting: "{setting}"
Story Tone: "{tone}"
Visual Art Style: "{art_style}"

Requirements:
- Exactly {num_panels} panels with a clear narrative arc (Beginning, Inciting Incident, Rising Action, Climax, Resolution).
- Output strictly a JSON array of objects with the following keys for each panel:
  - "panel_number": integer from 1 to {num_panels}
  - "title": a catchy title for the panel (e.g. "Panel 1: The Whispering Woods")
  - "scene_description": a vivid 2-3 sentence description of the environment, action, and mood
  - "image_prompt": a detailed prompt optimized for text-to-image AI (Stable Diffusion). Must include specific details about {character_name}, the background in {setting}, camera angle (e.g. close-up, wide-shot, dynamic low-angle), lighting, and art style "{art_style}". Avoid vague words.

Return ONLY the JSON array.
"""
            response = model.generate_content(system_prompt)
            text_response = response.text.strip()
            
            # Clean possible markdown fence
            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            text_response = text_response.strip()

            data = json.loads(text_response)
            if isinstance(data, list) and len(data) > 0:
                # Ensure all required fields exist
                sanitized = []
                for idx, p in enumerate(data, 1):
                    sanitized.append({
                        "panel_number": p.get("panel_number", idx),
                        "title": p.get("title", f"Panel {idx}: The Journey Begins"),
                        "scene_description": p.get("scene_description", "A mysterious scene unfolds."),
                        "image_prompt": p.get("image_prompt", f"Comic art of {character_name} in {setting}, {art_style} style, detailed background")
                    })
                return sanitized[:num_panels]
        except Exception as e:
            logger.error(f"Error calling Gemini Flash API: {e}. Falling back to intelligent outline generator.")

    # Graceful intelligent fallback if API key is missing or errored
    return _generate_fallback_outline(story_prompt, character_name, setting, tone, art_style, num_panels)


def _generate_fallback_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
    num_panels: int = 5
) -> List[Dict]:
    """Generates a cohesive, story-specific outline when external API is unreachable."""
    templates = [
        {
            "step": "Introduction",
            "title_suffix": "The Beginning of the Quest",
            "desc": f"{character_name} stands amidst {setting}, sensing an uncanny disturbance in the air. The mood is unmistakably {tone.lower()} as an unexpected discovery catches their eye.",
            "prompt_extra": f"establishing wide shot, {character_name} looking curious, detailed scenic {setting}, cinematic atmospheric lighting, {art_style} style"
        },
        {
            "step": "Discovery",
            "title_suffix": "A Hidden Clue",
            "desc": f"Upon closer inspection, {character_name} stumbles upon a glowing anomaly embedded in the heart of {setting}. Whispers resonate through the silence.",
            "prompt_extra": f"medium shot, {character_name} discovering a glowing mystical artifact, dramatic shadows, {art_style} graphic novel style"
        },
        {
            "step": "Confrontation",
            "title_suffix": "Facing the Trial",
            "desc": f"Suddenly, a daunting challenge emerges directly in front of {character_name}. With unwavering resolve, they prepare to take action as the stakes escalate.",
            "prompt_extra": f"dynamic action angle, intense face expression, swirling energy, high contrast comic illustration, {art_style} style"
        },
        {
            "step": "Climax",
            "title_suffix": "The Decisive Turn",
            "desc": f"In a breathtaking display of courage, {character_name} channels their inner strength to resolve the crisis unfolding in {setting}.",
            "prompt_extra": f"epic hero moment, vibrant particle effects, masterpiece comic panel, power surge, {art_style} style"
        },
        {
            "step": "Resolution",
            "title_suffix": "A New Dawn Ahead",
            "desc": f"As quiet returns to {setting}, {character_name} gazes into the horizon with newfound wisdom and an adventurous grin. The adventure is just beginning.",
            "prompt_extra": f"cinematic sunset golden hour, peaceful heroic pose, panoramic view of {setting}, detailed comic art, {art_style} style"
        }
    ]

    outline = []
    for i in range(min(num_panels, len(templates))):
        t = templates[i]
        outline.append({
            "panel_number": i + 1,
            "title": f"Panel {i + 1}: {t['title_suffix']}",
            "scene_description": t["desc"],
            "image_prompt": f"Masterpiece comic art: {story_prompt}. {t['prompt_extra']}. Featuring {character_name}, {setting}. Art style: {art_style}, 8k resolution, comic book panel."
        })
    return outline
