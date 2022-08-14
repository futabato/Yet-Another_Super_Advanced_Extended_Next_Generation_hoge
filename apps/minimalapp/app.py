from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.get("/contact/complete", response_class=HTMLResponse)
@app.post("/contact/complete", response_class=RedirectResponse)
def contact_complete(request: Request):
    if request.method == "POST":
        # メールを送る
        
        # contact endpointへリダイレクトする
        return RedirectResponse("/contact/complete", status_code=303)
    return templates.TemplateResponse("contact_complete.html", {"request": request})
