"""
The full pipeline that runs:
    1. Speech to text
    2. Chat GPT
    3. Text to speech
"""
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from uuid import uuid4
from pathlib import Path
import json
import time
import re
from cortana.cgpt import create_message_list_with_prompt, pluggable_chat_loop
from cortana.stt import stt_loop
from cortana.tts import tts_loop

SKIP = 'e6bf9e50-901a-49d3-b00c-2fd22613e0e3'


def check_for_hotword_or_hotword_corrections(text: str) -> str:
    hotword = os.environ.get('ASSISTANT_NAME', SKIP)
    if hotword != SKIP and hotword.lower() in text.lower():
        return text
    hotword_corrections = [
        hotword.strip()
        for hotword
        in os.environ.get('ASSISTANT_NAME_CORRECTIONS', '').split(',')
    ]
    if hotword_corrections and len(hotword_corrections) > 0:
        for hotword_correction in hotword_corrections:
            if hotword_correction.lower() in text.lower():
                text = re.sub(hotword_correction, hotword, text, flags=re.IGNORECASE)
                return text
    if hotword == SKIP:
        return text
    
    raise ValueError('Hotword not found')


def full_pipeline(with_tts: bool = True):
    message_list = create_message_list_with_prompt()
    if not (chat_folder:=Path('chats')).exists():
        chat_folder.mkdir()
    chat_file_name = f"chats/{time.time()}-{uuid4().hex}.json"
    chat_file = Path(chat_file_name)
    with open(chat_file, 'w') as f:
        f.write(json.dumps(message_list, indent=2))

    while True:
        text = stt_loop()

        try:
            text = check_for_hotword_or_hotword_corrections(text)
            response = pluggable_chat_loop(message_list, text)
            if with_tts:
                tts_loop(response[-1]['content'])
            else:
                print(response[-1]['content'])

            with open(chat_file, 'w') as f:
                f.write(json.dumps(message_list, indent=2))
        except ValueError:
            pass


def clone_pipeline():
    while True:
        text = stt_loop()
        tts_loop(text)
