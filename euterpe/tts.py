"""
Text to speech module that plugs into ElevenLabs.io
"""

import os
from typing import Any
import pyaudio
import requests
from pathlib import Path
import json
from pydub import AudioSegment
import io

from euterpe.stt import get_pyaudio_input_devices

VOICES = 'voices'
VOICE= 'voices/{voice_id}'
VOICE_SETTINGS = 'voices/{voice_id}/settings'
TTS = 'text-to-speech/{voice_id}'
TTS_STREAM = 'text-to-speech/{voice_id}/stream'
PLAYBACK_BLOCK_SIZE=2048
DOWNLOAD_BLOCK_SIZE=8*1024


def build_auth_header():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "xi-api-key": os.environ.get('ELEVENLABS_API_KEY'),
    }
    return headers


def make_api_request(method, url, data=None, stream=False):
    headers = build_auth_header()
    url = f"https://{os.environ.get('ELEVENLABS_API_URL')}{url}"
    print(url)
    response = requests.request(method, url, headers=headers, json=data, stream=stream)
    return response


def get_voices():
    # if the voices are cached, return them
    if (voices_path:= Path('voices.json')).exists():
        with open(voices_path, 'r') as f:
            return json.load(f)['voices']
    response = make_api_request('GET', VOICES)
    data = response.json()
    with open('voices.json', 'w') as f:
        json.dump(data, f, indent=4)

    return data['voices']


def stream_text_to_voice(voice_id, text):
    response_stream = make_api_request('POST', TTS_STREAM.format(voice_id=voice_id), data={
  "text": "Oh, shampoo, that magical elixir that we all slather on our hair without a clue as to how it actually works. It's like putting faith in a wizard who claims to have a secret potion that will make your hair shine like diamonds.",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.3
  }
}, stream=True)
    return response_stream


def get_text_to_voice(voice_id, text):
    response = make_api_request('POST', TTS.format(voice_id=voice_id), data={
        "text": text,
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.3
        }
    })
    return response


def get_non_premade_voices(voices):
    return [v for v in voices if not v['category']=='premade']


def find_voice_by_name(voices, name):
    return next((v for v in voices if name.lower() in v['name'].lower()), None)


def select_pyaudio_output_device(devices: list[Any], device_index: int=0):
    if (device_name:= os.environ.get('OUTPUT_DEVICE')):
        return next((d for d in devices if device_name in d['name']), None)
    return devices[device_index]


def play_response(response_data, device: Any):
    p = pyaudio.PyAudio()
    stream = p.open(
        format=pyaudio.paInt16,
        channels=2,
        rate=44100,
        output=True,
        output_device_index=device['index'], frames_per_buffer=DOWNLOAD_BLOCK_SIZE)
    print('Playing audio...')
    audio_segment = AudioSegment.from_file(io.BytesIO(response_data), format='mp3')
    audio_data = audio_segment.set_frame_rate(44100).set_channels(2).raw_data
    stream.write(audio_data)
    stream.stop_stream()
    stream.close()
    p.terminate()

def tts_loop(text: str = "Hey this is a test"):
    devices = get_pyaudio_input_devices()
    device = select_pyaudio_output_device(devices)
    voices = get_voices()
    voice = find_voice_by_name(get_non_premade_voices(voices), os.environ.get('ELEVENLABS_VOICE_NAME'))
    if not voice:
        raise Exception('Voice not found!')
    response_stream = get_text_to_voice(voice['voice_id'], text)
    play_response(response_stream.content, device)
