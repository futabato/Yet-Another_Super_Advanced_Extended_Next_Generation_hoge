import sys
from logging import DEBUG, StreamHandler, getLogger
from typing import Any, Optional

from debug_toolbar.middleware import DebugToolbarMiddleware
from email_validator import EmailNotValidError, validate_email
from fastapi import FastAPI, Form, Request
from fastapi.exception_handlers import (http_exception_handler,
                                        request_validation_exception_handler)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseSettings
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

middleware = [
    Middleware(SessionMiddleware, secret_key='super-secret')
]
app = FastAPI(middleware=middleware)
app.add_middleware(DebugToolbarMiddleware)

app.mount("/static", StaticFiles(directory="static"), name="static")

def flash(request: Request, message: Any, category: str = ""):
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

def get_flashed_messages(request: Request):
    #print(request.session)
    return request.session.pop("_messages") if "_messages" in request.session else []

templates = Jinja2Templates(directory="templates")
templates.env.globals['get_flashed_messages'] = get_flashed_messages

@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

logger = getLogger(__name__)
handler = StreamHandler(sys.stdout)
handler.setLevel(DEBUG)
logger.addHandler(handler)
logger.setLevel(DEBUG)


@app.post("/contact/complete", response_class=RedirectResponse)
def contact_complete(request: Request, username: Optional[str] = Form(None), email: Optional[str] = Form(None), description: Optional[str] = Form(None)):
    # 入力チェック
    is_valid = True

    if username is None:
        flash(request, "ユーザ名は必須です", "failed")
        is_valid = False

    if email is None:
        flash(request, "メールアドレスは必須です", "failed")
        is_valid = False
    else:
        try:
            validate_email(email)
        except EmailNotValidError:
            flash(request, "メールアドレスの形式で入力してください", "failed")
            is_valid = False

    if description is None:
        flash(request, "問い合わせ内容は必須です", "failed")
        is_valid = False

    if not is_valid:
        logger.info('入力ミス ++')
        return RedirectResponse("/contact", status_code=303)
    
    # メールを送る
    
    # contact/complete endpointへリダイレクトする (https://en.wikipedia.org/wiki/Post/Redirect/Get)
    flash(request, "問い合わせ内容はメールにて送信しました。問い合わせありがとうございます。", "success")
    return RedirectResponse("/contact/complete", status_code=303)

@app.get("/contact/complete", response_class=HTMLResponse)
def transition2complete(request: Request):
    return templates.TemplateResponse("contact_complete.html", {"request": request})
