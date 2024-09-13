import json
import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")

COMMON_HEADERS = {
    "Content-Type": "text/plain;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Referer": "https://suno.com",
    "Origin": "https://suno.com",
}


async def fetch(url, headers=None, data=None, method="POST"):
    if headers is None:
        headers = {}
    headers.update(COMMON_HEADERS)
    if data is not None:
        data = json.dumps(data)



    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=method, url=url, data=data, headers=headers
            ) as resp:
                return await resp.json()
        except Exception as e:
            return f"An error occurred: {e}"


async def get_feed(ids, token):
    print("GetFeed", token)
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/feed/?ids={ids}"
    response = await fetch(api_url, headers, method="GET")
    print(response)
    return response


async def generate_music(data, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/v2/"
    response = await fetch(api_url, headers, data)

    if isinstance(response, str):
        return response

    if not response and isinstance(response, list):
        print("Failed to generate custom audio.")
        return None
    print(response)
    if response.get('clips') and isinstance(response.get('clips'), list):
        ids = ",".join([str(item['id']) for item in response.get('clips')])
        print(f"Generated Audio IDs: {ids}")
        while True:
            audio_info = await get_feed(ids, token)
            if isinstance(audio_info, list) and all(isinstance(item, dict) and 'status' in item for item in audio_info):
                if all(item["status"] == 'streaming' for item in audio_info):
                    for item in audio_info:
                        return item['audio_url']  
                    break
                else:
                    print("Waiting for audio to be ready...")
            else:
                print(f"Unexpected audio_info format: {audio_info}")
            
            await asyncio.sleep(5)

    return response

async def get_audio_information(audio_ids, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/clips/get_similar/?id={audio_ids}"
    return await fetch(api_url, headers, method="GET")

async def generate_lyrics(prompt, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/lyrics/"
    data = {"prompt": prompt}
    return await fetch(api_url, headers, data)


async def get_lyrics(lid, token):
    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/generate/lyrics/{lid}"
    return await fetch(api_url, headers, method="GET")


async def get_credits(token):

    headers = {"Authorization": f"Bearer {token}"}
    api_url = f"{BASE_URL}/api/billing/info/"
    respose = await fetch(api_url, headers, method="GET")
    return {
        "credits_left": respose.get('total_credits_left',''),
        "period": respose.get('period',''),
        "monthly_limit": respose.get('monthly_limit',''),
        "monthly_usage": respose.get('monthly_usage','')
    }
