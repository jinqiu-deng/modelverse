import json
import aiohttp

class CustomOpenAIClient:
    def __init__(self, organization_id, api_key):
        self.organization_id = organization_id
        self.api_key = api_key
        self.api_base_url = "https://api.openai.com/v1/chat/completions"

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json",
            "openai-organization": self.organization_id,
            "Authorization": f"Bearer {self.api_key}"
        }
        return headers

    async def create_chat_completion(self, request_body_json):
        headers = self._get_headers()
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.api_base_url, json=request_body_json) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API call failed with status code {response.status}: {await response.text()}")
