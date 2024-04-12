from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index_kor.html", {"request": request})

@app.post("/chat")
async def chat(request: Request):
    try:
        body = await request.json()
        user_question = body.get('question')
        if not user_question:
            return JSONResponse(content={"error": "No question provided"}, status_code=400)
        response = 'hi'  # chatgpt()
        return JSONResponse(content={"response": response})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)
