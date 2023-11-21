import datetime
from telethon.sync import TelegramClient
 
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel
 
import json
 
api_id = 20575050
api_hash = "41116e47843badfda5ecf096a05af461"
username = "anikdote"
 
client = TelegramClient(username, api_id, api_hash)
 
client.start()
 
channel = client.get_entity('https://t.me/farvatercanbus')
 
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
            image_date = message.photo.date
            img_data = dict(model='mp_messages.image', pk=photo_url, fields={'image_url': photo_url,
                                                                                        'date': image_date,
                                                                                        'message_id': message.id})
            client.download_media(message.photo, photo_url)
            message_with_image[message.id] = dict(message = message.message, images_id = message.photo.id, date=message.date.strftime("%Y-%m-%d"))
        except:
            message_with_image[message.id] = dict(message = message.message, images_id = '', date=message.date.strftime("%Y-%m-%d"))
        
    offset_id = messages[len(messages) - 1].id
    if total_count_limit != 0 and total_messages >= total_count_limit:
        break
  
print("Сохраняем данные в файл...")
with open("app/static/telegram_msg/messages.json", "w") as f:
    json.dump(message_with_image, f) 
print('Парсинг сообщений группы успешно выполнен.')   
with open("app/static/telegram_msg/messages.json", "r") as f:
    print(json.load(f))
