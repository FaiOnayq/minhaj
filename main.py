from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Minhaj – AI Curriculum Builder")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Receive JSON from form
@app.post("/generate")
async def generate(data: dict):
    print("Received JSON data:")
    print(data)  # <-- This prints in CMD/terminal
    return JSONResponse({"message": "Data received successfully!"})
