# Build frontend
FROM node:22-slim AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Runtime: backend phục vụ API + frontend đã build. Không cần Ollama local, không cần GPU.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi "uvicorn[standard]" sqlalchemy pydantic pydantic-settings httpx numpy scikit-learn python-multipart pillow
COPY backend/ backend/
COPY knowledge_base/ knowledge_base/
COPY data/museum.db data/museum.db
COPY data/raw/archive2 data/raw/archive2
COPY data/images/book data/images/book
COPY --from=web /web/dist frontend/dist
WORKDIR /app/backend
ENV DATABASE_URL=sqlite:////app/data/museum.db AUDIO_CACHE_DIR=/app/data/audio_cache IMAGES_ROOT=/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
