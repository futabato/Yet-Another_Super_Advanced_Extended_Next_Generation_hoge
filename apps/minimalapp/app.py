from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


templates = Jinja2Templates(directory="templates")

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact/complete", response_class=RedirectResponse)
def contact_complete(request: Request, username: str = Form(), email: str = Form(), description: str = Form()):
    # メールを送る

    # contact/complete endpointへリダイレクトする (https://en.wikipedia.org/wiki/Post/Redirect/Get)
    return RedirectResponse("/contact/complete", status_code=303)

@app.get("/contact/complete", response_class=HTMLResponse)
def transition2complete(request: Request):
    return templates.TemplateResponse("contact_complete.html", {"request": request})
