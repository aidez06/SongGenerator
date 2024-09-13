from notion.notion_data_operations import NotionDatabase
from suno_api.client_api import generate_music, get_credits
from dotenv import load_dotenv
import asyncio
import os
import logging
load_dotenv()

class Music:
    MAX_RETRIES = 5  # Max retries before giving up
    RETRY_DELAY = 10  # Delay (in seconds) between retries
    def __init__(self, token):
        self.model_version = os.getenv("MODEL_VERSION", "chirp-v3-5")  
        self.base_url = 'http://localhost:3000'  
        self.database = NotionDatabase(database_id=os.getenv('NOTION_DATABASE_ID'))
        self.token = token
        self.semaphore = asyncio.Semaphore(2)  # Limit concurrent tasks to 2

    async def generate_music_payload(self, title, lyrics, style):
        balance = await get_credits(self.token)
        if balance.get('credits_left') == 0:
            return f"Failed to Create Music! \n Credits: {balance}"

        # Creates the payload for the Suno API request
        payload = {
            "mv": self.model_version,
            "prompt": lyrics,
            "tags": style,
            "title": title
        }
        return payload

    async def process_music(self, database, title, lyrics, style):
        retries = 0

        while retries < self.MAX_RETRIES:
            async with self.semaphore:
                payload = await self.generate_music_payload(
                    title=title,
                    lyrics=lyrics,
                    style=style
                )
                if isinstance(payload, dict):
                    audio_url = await generate_music(data=payload, token=self.token)
                    if 'Too many running jobs' in audio_url:
                        retries += 1
                        logging.warning(f"Too many running jobs. Retrying {retries}/{self.MAX_RETRIES} in {self.RETRY_DELAY} seconds...")
                        await asyncio.sleep(self.RETRY_DELAY)  # Wait before retrying
                        continue  # Retry the task
                    else:
                        data = {
                            'Song Title': database.get('Song Title'),
                            'Simple Output': database.get('Simple Output'),
                            'Style Of Music': database.get('Style Of Music'),
                            'Suno Link - SMP': {audio_url: 'url'}
                        }
                        database.update(data)
                        await self.database.insert_notion_data(data=database)
                        return audio_url
                else:
                    logging.warning(payload)
                    print(payload)
                    return payload

        logging.warning(f"Max retries reached for {title}. Failed to create music.")
        return f"Failed to create music after {self.MAX_RETRIES} retries."

    async def create_music(self):
        def get_key_from_dict(field_data):
            return next(iter(field_data))

        tasks = []

        async for database in self.database.get_notion_data():
            style = get_key_from_dict(database.get('Style Of Music'))
            lyrics = get_key_from_dict(database.get('Simple Output'))
            title = get_key_from_dict(database.get('Song Title'))

            if title and lyrics:
                print(f"Creating music for {title}")
                tasks.append(self.process_music(database, title, lyrics, style))

        # Wait for all tasks to complete while respecting the semaphore
        results = await asyncio.gather(*tasks)
        return results
