import os
import logging
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Request, Form, HTTPException, Query, status
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.models import PromptRequest, ComicResponse
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story
from app.image_generator import generate_image
from app.layout_builder import build_comic_layout
from app.exporters import save_pdf

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Loads the homepage where users can input story details to create a comic."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form("Enchanted Forest"),
    tone: str = Form("Dramatic"),
    art_style: str = Form("Comic Book"),
    num_panels: int = Form(5)
):
    """
    Handles form submission, orchestrates the multi-agent AI pipeline:
    1. Gemini Flash -> 5-panel structured outline
    2. Gemini Pro -> Narrations and character dialogues
    3. Stable Diffusion -> Generates comic-style panel illustrations
    4. Layout Builder -> Structures panels into unified layout
    5. Exporters -> Generates professional PDF
    Renders comic_preview.html for sequential viewing.
    """
    try:
        num_panels = max(1, min(num_panels, 6))

        # Step 1: Generate outline with Gemini Flash
        outline = generate_outline(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
            num_panels=num_panels
        )

        # Step 2: Generate story narration & dialogue with Gemini Pro
        story_data = generate_story(
            outline=outline,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )

        # Step 3: Generate comic panel illustrations
        image_paths = []
        for panel in outline:
            img_path = generate_image(
                prompt=panel.get("image_prompt", story_prompt),
                art_style=art_style,
                panel_num=panel.get("panel_number", 1)
            )
            image_paths.append(img_path)

        # Step 4: Assemble comic layout
        layout = build_comic_layout(
            outline=outline,
            story=story_data,
            image_paths=image_paths
        )

        # Step 5: Export to PDF
        pdf_path = save_pdf(
            layout=layout,
            comic_title=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style
        )
        pdf_filename = Path(pdf_path).name

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "story_prompt": story_prompt,
                "character_name": character_name,
                "setting": setting,
                "tone": tone,
                "art_style": art_style,
                "layout": layout,
                "pdf_url": pdf_path,
                "pdf_filename": pdf_filename
            }
        )
    except Exception as e:
        logger.error(f"Error generating comic: {e}", exc_info=True)
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "error": f"An error occurred while crafting your comic: {str(e)}",
                "story_prompt": story_prompt,
                "character_name": character_name
            },
            status_code=500
        )


@router.post("/generate-comic/json", response_model=ComicResponse)
async def generate_comic_json(payload: PromptRequest):
    """
    API endpoint accepting a JSON payload, triggers comic generation,
    and returns comic layout data and the generated PDF path.
    """
    try:
        num_panels = payload.num_panels or 5
        outline = generate_outline(
            story_prompt=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
            num_panels=num_panels
        )

        story_data = generate_story(
            outline=outline,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style
        )

        image_paths = []
        for panel in outline:
            img_path = generate_image(
                prompt=panel.get("image_prompt", payload.story_prompt),
                art_style=payload.art_style,
                panel_num=panel.get("panel_number", 1)
            )
            image_paths.append(img_path)

        layout = build_comic_layout(
            outline=outline,
            story=story_data,
            image_paths=image_paths
        )

        pdf_path = save_pdf(
            layout=layout,
            comic_title=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style
        )
        pdf_filename = Path(pdf_path).name

        return ComicResponse(
            status="success",
            title=payload.story_prompt,
            character_name=payload.character_name,
            setting=payload.setting,
            tone=payload.tone,
            art_style=payload.art_style,
            layout=layout,
            pdf_url=pdf_path,
            pdf_filename=pdf_filename
        )
    except Exception as e:
        logger.error(f"Error in JSON comic generation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate comic: {str(e)}"
        )


@router.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    """Serves the generated PDF file for download."""
    clean_name = Path(filename).name
    file_path = Path("static/exports") / clean_name
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested PDF was not found.")
    return FileResponse(
        path=file_path,
        filename=clean_name,
        media_type="application/pdf"
    )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(
    request: Request,
    pdf_filename: Optional[str] = Query(None),
    title: Optional[str] = Query("Your Comic Story")
):
    """
    Displays a success confirmation page after the comic is downloaded,
    with a call-to-action button to create another comic.
    """
    pdf_url = f"/static/exports/{pdf_filename}" if pdf_filename else None
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "title": title,
            "pdf_filename": pdf_filename,
            "pdf_url": pdf_url
        }
    )


@router.api_route("/test-image", methods=["GET", "POST"])
async def test_image(
    request: Request,
    prompt: Optional[str] = Query(None),
    art_style: Optional[str] = Query("Comic Book")
):
    """
    Developer utility route to test image generation functionality separately
    with a custom prompt without running full comic creation.
    """
    if request.method == "POST":
        try:
            form = await request.form()
            prompt = form.get("prompt") or prompt
            art_style = form.get("art_style") or art_style
        except Exception:
            pass

    test_prompt = prompt or "A brave cybernetic fox exploring an illuminated neon forest"
    img_url = generate_image(prompt=test_prompt, art_style=art_style or "Comic Book", panel_num=99)

    return JSONResponse({
        "status": "success",
        "prompt": test_prompt,
        "art_style": art_style,
        "image_url": img_url,
        "message": "Image generated successfully."
    })
