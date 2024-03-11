import os
import secrets
import asyncio
import aiofiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse


app = FastAPI()


time = {}

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def delete():
    while True:
        await asyncio.sleep(60)
        remove = []
        for key in time.keys():
            time[key] = time[key] - 1
            if time[key] == 0:
                remove.append(key)
                if os.path.exists(f'./files/{key}_file.zip'):
                    os.remove(f'./files/{key}_file.zip')
        for key in remove:
            del time[key]


@app.on_event("startup")
async def start():
    t = asyncio.create_task(delete())


@app.get("/")
async def root():
    return FileResponse('./dist/index.html')

@app.get("/send")
async def send():
    return FileResponse('./dist/index.html')

@app.get("/receive")
async def receive():
    return FileResponse('./dist/index.html')

@app.get("/receive/{code}")
async def receive_code(code: int):
    return FileResponse('./dist/index.html')

@app.get("/logo")
async def logo():
    return FileResponse('./assets/logo.png')

@app.get("/icon")
async def icon():
    return FileResponse('./assets/icon.png')

@app.get("/js")
async def js():
    return FileResponse('./dist/assets/index-9cd9f8fe.js')

@app.get("/css")
async def css():
    return FileResponse('./dist/assets/index-1e34515e.css')

@app.get("/bg/home")
async def home_bg():
    return FileResponse('./assets/home.jpg')

@app.get("/bg/send")
async def send_bg():
    return FileResponse('./assets/send.jpg')

@app.get("/bg/receive")
async def receive_bg():
    return FileResponse('./assets/receive.jpg')

@app.get("/receive/files/{fn}")
async def download(fn: str):
    if os.path.exists(f"./files/{fn}_file.zip"):
        return FileResponse(f"./files/{fn}_file.zip")
    else:
        raise HTTPException(status_code=404, detail="File not found")

@app.post("/send/submitfile")
async def upload(file: UploadFile = File(...)):
    while True:
        name = secrets.randbelow(999999)
        if name not in time.keys():
            filename = name
            async with aiofiles.open(f'./files/{filename}_file.zip', 'wb') as f:
                contents = await file.read()
                await f.write(contents)
            time[name] = 10

            return {"code": filename}