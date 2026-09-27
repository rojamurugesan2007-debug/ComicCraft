# ComicCraft

ComicCraft turns a story concept into a structured, illustrated comic with a downloadable PDF. It uses FastAPI and Jinja2, Gemini or Groq for text, and Hugging Face Inference Providers for images. No local GPU is needed.

## Run locally (Windows)

1. Install Python 3.11 or newer. In PowerShell from the project root:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   Copy-Item .env.example .env
   ```

2. Add the provider keys you want to `.env`: `GEMINI_API_KEY` and/or `GROQ_API_KEY`, and `HF_API_KEY` for artwork. Never commit those values.
3. Run `uvicorn app.main:app --reload`, then visit http://127.0.0.1:8000. API docs: http://127.0.0.1:8000/docs. Health: http://127.0.0.1:8000/health.

The app gives clear configuration errors when keys are missing. Model choices are controlled by `GEMINI_MODELS` and `GROQ_MODELS`, and the requested model is validated on the server. Set `IMAGE_MODEL` to a text-to-image model enabled for your Hugging Face account.

## Railway deployment

1. Push this repository to GitHub and create a Railway project from the repository.
2. Railway builds using the root `Dockerfile`; no custom start command is required.
3. In Railway Variables configure at least one text key (`GEMINI_API_KEY` and/or `GROQ_API_KEY`) and `HF_API_KEY` (or `IMAGE_API_KEY`) for artwork. Set provider model lists and defaults if desired.
4. Generate a public domain in Railway Networking.
5. Visit `https://YOUR-DOMAIN/health`, then open the homepage and try comic generation.

Railway supplies `PORT`; the container binds Uvicorn to `0.0.0.0:$PORT`. Generated media and comic manifests are stored locally. Attach persistent storage and set `STORAGE_DIR` to the mount path to keep files across redeploys.

## Environment variables

- `GEMINI_API_KEY`, `GROQ_API_KEY`: text provider credentials; configure at least one.
- `GEMINI_MODELS`, `GROQ_MODELS`: comma-separated model IDs used for UI options and validation.
- `DEFAULT_AI_PROVIDER`, `DEFAULT_GEMINI_MODEL`, `DEFAULT_GROQ_MODEL`: default selection.
- `IMAGE_PROVIDER`: `huggingface` (default), `none`, or `disabled`.
- `HF_API_KEY` or `IMAGE_API_KEY`: Hugging Face Inference Providers key; required for images.
- `IMAGE_MODEL`: hosted text-to-image model identifier.
- `AI_TIMEOUT_SECONDS`, `IMAGE_TIMEOUT_SECONDS`, `MAX_PANELS`, `STORAGE_DIR`, `APP_ENV`: operational settings.

`POST /api/generate-comic/json` accepts `prompt`, `character_name`, `setting`, `tone`, `art_style`, `provider`, `model`, and `panel_count`, then returns a comic ID, panel content, and PDF URL.

