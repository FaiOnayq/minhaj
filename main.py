from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from workflow import Workflow
import json

workflow = Workflow()

app = FastAPI(title="Minhaj – AI Curriculum Builder")

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Receive JSON from form and generate course
@app.post("/generate")
async def generate(data: dict):
    try:
        # Log received data
        print("Received JSON data:")
        print(json.dumps(data, indent=2))
        
        # Call the course generation function
        result = workflow.run(data)
        print("Course generation completed.")
        print(result)
        
        # Optionally, save the generated course to a JSON file
        with open("generated_course.json", "w") as f:
            json.dump(result, f, indent=2)
        
        # Return generated course as JSON
        return JSONResponse({"message": "Course generated successfully!", "course": result})
    
    except Exception as e:
        # Handle any errors
        print("Error during course generation:", str(e))
        return JSONResponse({"message": "Failed to generate course", "error": str(e)}, status_code=500)
