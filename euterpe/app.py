"""
The full pipeline that runs:
    1. Speech to text
    2. Chat GPT
    3. Text to speech
"""
import os
from uuid import uuid4
from pathlib import Path
import json
import time
from euterpe.cgpt import create_message_list_with_prompt, pluggable_chat_loop
from euterpe.stt import stt_loop
from euterpe.tts import tts_loop

SKIP = 'e6bf9e50-901a-49d3-b00c-2fd22613e0e3'

def full_pipeline():
    message_list = create_message_list_with_prompt()
    hotword = os.environ.get('VOICE_ASSISTANT_HOTWORD', SKIP)
    if not (chat_folder:=Path('chats')).exists():
        chat_folder.mkdir()
    chat_file_name = f"chats/{time.time()}-{uuid4().hex}.txt"
    chat_file = Path(chat_file_name)
    with open(chat_file, 'w') as f:
        f.write(json.dumps(message_list, indent=2))
    print(message_list)
    while True:
        text = stt_loop()

        if (hotword and hotword != SKIP and hotword.lower() in text.lower()) or hotword == SKIP:
            response = pluggable_chat_loop(message_list, text)
            tts_loop(response[-1]['content'])

            with open(chat_file, 'w') as f:
                f.write(json.dumps(message_list, indent=2))
