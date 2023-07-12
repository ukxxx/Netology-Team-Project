import aiofiles
import json


async def read_token(file_path):
    async with aiofiles.open(file_path, mode='r') as file:
        data = await file.read()
        data = json.loads(data)
        token = data['token']
        return token