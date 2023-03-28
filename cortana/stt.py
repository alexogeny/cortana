"""
Module that records text and turns it into speech.
"""

from typing import Any
import whisper # type: ignore
import os
import pyaudio
import numpy as np
import wave

# Constants
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
SILENCE_THRESHOLD = 0.1  # Adjust this value to tweak sensitivity
WAIT_TIME = 1
OUTPUT_FILE = 'output.wav'


def get_pyaudio_input_devices() -> list[Any]:
    p = pyaudio.PyAudio()
    devices: list[Any] = []
    for i in range(p.get_device_count()):
        devices.append(p.get_device_info_by_index(i))
    return devices


def select_pyaudio_input_device(input_devices: list[Any], device_index: int = 0) -> None:
    if (device_name:= os.environ.get('INPUT_DEVICE')):
        return next((d for d in input_devices if device_name in d['name'] and d['defaultSampleRate'] == RATE), None)
    return input_devices[device_index]

def get_whisper_model():
    model = whisper.load_model(os.environ.get('OPENAI_WHISPER_MODEL', 'tiny'))
    return model

def transcribe_audio_to_text(model):
    print('Transcribing...')
    text: str = model.transcribe(OUTPUT_FILE)
    return f"{text['text']}".strip()

def detect_silence(data, threshold):
    return np.mean(np.abs(data)) < threshold

def listen_to_pyaudio_input_device(input_device: Any):
    p = pyaudio.PyAudio()
    # open a new stream at the given input_device['index']
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True, frames_per_buffer=CHUNK, input_device_index=input_device['index'])
    print('Waiting for speech...')
    audio_data = []
    while True:
        data = stream.read(CHUNK)
        audio_np = np.frombuffer(data, dtype=np.int16)
        if np.max(audio_np) > 100:
            audio_data.append(data)
            break

    print('Listening...')
    silence_count = 0
    while True:
        data = stream.read(CHUNK)
        audio_data.append(data)

        # convert audio data to numpy array
        audio_np = np.frombuffer(data, dtype=np.int16)

        # if audio amplitude falls below threshold, stop recording
        if np.max(audio_np) < 100:
            silence_count += 1
            if silence_count > int(RATE / CHUNK):
                break
        else:
            silence_count = 0

    print("Finished listening.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = b''.join(audio_data)
    return audio_data

def save_to_wav_file(audio_data, channels: int, rate: int) -> None:
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio_data)

def stt_loop() -> str:
    input_devices = get_pyaudio_input_devices()
    input_device = select_pyaudio_input_device(input_devices)
    model = get_whisper_model()

    frames = listen_to_pyaudio_input_device(input_device)
    save_to_wav_file(frames, CHANNELS, RATE)
    text = transcribe_audio_to_text(model)
    print(f'Transcribed text: {text}')
    return text        
