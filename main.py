import os
import secrets
import asyncio
import logging
from fastapi import FastAPI, UploadFile, File
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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


async def delete():
    while True:
        logger.debug(time)
        await asyncio.sleep(60)
        remove = []
        for key in time.keys():
            time[key] = time[key] - 1
            logger.debug("2")
            if time[key] == 0:
                logger.debug("3")
                remove.append(key)
                if os.path.exists(f'./files/{key}_file.zip'):
                    logger.debug("4")
                    os.remove(f'./files/{key}_file.zip')
        for key in remove:
            del time[key]


@app.on_event("startup")
async def start():
    t = asyncio.create_task(delete())


@app.get("/")
async def root():
    return FileResponse('./dist/index.html')

@app.get("/js")
async def js():
    return FileResponse('./dist/assets/index-66192589.js')

@app.get("/css")
async def css():
    return FileResponse('./dist/assets/index-c1357765.css')

@app.get("/home/bg")
async def home_bg():
    return FileResponse('./assets/home.jpg')

@app.get("/send/bg")
async def send_bg():
    return FileResponse('./assets/send.jpg')

@app.get("/receive/bg")
async def receive_bg():
    return FileResponse('./assets/receive.jpg')

@app.get("/receive/files/{fn}")
async def download(fn: str):
    return FileResponse(f'./files/{fn}_file.zip')

@app.post("/send/submitfile")
async def upload(file: UploadFile = File(...)):
    while True:
        name = secrets.randbelow(999999)
        if name not in time.keys():
            time[name] = 2
            filename = name
            with open(f'./files/{filename}_file.zip', 'wb') as f:
                contents = await file.read()
                f.write(contents)

            return {"code": filename}