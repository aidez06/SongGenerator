from notion.notion_data_operations import NotionDatabase
from suno_api.client_api import generate_music, get_credits
from dotenv import load_dotenv
import asyncio
import os
import logging
from suno_api.deps import get_token 
load_dotenv()

class Music:
    def __init__(self):
        self.model_version = os.getenv("MODEL_VERSION", "chirp-v3-5")  
        self.base_url = 'http://localhost:3000'  
        self.database = NotionDatabase(database_id=os.getenv('NOTION_DATABASE_ID'))
    
        self.semaphore = asyncio.Semaphore(2) 
    async def generate_music_payload(self, title, lyrics, style):
        balance = await get_credits(next(get_token()))
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
 
        async with self.semaphore:
            payload = await self.generate_music_payload(
                title=title,
                lyrics=lyrics,
                style=style
            )
            if isinstance(payload, dict):
                while True:
                    audio_url = await generate_music(data=payload, token=next(get_token()))
                    print(audio_url, type(audio_url))
                    if 'audiopipe' in audio_url:
                        # Assuming the correct response is a dictionary
                        data = {
                            'Song Title': database.get('Song Title'),
                            'Simple Output': database.get('Simple Output'),
                            'Style Of Music': database.get('Style Of Music'),
                            'Suno Link - SMP': {audio_url: 'url'}
                        }
                        database.update(data)
                        await self.database.insert_notion_data(data=database)
                        return audio_url  # Return the valid audio_url and exit the loop
                    
                    else:
                        # Log a message to track retries and delays
                        logging.warning(f"Retrying: Received {audio_url} (Type: {type(audio_url)}). Waiting 30 seconds before retrying...")
                        await asyncio.sleep(30)  # Delay before retrying the request



            else:
                logging.warning(payload)
                print(payload)
                return payload

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
