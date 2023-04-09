import json
import aiohttp

class CustomOpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_base_url = "https://api.openai.com/v1/chat/completions"

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers

    async def create_chat_completion_stream(self, request_body_json):
        headers = self._get_headers()

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.api_base_url, json=request_body_json) as response:
                if response.status == 200:
                    while True:
                        chunk = await response.content.readline()
                        if not chunk:
                            break
                        decoded_chunk = chunk.decode('utf-8')
                        if decoded_chunk.startswith("data: "):
                            data_json = json.loads(decoded_chunk[6:].strip())
                            finish_reason = data_json['choices'][0].get('finish_reason')
                            yield data_json
                            if finish_reason == 'stop':
                                break
                else:
                    raise Exception(f"API call failed with status code {response.status}: {await response.text()}")

    async def create_chat_completion(self, request_body_json):
        headers = self._get_headers()

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.api_base_url, json=request_body_json) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API call failed with status code {response.status}: {await response.text()}")
