# ComicCraft - AI Comic Story Creator using Gemini Models

ComicCraft is a full-stack, AI-powered web application that automatically generates personalized comic book stories, character dialogues, and vivid comic-style illustrations based on user-provided prompts.

Built with **FastAPI**, integrated with **Google Gemini Flash** for structured story arcs, **Google Gemini Pro** for rich narration and dialogue, and **Stable Diffusion** for visual comic panels, ComicCraft streamlines the comic creation process and exports professional multi-page comic book PDFs.

---

## 🚀 Key Features

- **Automated Story Outlines**: Uses **Gemini 1.5 Flash** to structure a complete 5-panel comic arc (Beginning, Inciting Incident, Rising Action, Climax, Resolution).
- **Engaging Dialogue & Narration**: Uses **Gemini 1.5 Pro** to write expressive character speech, ambient scene captions, and sequential narration.
- **Comic-Style Illustrations**: Generates styled artwork for each panel tailored to the user's chosen art style (Comic Book, Anime, Pixel Art, Realistic, Noir).
- **Structured Layout Binding**: Programmatically binds outline, story text, dialogues, captions, and panel images using `layout_builder.py`.
- **Multi-Page PDF Export**: Compiles full comic stories with FPDF into timestamped, publication-ready PDF books with cover headers, comic badges, and narration frames.
- **Dual Interface**: Offers an intuitive, responsive web UI (Jinja2, HTML, CSS, JavaScript) alongside a RESTful JSON API for programmatic access (`/generate-comic/json`).

---

## 🛠️ Technical Architecture

```
                                  [ User / Client ]
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
            Web Browser Form                            JSON API Client
           (POST /generate)                        (POST /generate-comic/json)
                    │                                         │
                    └────────────────────┬────────────────────┘
                                         ▼
                             FastAPI Backend (routes.py)
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
  Gemini Flash                      Gemini Pro                    Stable Diffusion
 (gemini_flash.py)                (gemini_pro.py)               (image_generator.py)
   5-Panel Arc                     Dialogues &                     Comic Panel
     Outline                        Narrations                     Illustrations
        │                                │                                │
        └────────────────────────────────┴────────────────────────────────┘
                                         │
                                         ▼
                             Layout Builder (layout_builder.py)
                                         │
                                         ▼
                              PDF Exporter (exporters.py)
                             (Multi-page comic via FPDF)
                                         │
                    ┌────────────────────┴────────────────────┐
                    ▼                                         ▼
           comic_preview.html                          export_success.html
         (Sequential Review)                         (Download & Success)
```

---

## 📂 Project Directory Structure

```
ComicCraft/
├── app/
│   ├── __init__.py           # Application package initializer
│   ├── main.py               # FastAPI entry point, CORS, lifespan, static mounting
│   ├── routes.py             # Route definitions (/, /generate, /generate-comic/json, etc.)
│   ├── models.py             # Pydantic schemas (PromptRequest, ComicResponse, etc.)
│   ├── gemini_flash.py       # Gemini Flash outline generator (generate_outline)
│   ├── gemini_pro.py         # Gemini Pro story & dialogue generator (generate_story)
│   ├── image_generator.py    # Stable Diffusion / AI illustration generator (generate_image)
│   ├── layout_builder.py     # Layout assembler (build_comic_layout)
│   └── exporters.py          # PDF compilation engine using FPDF (save_pdf)
├── static/
│   ├── css/
│   │   └── style.css         # Modern comic book styling & halftone effects
│   ├── js/
│   │   └── script.js         # Preset chips autofill, progress modal, and PDF triggers
│   ├── panels/               # Storage directory for generated panel images
│   └── exports/              # Storage directory for compiled PDF comic books
├── templates/
│   ├── index.html            # Homepage with creative prompts & comic craft form
│   ├── comic_preview.html    # Panel-by-panel preview with narration and download
│   └── export_success.html   # Download confirmation with CTA to create another comic
├── .env.example              # Environment variables template
├── requirements.txt          # Python project dependencies
└── README.md                 # Complete project documentation
```

---

## 📋 Scenarios

### Scenario 1: Personalized Adventure Comic
A user enters a prompt describing their comic story: *"A brave fox exploring an enchanted forest discovers a forgotten ancient shrine."* They specify character name *"Finley"*, setting *"Enchanted Forest"*, tone *"Dramatic"*, and art style *"Anime"*. The system coordinates Gemini Flash, Gemini Pro, and Stable Diffusion to produce a personalized 5-panel comic strip with matching visual aesthetic.

### Scenario 2: Iterating Tone and Art Style
A user wants a light-hearted, cartoonish feel. On the input form, they select *"Funny"* as tone and *"Comic Book"* as art style. Upon submission, the pipeline dynamically adapts all prompts and system instructions, producing humorous dialogues and classic pop-art illustrations.

### Scenario 3: Review and PDF Download
After reviewing the on-screen preview of their comic on `/generate`, the user clicks **"Download Your Comic as PDF"**. The system invokes `exporters.py` to compile the comic into a multi-page PDF using FPDF, places images and narration onto consecutive pages, downloads the file, and seamlessly transitions to the `export_success.html` confirmation page.

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+
- Pip and Virtualenv

### 2. Clone and Setup Virtual Environment
```powershell
git clone <repo-url> ComicCraft
cd ComicCraft

# Create and activate virtual environment
python -m venv comiccraft-env
.\comiccraft-env\Scripts\activate   # On Windows
# source comiccraft-env/bin/activate # On macOS/Linux
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
HF_API_KEY=your_huggingface_api_key_here
```
*(Note: If API keys are not supplied, ComicCraft automatically provides intelligent built-in fallbacks and fast AI generation so all endpoints and features remain 100% operational).*

---

## 🚦 Running the Application Locally

Start the Uvicorn development server:
```powershell
.\comiccraft-env\Scripts\uvicorn app.main:app --reload --port 8000
```

- **Web Application**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Alternative ReDoc**: Open [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🌐 API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Loads the homepage with input form and preset suggestions |
| `POST` | `/generate` | Handles form submission, triggers AI pipeline, and renders `comic_preview.html` |
| `POST` | `/generate-comic/json` | JSON API accepting `PromptRequest` and returning structured `ComicResponse` |
| `GET` | `/download-pdf/{filename}` | Downloads a specific generated PDF comic book |
| `GET` | `/export-success` | Renders the export confirmation page |
| `GET / POST` | `/test-image` | Developer utility to test prompt-to-image generation directly |

### Example JSON API Request
```bash
curl -X POST "http://127.0.0.1:8000/generate-comic/json" \
     -H "Content-Type: application/json" \
     -d '{
       "story_prompt": "A brave fox exploring an enchanted forest",
       "character_name": "Finley",
       "setting": "Enchanted Forest",
       "tone": "Dramatic",
       "art_style": "Anime",
       "num_panels": 5
     }'
```

---

## 🏆 Project Milestones Summary

- **Milestone 1**: Model Selection & Architecture (Gemini Flash, Gemini Pro, Stable Diffusion, FastAPI).
- **Milestone 2**: Core Functionalities (`gemini_flash.py`, `gemini_pro.py`, `image_generator.py`, `layout_builder.py`, `exporters.py`).
- **Milestone 3**: Routing & Request Processing (`app/routes.py`, `PromptRequest` schema, error handling).
- **Milestone 4**: Frontend Development (`index.html`, `comic_preview.html`, `export_success.html`, custom comic design system in `style.css`, and `script.js`).
- **Milestone 5**: Local Deployment & Verification (Uvicorn ASGI runner, Swagger docs, cross-browser validation).
