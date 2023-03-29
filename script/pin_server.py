import asyncio
import aiohttp

async def send_request(url, request_data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request_data) as response:
            return await response.json()


async def main():
    url = "http://localhost:8080/"

    request_data = {'group_name': 'group_1', 'model': "gpt-3.5-turbo", 'temperature': 1, 'messages': [{'role': "user", 'content': '写唐诗'}]}

    tasks = [send_request(url, request_data) for _ in range(2)]

    responses = await asyncio.gather(*tasks)

    for i, response in enumerate(responses, 1):
        print(f"Response {i}: {response}")

asyncio.run(main())
