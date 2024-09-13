from suno_music import Music
from google_ai_studio.generate_content import prompt
from suno_api.deps import get_token  
import asyncio

async def main():

    token = next(get_token())
    music_instance = Music(token=token)
    await music_instance.create_music() 

if __name__ == '__main__':
    asyncio.run(main())  