"""FastAPI app factory. Chạy: uvicorn app.main:app --reload --port 8000 (từ thư mục backend/)."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .api import chat, documents, health, images, narration, story, timeline, topics
from .config import Settings, get_settings
from .core.exceptions import AppError
from .core.logging import setup_logging
from .database import repository as R
from .database.database import get_engine, session_scope
from .services.embedding_service import get_dense_embedder
from .services.llm_service import LLMService
from .services.narration_service import NarrationService
from .services.rag_service import RagService
from .services.retrieval_service import ImageIndex, RetrievalIndex
from .services.tts_service import TTSService

log = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, *, llm: LLMService | None = None, tts: TTSService | None = None) -> FastAPI:
    setup_logging()
    settings = settings or get_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        get_engine(settings.database_url)
        with session_scope() as db:
            chunks, imgs, links = R.load_chunks(db), R.load_images(db), R.chunk_image_links(db)
        if not chunks:
            raise RuntimeError("CSDL rỗng. Chạy scripts/build_knowledge_base.py trước.")
        dense = get_dense_embedder(settings.embedding_backend, settings.embedding_model)
        app.state.settings = settings
        app.state.index = RetrievalIndex(chunks, dense)
        app.state.image_index = ImageIndex(imgs)
        app.state.llm = llm or LLMService(settings)
        app.state.tts = tts or TTSService(settings)
        app.state.narration = NarrationService(settings, app.state.tts)
        app.state.rag = RagService(settings, app.state.index, app.state.image_index, app.state.llm, {i["image_id"]: i for i in imgs}, links)
        log.info("Sẵn sàng: %d chunk, %d ảnh, retrieval=%s", len(chunks), len(imgs), app.state.index.backend)
        yield

    app = FastAPI(title="Multimodal AI Museum Guide", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()], allow_methods=["GET", "POST"], allow_headers=["Content-Type"])

    @app.middleware("http")
    async def limit_body(request: Request, call_next):
        cl = request.headers.get("content-length")
        if cl and cl.isdigit() and int(cl) > settings.max_request_bytes:
            return JSONResponse({"error": {"code": "request_too_large", "message": "Yêu cầu quá lớn."}}, status_code=413)
        return await call_next(request)

    @app.exception_handler(AppError)
    async def app_error(_: Request, e: AppError):
        return JSONResponse({"error": {"code": e.code, "message": e.message}}, status_code=e.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, e: RequestValidationError):
        errs = [{"loc": [str(x) for x in er["loc"]], "msg": er["msg"]} for er in e.errors()]
        return JSONResponse({"error": {"code": "validation_error", "message": "Dữ liệu không hợp lệ.", "details": errs}}, status_code=422)

    for r in (health.router, chat.router, images.router, topics.router, timeline.router, documents.router, narration.router, story.router):
        app.include_router(r)

    # Production: phục vụ frontend đã build (frontend/dist) cùng origin -> không cần CORS/proxy. Dev dùng `npm run dev`.
    dist = Path(settings.images_root) / "frontend/dist"
    if dist.is_dir():
        app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        async def spa(path: str):
            if path.startswith("api/"):
                return JSONResponse({"error": {"code": "not_found", "message": "Không tìm thấy."}}, status_code=404)
            f = (dist / path).resolve()
            if path and dist.resolve() in f.parents and f.is_file():
                return FileResponse(f)
            return FileResponse(dist / "index.html")
    return app


app = create_app()
