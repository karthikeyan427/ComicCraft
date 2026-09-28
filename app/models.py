import os
from pydantic import BaseModel, Field
from typing import List, Optional

class PromptRequest(BaseModel):
    story_prompt: str = Field(..., description="Main story idea or prompt for the comic")
    character_name: str = Field(..., description="Hero / main character name")
    setting: str = Field("Enchanted Forest", description="Setting/Location (e.g., forest, school, space, city)")
    tone: str = Field("Dramatic", description="Mood of the story (e.g., dramatic, funny, poetic)")
    art_style: str = Field("Comic Book", description="Visual style preference (e.g., anime, comic book, pixel art, realistic)")
    num_panels: Optional[int] = Field(5, description="Number of comic panels (default: 5)")

class PanelOutline(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str

class PanelStory(BaseModel):
    panel_number: int
    caption: str
    narration: str
    dialogue: str

class ComicPanelLayout(BaseModel):
    panel_number: int
    title: str
    image_path: str
    scene_description: str
    caption: str
    narration: str
    dialogue: str
    image_prompt: str

class ComicResponse(BaseModel):
    status: str
    title: str
    character_name: str
    setting: str
    tone: str
    art_style: str
    layout: List[ComicPanelLayout]
    pdf_url: str
    pdf_filename: str
