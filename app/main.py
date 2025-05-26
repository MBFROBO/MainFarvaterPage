import os, uvicorn, json
from multiprocessing import Process
import time
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from dotenv import load_dotenv
from pathlib import Path

from datetime import date, datetime

from logger import logging

dotenv_path = Path(__file__).parent.absolute() / ".env"
if os.path.exists(dotenv_path): load_dotenv(dotenv_path)

app = FastAPI()

app.mount('/static', StaticFiles(directory=Path(__file__).parent.absolute() / 'static', html=True), name='static')
templates = Jinja2Templates(Path(__file__).parent.absolute() / 'temp')


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("page39548763.html", {'request': request})
    
if __name__ == '__main__':
    uvicorn.run(app=app, host=(os.getenv('LANDING_HOST')), port=int(os.getenv('LANDING_PORT')))
    