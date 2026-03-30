import asyncio
import os
import secrets
from pathlib import Path

import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles


CHUNK_SIZE = 1024 * 1024
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
DEFAULT_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


def load_local_env(env_path: Path) -> None:
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


def resolve_path(var_name: str, default_path: Path) -> Path:
    configured = os.getenv(var_name, "").strip()
    if not configured:
        return default_path
    candidate = Path(configured)
    if candidate.is_absolute():
        return candidate
    return (BASE_DIR / candidate).resolve()


def parse_csv_env(var_name: str, default_values: list[str]) -> list[str]:
    raw = os.getenv(var_name, "").strip()
    if not raw:
        return default_values
    return [item.strip() for item in raw.split(",") if item.strip()]


load_local_env(BASE_DIR / ".env")

DIST_DIR = resolve_path("UI_DIST_DIR", BASE_DIR / "dist")
DIST_ASSETS_DIR = DIST_DIR / "assets"
PUBLIC_ASSETS_DIR = resolve_path("PUBLIC_ASSETS_DIR", BASE_DIR / "assets")
UPLOAD_DIR = resolve_path("UPLOAD_DIR", BASE_DIR / "files")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI()
time: dict[int, int] = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=parse_csv_env("CORS_ALLOW_ORIGINS", DEFAULT_ORIGINS),
    allow_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX", DEFAULT_ORIGIN_REGEX),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Built UI assets from Vite (hashed JS/CSS) are served directly by path.
app.mount("/assets", StaticFiles(directory=str(DIST_ASSETS_DIR), check_dir=False), name="ui-assets")


def serve_index() -> FileResponse:
    index_path = DIST_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=503, detail="UI has not been deployed yet")
    return FileResponse(str(index_path))


def timed_file_path(file_code: str | int) -> Path:
    return UPLOAD_DIR / f"{file_code}_file.zip"


def serve_dist_asset(pattern: str) -> FileResponse:
    candidates = list(DIST_ASSETS_DIR.glob(pattern))
    if not candidates:
        raise HTTPException(status_code=404, detail="Build asset not found")
    newest = max(candidates, key=lambda path: path.stat().st_mtime)
    return FileResponse(str(newest))


async def delete():
    while True:
        await asyncio.sleep(60)
        expired_keys: list[int] = []
        for key in list(time.keys()):
            time[key] = time[key] - 1
            if time[key] <= 0:
                expired_keys.append(key)
                expired_file = timed_file_path(key)
                if expired_file.exists():
                    expired_file.unlink()
        for key in expired_keys:
            del time[key]


@app.on_event("startup")
async def start():
    asyncio.create_task(delete())


@app.get("/")
async def root():
    return serve_index()


@app.get("/send")
async def send():
    return serve_index()


@app.get("/receive")
async def receive():
    return serve_index()


@app.get("/receive/{code}")
async def receive_code(code: int):
    return serve_index()


@app.get("/logo")
async def logo():
    logo_path = PUBLIC_ASSETS_DIR / "logo.png"
    if not logo_path.exists():
        raise HTTPException(status_code=404, detail="Logo not found")
    return FileResponse(str(logo_path))


@app.get("/icon")
async def icon():
    icon_path = PUBLIC_ASSETS_DIR / "icon.png"
    if not icon_path.exists():
        raise HTTPException(status_code=404, detail="Icon not found")
    return FileResponse(str(icon_path))


@app.get("/js")
async def js():
    # Backward-compatibility endpoint for older index.html files.
    return serve_dist_asset("index-*.js")


@app.get("/css")
async def css():
    # Backward-compatibility endpoint for older index.html files.
    return serve_dist_asset("index-*.css")


@app.get("/bg/home")
async def home_bg():
    home_bg_path = PUBLIC_ASSETS_DIR / "home.jpg"
    if not home_bg_path.exists():
        raise HTTPException(status_code=404, detail="Background not found")
    return FileResponse(str(home_bg_path))


@app.get("/bg/send")
async def send_bg():
    send_bg_path = PUBLIC_ASSETS_DIR / "send.jpg"
    if not send_bg_path.exists():
        raise HTTPException(status_code=404, detail="Background not found")
    return FileResponse(str(send_bg_path))


@app.get("/bg/receive")
async def receive_bg():
    receive_bg_path = PUBLIC_ASSETS_DIR / "receive.jpg"
    if not receive_bg_path.exists():
        raise HTTPException(status_code=404, detail="Background not found")
    return FileResponse(str(receive_bg_path))


@app.get("/receive/files/{fn}")
async def download(fn: str):
    file_path = timed_file_path(fn)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    async def iterfile():
        async with aiofiles.open(file_path, "rb") as f:
            while chunk := await f.read(CHUNK_SIZE):
                yield chunk

    headers = {
        "Content-Disposition": f'attachment; filename="{fn}_file.zip"',
        "Content-Length": str(file_path.stat().st_size),
    }
    return StreamingResponse(iterfile(), headers=headers, media_type="application/zip")


@app.post("/send/submitfile")
async def upload(file: UploadFile = File(...)):
    while True:
        name = secrets.randbelow(999999)
        if name in time:
            continue

        file_path = timed_file_path(name)
        async with aiofiles.open(file_path, "wb") as f:
            while chunk := await file.read(CHUNK_SIZE):
                await f.write(chunk)

        time[name] = 10
        return {"code": name}
