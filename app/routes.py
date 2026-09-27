"""FastAPI routes for comic creation and exports."""
import logging, time, uuid
from pathlib import Path
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool
from app.ai.base import ProviderError
from app.ai.factory import get_provider
from app.config import ROOT_DIR, get_settings
from app.image.factory import get_image_provider
from app.image.provider import ImageProviderError
from app.prompts.image import consistent_image_prompt
from app.schemas import ComicRequest, ComicStory, GenerationResponse, ImageTestRequest, ProviderInfo
from app.services.exporters import export_pdf
from app.services.files import load_manifest, safe_id, save_manifest, storage_paths

logger=logging.getLogger("comiccraft")
router=APIRouter()
templates=Jinja2Templates(directory=str(ROOT_DIR/"templates"))

def _build_comic(payload: ComicRequest) -> GenerationResponse:
    started=time.monotonic(); comic_id=str(uuid.uuid4())
    logger.info("generation started provider=%s model=%s panels=%s",payload.provider,payload.model or "default",payload.panel_count)
    try:
        provider=get_provider(payload.provider,payload.model)
        image_provider=get_image_provider()
        outline=provider.generate_outline(payload)
        story=provider.generate_story(payload,outline)
        panels_dir,exports_dir,_=storage_paths(); image_paths={}
        for panel in story.panels:
            image_bytes=image_provider.generate(consistent_image_prompt(payload,panel))
            image_path=panels_dir/f"{comic_id}_{panel.panel_number:02d}.png"
            image_path.write_bytes(image_bytes); image_paths[panel.panel_number]=image_path
            panel.image_url=f"/media/panels/{image_path.name}"
            logger.info("panel image generated comic_id=%s panel=%s",comic_id,panel.panel_number)
        story.metadata={"provider":payload.provider,"model":payload.model or get_settings().default_model_for(payload.provider),"art_style":payload.art_style}
        pdf_path=exports_dir/f"comiccraft_{comic_id}.pdf"
        export_pdf(story,image_paths,pdf_path)
        response=GenerationResponse(comic_id=comic_id,comic=story,pdf_url=f"/export/{comic_id}")
        save_manifest(comic_id,{"comic":story.model_dump(),"pdf":pdf_path.name})
        logger.info("generation complete comic_id=%s duration=%.2fs",comic_id,time.monotonic()-started)
        return response
    except (ProviderError,ImageProviderError) as exc:
        logger.warning("generation unavailable provider=%s model=%s reason=%s",payload.provider,payload.model or "default",str(exc))
        raise
    except Exception as exc:
        logger.exception("generation failed provider=%s",payload.provider)
        raise RuntimeError("Comic generation could not be completed. Please retry.") from exc

async def _generate(payload:ComicRequest)->GenerationResponse:
    try: return await run_in_threadpool(_build_comic,payload)
    except ProviderError as exc: raise HTTPException(status_code=503,detail=str(exc)) from exc
    except ImageProviderError as exc: raise HTTPException(status_code=503,detail=str(exc)) from exc
    except RuntimeError as exc: raise HTTPException(status_code=500,detail=str(exc)) from exc

@router.get("/",response_class=HTMLResponse)
async def home(request:Request):
    settings=get_settings()
    return templates.TemplateResponse(request=request,name="index.html",context={"default_provider":settings.default_ai_provider,"max_panels":settings.max_panels})

@router.get("/health")
async def health(): return {"status":"ok","service":"ComicCraft"}

@router.get("/api/providers",response_model=list[ProviderInfo])
async def providers():
    settings=get_settings()
    return [ProviderInfo(id="gemini",name="Google Gemini",configured=bool(settings.gemini_api_key),models=settings.models_for("gemini")),
            ProviderInfo(id="groq",name="Groq",configured=bool(settings.groq_api_key),models=settings.models_for("groq"))]

@router.get("/api/models")
async def models(provider:str="gemini"):
    name=provider.lower()
    if name not in {"gemini","groq"}: raise HTTPException(status_code=400,detail="Provider must be gemini or groq.")
    settings=get_settings()
    return {"provider":name,"models":settings.models_for(name),"default":settings.default_model_for(name)}

@router.post("/api/generate",response_model=GenerationResponse)
async def generate_api(payload:ComicRequest): return await _generate(payload)

@router.post("/api/generate-comic/json",response_model=GenerationResponse)
async def generate_json(payload:ComicRequest): return await _generate(payload)

@router.post("/generate",response_class=HTMLResponse)
async def generate_form(request:Request,prompt:str=Form(...),character_name:str=Form(...),setting:str=Form(...),tone:str=Form(...),art_style:str=Form(...),provider:str=Form(...),model:str=Form(""),panel_count:int=Form(5)):
    try:
        payload=ComicRequest(prompt=prompt,character_name=character_name,setting=setting,tone=tone,art_style=art_style,provider=provider,model=model,panel_count=panel_count)
        result=await _generate(payload)
        return RedirectResponse(url=f"/comic/{result.comic_id}",status_code=303)
    except HTTPException as exc:
        return templates.TemplateResponse(request=request,name="error.html",context={"message":exc.detail},status_code=exc.status_code)
    except Exception as exc:
        logger.info("invalid form request: %s",type(exc).__name__)
        return templates.TemplateResponse(request=request,name="error.html",context={"message":"Please review the form fields and try again."},status_code=422)

@router.get("/comic/{comic_id}",response_class=HTMLResponse)
async def comic_preview(request:Request,comic_id:str):
    try: manifest=load_manifest(comic_id)
    except (FileNotFoundError,OSError,ValueError): raise HTTPException(status_code=404,detail="Comic not found.")
    return templates.TemplateResponse(request=request,name="comic_preview.html",context={"comic":ComicStory.model_validate(manifest["comic"]),"comic_id":safe_id(comic_id)})

@router.post("/api/test-image")
async def test_image(payload:ImageTestRequest):
    prompt=payload.prompt.strip()
    if not prompt or len(prompt)>800: raise HTTPException(status_code=422,detail="Provide an image prompt with at most 800 characters.")
    try:
        provider=get_image_provider(); data=await run_in_threadpool(provider.generate,prompt)
        return {"success":True,"bytes":len(data),"content_type":"image/png"}
    except ImageProviderError as exc: raise HTTPException(status_code=503,detail=str(exc)) from exc

@router.get("/export/{comic_id}")
async def download_pdf(comic_id:str):
    try: manifest=load_manifest(comic_id)
    except (FileNotFoundError,OSError,ValueError): raise HTTPException(status_code=404,detail="Comic not found.")
    _,exports,_=storage_paths(); path=exports/Path(manifest["pdf"]).name
    if not path.is_file(): raise HTTPException(status_code=404,detail="PDF export is no longer available.")
    return FileResponse(path,media_type="application/pdf",filename=f"comiccraft_{safe_id(comic_id)}.pdf")

@router.post("/export")
async def export_post(comic_id:str=Form(...)):
    try: safe_id(comic_id); load_manifest(comic_id)
    except (FileNotFoundError,OSError,ValueError): raise HTTPException(status_code=404,detail="Comic not found.")
    return RedirectResponse(f"/export-success?comic_id={comic_id}",status_code=303)

@router.get("/export-success",response_class=HTMLResponse)
async def export_success(request:Request,comic_id:str):
    try: load_manifest(comic_id)
    except (FileNotFoundError,OSError,ValueError): raise HTTPException(status_code=404,detail="Comic not found.")
    return templates.TemplateResponse(request=request,name="export_success.html",context={"comic_id":safe_id(comic_id)})




