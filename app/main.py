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

from telethon.sync import TelegramClient
from telethon import connection

from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

from telethon.tl.functions.messages import GetHistoryRequest, GetDialogsRequest

from logger import logging

dotenv_path = Path(__file__).parent.absolute() / ".env"
if os.path.exists(dotenv_path): load_dotenv(dotenv_path)

app = FastAPI()

app.mount('/static', StaticFiles(directory=Path(__file__).parent.absolute() / 'static', html=True), name='static')
templates = Jinja2Templates(Path(__file__).parent.absolute() / 'temp')


def parse_main():
    """
        Основная функция парсинга канала
    """
    api_id      =   int(os.getenv('TELEGRAM_API_ID'))
    api_hash    =   os.getenv('TELEGRAM_API_HASH')
    username    =   os.getenv('TELEGRAM_API_USERNAME')
    
    client = TelegramClient(username, api_id, api_hash)
    
    client.start()
    
    channel = client.get_entity(os.getenv('CHANNEL_LINK'))
    
    offset_id = 0
    limit = 100
    message_with_image = {}
    total_messages = 0
    total_count_limit = 0
    
    while True:
        history = client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages  
            
        for message in messages:
            try:
                photo_url = f'app/static/telegram_images/{message.photo.id}.png'
                try:
                    video_url = f'app/static/telegram_videos/{message.video.id}.mp4'
                except:
                    video_url = ''
                    
                image_date = message.photo.date
                img_data = dict(model='mp_messages.image', pk=photo_url, fields={'image_url': photo_url,
                                                                                            'date': image_date,
                                                                                            'message_id': message.id})
                client.download_media(message.photo, photo_url)
                if message.message == '' or message.message == 'None' or message.message == None:
                    pass
                else:
                    message_with_image[message.id] = dict(message = str(message.message).replace('"',"'"), images_id = f"{message.photo.id}", date=message.date.strftime("%d.%m.%Y"))
            except:
                if message.message == '' or message.message == 'None' or message.message == None:
                    pass
                else:
                    message_with_image[message.id] = dict(message = str(message.message).replace('"',"'"), images_id = '', date=message.date.strftime("%d.%m.%Y"))
            
        offset_id = messages[len(messages) - 1].id
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    
    with open("app/static/telegram_msg/messages.json", "w") as f:
        json.dump(message_with_image, f) 

def thread_parse_func():
    
    while True:
        parse_main()
        time.sleep(86400)
        
def read_news():
    with open("app/static/telegram_msg/messages.json", "r") as f:
        data = json.load(f)
        http_data_dict = {}
        http_data_arr = []
        i = 0
        while i < 5:
            http_data_arr.append(data[f"{list(data.keys())[i]}"])
            i+=1
        http_data_dict['data'] = http_data_arr
        return http_data_dict
        
    
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    news_data = read_news()
    return templates.TemplateResponse("page39548763.html", {'request': request, 'news_data': json.dumps(news_data)})
    
if __name__ == '__main__':
    proc = Process(target=thread_parse_func, daemon=True)
    proc.start()
    uvicorn.run(app=app, host=os.getenv('LANDING_HOST'), port=int(os.getenv('LANDING_PORT')))
    