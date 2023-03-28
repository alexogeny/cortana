"""
Text to speech module that plugs into ElevenLabs.io
"""

import os
from typing import Any, NoReturn
import pyaudio
from pathlib import Path
import json
from pydub import AudioSegment # type: ignore
import io

from cortana.stt import get_pyaudio_input_devices
from cortana.api import make_api_request, ApiType

VOICES = 'voices'
VOICE= 'voices/{voice_id}'
VOICE_SETTINGS = 'voices/{voice_id}/settings'
TTS = 'text-to-speech/{voice_id}'
TTS_STREAM = 'text-to-speech/{voice_id}/stream'
PLAYBACK_BLOCK_SIZE=2048
DOWNLOAD_BLOCK_SIZE=8*1024


def get_voices() -> list[Any]:
    if (voices_path:= Path('voices.json')).exists():
        with open(voices_path, 'r') as f:
            return json.load(f)['voices']
    response = make_api_request('GET', ApiType.ELEVENLABS, VOICES)
    with open('voices.json', 'w') as f:
        json.dump(response, f, indent=4)
    
    if not response:
        raise Exception('No voices found!')

    return response.get('voices', [])


def stream_text_to_voice(voice_id: str, text: str):
    response_stream = make_api_request('POST', ApiType.ELEVENLABS, TTS_STREAM.format(voice_id=voice_id), data={
  "text": "Oh, shampoo, that magical elixir that we all slather on our hair without a clue as to how it actually works. It's like putting faith in a wizard who claims to have a secret potion that will make your hair shine like diamonds.",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.3
  }
}, stream=True)
    return response_stream


def get_text_to_voice(voice_id: str, text: str):
    response = make_api_request('POST', ApiType.ELEVENLABS, TTS.format(voice_id=voice_id), data={
        "text": text,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.3
        }
    })
    return response


def get_non_premade_voices(voices: list[dict[Any, Any]]) -> list[dict[Any, Any]]:
    return [
        voice
        for voice
        in voices
        if not voice.get('category', None)=='premade']


def find_voice_by_name(voices: list[dict[Any, Any]], name: str) -> dict[Any, Any] | None:
    return next((v for v in voices if name.lower() in v['name'].lower()), None)


def select_pyaudio_output_device(devices: list[Any], device_index: int=0) -> dict[Any, Any] | None:
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
    voice = find_voice_by_name(get_non_premade_voices(voices), os.environ.get('ELEVENLABS_VOICE_NAME', ''))
    if not voice:
        raise Exception('Voice not found!')
    while True:
        # get user input text
        text = input('Enter text to speak: ')
        response_stream = get_text_to_voice(voice['voice_id'], text)
        play_response(response_stream.content, device)
