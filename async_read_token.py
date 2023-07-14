import asyncio
import json

class FileTokenReader:
    def __init__(self, filename):
        self.filename = filename
        self.tokens = {}

    async def __aenter__(self):
        with open(self.filename, 'r') as file:
            self.tokens = json.load(file)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def read_token(self, token_type):
        return self.tokens.get(token_type)

async def get_token_async():
    async with FileTokenReader('vk_credentials.json') as reader:
        group_token = await reader.read_token('group_token')
        personal_token = await reader.read_token('personal_token')
        return group_token, personal_token

group_token, personal_token = asyncio.run(get_token_async())

print(group_token, personal_token)