import os
import json
import logging
from typing import List, Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def generate_story(
    outline: List[Dict],
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> List[Dict]:
    """
    Uses Google Gemini Pro to expand comic panel outlines into immersive comic narrative,
    captions, and character dialogues for each panel.
    Returns a list of dicts:
    [
        {
            "panel_number": 1,
            "caption": "A cold whisper chills the ancient trees...",
            "narration": "Deep within the forest, an unnatural silence had taken hold.",
            "dialogue": "Character: 'Something feels different today...'"
        }, ...
    ]
    """
    api_key = os.getenv("GEMINI_API_KEY", "").strip()

    if api_key and api_key != "your_gemini_api_key_here":
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                generation_config={
                    "temperature": 0.8,
                    "top_p": 0.95,
                    "response_mime_type": "application/json",
                }
            )

            panels_brief = json.dumps(outline, indent=2)

            system_prompt = f"""
You are an award-winning comic book writer and dialogue specialist.
Expand the following {len(outline)}-panel comic outline into full comic story narration and character dialogue.

Protagonist: "{character_name}"
Setting: "{setting}"
Story Tone: "{tone}"
Visual Style: "{art_style}"

Comic Outline:
{panels_brief}

For EACH panel in the outline, generate:
1. "panel_number": matching the panel index (integer)
2. "caption": A concise, punchy comic caption setting the scene's ambient tone or sound effect (e.g. "Meanwhile, beneath the emerald canopy...", "CRACK! A sudden flash fractures the twilight.")
3. "narration": 1 to 2 sentences describing the protagonist's feelings, motives, or immediate action.
4. "dialogue": Direct character dialogue or exclamation from {character_name} or relevant characters, formatted with quotation marks (e.g., "{character_name}: 'We don't turn back now!'").

Output strictly a JSON array of objects with keys: ["panel_number", "caption", "narration", "dialogue"].
"""
            response = model.generate_content(system_prompt)
            text_response = response.text.strip()

            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]
            text_response = text_response.strip()

            data = json.loads(text_response)
            if isinstance(data, list) and len(data) > 0:
                result = []
                for idx, p in enumerate(data, 1):
                    result.append({
                        "panel_number": p.get("panel_number", idx),
                        "caption": p.get("caption", f"Panel {idx}"),
                        "narration": p.get("narration", f"{character_name} presses onward."),
                        "dialogue": p.get("dialogue", f"{character_name}: 'I won't give up.'")
                    })
                return result
        except Exception as e:
            logger.error(f"Error calling Gemini Pro API: {e}. Falling back to rich story generator.")

    # Graceful intelligent fallback
    return _generate_fallback_story(outline, character_name, setting, tone)


def _generate_fallback_story(
    outline: List[Dict],
    character_name: str,
    setting: str,
    tone: str
) -> List[Dict]:
    """Generates engaging, context-aware comic narration and dialogue for each panel."""
    story_panels = []
    
    tone_captions = {
        "dramatic": [
            f"Tension hangs thick in the air of {setting}...",
            "A startling tremor ripples through the ground.",
            "The moment of reckoning arrives without warning.",
            "Lightning arcs across the sky in a flash of raw fury!",
            "Silence descends once more, forever altered."
        ],
        "funny": [
            f"Another completely ordinary Tuesday in {setting}... or not.",
            "Whoops! That definitely wasn't supposed to happen.",
            "Well, that plan lasted for about three seconds flat.",
            "Against all logical odds, chaos turned into victory!",
            "Time to pretend this was the master plan all along."
        ],
        "poetic": [
            f"Where the shadows whisper in {setting}, history awakens.",
            "A spark of forgotten starlight illuminates the quiet path.",
            "Heartbeats synchronize with the rhythm of the unknown.",
            "In the crescendo of fate, the veil is parted.",
            "Dawn paints the horizon in hues of courage and rebirth."
        ]
    }
    
    selected_captions = tone_captions.get(tone.lower(), tone_captions["dramatic"])
    
    dialogue_samples = [
        f"{character_name}: \"There's something hidden here... I can feel it.\"",
        f"{character_name}: \"Wait, is that what I think it is?!\"",
        f"{character_name}: \"No backing down now. Let's see what you've got!\"",
        f"{character_name}: \"Hold on tight! This is it!\"",
        f"{character_name}: \"We did it. Now, what's over the next horizon?\""
    ]

    for idx, panel in enumerate(outline):
        cap = selected_captions[idx % len(selected_captions)]
        dial = dialogue_samples[idx % len(dialogue_samples)]
        narr = f"{character_name} surveys {setting}. {panel.get('scene_description', 'The story continues.')}"
        story_panels.append({
            "panel_number": panel.get("panel_number", idx + 1),
            "caption": cap,
            "narration": narr,
            "dialogue": dial
        })
        
    return story_panels
