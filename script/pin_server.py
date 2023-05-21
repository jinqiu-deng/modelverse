import asyncio
import aiohttp

async def send_request(url, request_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_data) as response:
            while True:
                chunk = await response.content.readany()
                if not chunk:
                    break
                print(chunk.decode('utf-8'))

async def main():
    # url = "http://localhost:8080/"
    url = "http://52.53.130.54:8080/"

    request_data = {'group_name': 'default_group', 'stream': False, 'model': "gpt-4", 'temperature': 1, 'messages': [{'role': "user", 'content': 'count from 1 to 100'}]}

    tasks = [send_request(url, request_data) for _ in range(20)]

    await asyncio.gather(*tasks)

asyncio.run(main())
