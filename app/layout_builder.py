import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


def build_comic_layout(
    outline: List[Dict[str, Any]],
    story: List[Dict[str, Any]],
    image_paths: List[str]
) -> List[Dict[str, Any]]:
    """
    Organizes the generated images, panel outlines, and story dialogues into a
    unified, structured comic panel layout list for frontend rendering and PDF export.

    Matches each image with its corresponding panel story and outline information.
    """
    layout = []
    num_panels = len(outline)

    # Index story elements by panel_number for fast lookup
    story_map = {}
    for item in story:
        p_num = item.get("panel_number")
        if p_num is not None:
            story_map[p_num] = item

    for idx, panel_outline in enumerate(outline):
        panel_num = panel_outline.get("panel_number", idx + 1)
        story_item = story_map.get(panel_num, {})

        # Find matching image path or fallback to whatever image index is available
        if idx < len(image_paths):
            img_path = image_paths[idx]
        elif image_paths:
            img_path = image_paths[-1]
        else:
            img_path = "/static/panels/default_panel.png"

        title = panel_outline.get("title", f"Panel {panel_num}")
        scene_desc = panel_outline.get("scene_description", "The action unfolds across the panels.")
        image_prompt = panel_outline.get("image_prompt", "")

        caption = story_item.get("caption", f"Meanwhile in scene {panel_num}...")
        narration = story_item.get("narration", scene_desc)
        dialogue = story_item.get("dialogue", "")

        layout.append({
            "panel_number": panel_num,
            "title": title,
            "image_path": img_path,
            "scene_description": scene_desc,
            "caption": caption,
            "narration": narration,
            "dialogue": dialogue,
            "image_prompt": image_prompt
        })

    logger.info(f"Built comic layout with {len(layout)} structured panels.")
    return layout
