import enum
import os
import requests
from typing import Any, Literal
from dotenv import load_dotenv
load_dotenv(override=True)
class ApiType(enum.Enum):
    ELEVENLABS = os.environ.get('ELEVENLABS_API_URL')
    OPENAI = os.environ.get('OPENAI_API_URL')


Method = Literal['GET', 'POST', 'PUT', 'DELETE']

def build_auth_header(api_type: ApiType) -> dict[Any, Any]:
    header = {
        'Content-Type': 'application/json',
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
    }
    if api_type == ApiType.ELEVENLABS:
        header = {**header, **{
        "xi-api-key": os.environ.get('ELEVENLABS_API_KEY'),
    }}
    if api_type == ApiType.OPENAI:
        header = {**header, **{
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
        "OpenAI-Organization": os.environ.get('OPENAI_ORG_ID'),
    }}
    
    return header


def make_api_request(method: Method, api_type: ApiType, url: str, data: dict[Any, Any]|None=None, stream: bool=False) -> Any | None:
    headers = build_auth_header(api_type)
    url = f"https://{api_type.value}{url}"
    response = requests.request(method, url, headers=headers, json=data, stream=stream)
    if not stream and response.headers['Content-Type'] != 'application/json':
        return response
    if not stream and response.headers['Content-Type'] == 'application/json':
        return response.json()
    if stream:
        return response
