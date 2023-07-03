import secrets
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(debug=True)


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
    filename = secrets.randbelow(999999)
    with open(f'./files/{filename}_file.zip', 'wb') as f:
        contents = await file.read()
        f.write(contents)

    # Perform any other necessary processing

    return {"code": filename}
