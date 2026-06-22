"""
Text to speech module.

Synthesis is delegated to a pluggable provider (ElevenLabs or 60db) defined in
cortana/tts_providers.py; this module only handles device selection and playback,
so the behaviour is identical regardless of which provider is active.
"""
from dotenv import load_dotenv
load_dotenv(override=True)
import os
from typing import Any
import pyaudio
from pydub import AudioSegment # type: ignore
import io

from cortana.stt import get_pyaudio_input_devices
from cortana.tts_providers import get_provider

PLAYBACK_BLOCK_SIZE=2048
DOWNLOAD_BLOCK_SIZE=8*1024


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

def tts_loop(text: str|None = None, provider: str|None = None):
    tts_provider = get_provider(provider)
    devices = get_pyaudio_input_devices()
    device = select_pyaudio_output_device(devices)
    voices = tts_provider.list_voices()
    voice = find_voice_by_name(voices, tts_provider.voice_name)
    if not voice:
        raise Exception('Voice not found!')
    if not text:
        while True:
            text = input('Enter text to speak: ')
            audio = tts_provider.synthesize(voice['voice_id'], text)
            play_response(audio, device)
    else:
        audio = tts_provider.synthesize(voice['voice_id'], text)
        play_response(audio, device)
