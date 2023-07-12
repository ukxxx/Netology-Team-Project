import os
import asyncio
import aiofiles
import json


async def read_file(file_path):
    async with aiofiles.open(file_path, mode='r') as file:
        data = await file.read()
        data = json.loads(data)
        return data
    
token = asyncio.run(read_file('vk_credentials.json'))['token']
print(result['token'])