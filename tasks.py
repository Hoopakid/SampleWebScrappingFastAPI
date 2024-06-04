import os
import requests

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

app = Celery(
    'tasks',
    broker='redis://redis_chart:6379',
    backend='redis://redis_chart:6379'
)

app.conf.beat_schedule = {
    'send_message': {
        'task': 'tasks.send_message_to_user',
        'schedule': crontab(hour=14, minute=30)
    }
}

BOT_TOKEN = os.environ.get('BOT_TOKEN')
MBI_CHAT_ID = os.environ.get('MBI_CHAT_ID')
SHER_CHAT_ID = os.environ.get('SHER_CHAT_ID')

chat_ids = [int(MBI_CHAT_ID), int(SHER_CHAT_ID)]


@app.task()
def send_message_to_user():
    url = f'https://api.telegram.org/bot{BOT_TOKEN}'
    for chat_id in chat_ids:
        with open('calls.jpg', 'rb') as photo:
            requests.post(url + '/sendPhoto', data={'chat_id': chat_id}, files={'photo': photo})
    return True
