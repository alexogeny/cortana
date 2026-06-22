"""
TTS provider abstraction so ElevenLabs and 60db can be used interchangeably.

Every provider exposes the same minimal interface, which keeps the rest of the
TTS pipeline (device selection + playback in tts.py) completely provider-agnostic:

    - voice_name        the configured voice to look for (from .env)
    - list_voices()     a normalized list of {'voice_id', 'name', ...} dicts
    - synthesize(...)   audio bytes (mp3) ready for playback

The provider is chosen by name: an explicit argument (e.g. the --provider CLI
flag) takes precedence, otherwise the TTS_PROVIDER env var, otherwise elevenlabs.
"""
from dotenv import load_dotenv
load_dotenv(override=True)
import os
import json
import base64
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from cortana.api import make_api_request, ApiType


class TTSProvider(ABC):
    name: str

    @property
    @abstractmethod
    def voice_name(self) -> str:
        """The voice name to look for, read from this provider's .env var."""
        ...

    @abstractmethod
    def list_voices(self) -> list[dict[str, Any]]:
        """Normalized list of voices, each a dict with at least 'voice_id' and 'name'."""
        ...

    @abstractmethod
    def synthesize(self, voice_id: str, text: str) -> bytes:
        """Return mp3 audio bytes for the given text in the given voice."""
        ...

    def _read_cache(self, cache_path: Path) -> Any | None:
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None

    def _write_cache(self, cache_path: Path, payload: Any) -> None:
        with open(cache_path, 'w') as f:
            json.dump(payload, f, indent=4)


class ElevenLabsProvider(TTSProvider):
    name = 'elevenlabs'
    VOICES = 'voices'
    TTS = 'text-to-speech/{voice_id}'
    CACHE = Path('voices.json')

    @property
    def voice_name(self) -> str:
        return os.environ.get('ELEVENLABS_VOICE_NAME', '')

    def list_voices(self) -> list[dict[str, Any]]:
        cached = self._read_cache(self.CACHE)
        if cached is not None:
            voices = cached.get('voices', []) if isinstance(cached, dict) else cached
        else:
            response = make_api_request('GET', ApiType.ELEVENLABS, self.VOICES)
            if not response:
                raise Exception('No voices found!')
            self._write_cache(self.CACHE, response)
            voices = response.get('voices', [])
        # exclude elevenlabs' stock voices so we match cloned/custom ones by name
        return [v for v in voices if v.get('category') != 'premade']

    def synthesize(self, voice_id: str, text: str) -> bytes:
        response = make_api_request('POST', ApiType.ELEVENLABS, self.TTS.format(voice_id=voice_id), data={
            'text': text,
            'voice_settings': {
                'stability': float(os.environ.get('ELEVENLABS_STABILITY', 0.6)),
                'similarity_boost': float(os.environ.get('ELEVENLABS_SIMILARITY_BOOST', 0.3)),
            },
        })
        # elevenlabs returns raw mp3 bytes (non-json), so make_api_request hands back a Response
        return response.content


class SixtyDBProvider(TTSProvider):
    name = '60db'
    MYVOICES = 'myvoices'
    TTS = 'tts-synthesize'
    CACHE = Path('voices_60db.json')

    @property
    def voice_name(self) -> str:
        return os.environ.get('SIXTYDB_VOICE_NAME', '')

    def list_voices(self) -> list[dict[str, Any]]:
        cached = self._read_cache(self.CACHE)
        if cached is not None:
            return cached.get('data', []) if isinstance(cached, dict) else cached
        response = make_api_request('GET', ApiType.SIXTYDB, self.MYVOICES)
        if not response or not response.get('data'):
            raise Exception('No voices found!')
        self._write_cache(self.CACHE, response)
        # /myvoices only returns the user's own voices, so no premade filtering needed
        return response.get('data', [])

    def synthesize(self, voice_id: str, text: str) -> bytes:
        response = make_api_request('POST', ApiType.SIXTYDB, self.TTS, data={
            'text': text,
            'voice_id': voice_id,
            'output_format': 'mp3',  # mp3 keeps playback identical to the elevenlabs path
            'enhance': os.environ.get('SIXTYDB_ENHANCE', 'true').strip().lower() == 'true',
            'speed': float(os.environ.get('SIXTYDB_SPEED', 1)),
            'stability': float(os.environ.get('SIXTYDB_STABILITY', 50)),
            'similarity': float(os.environ.get('SIXTYDB_SIMILARITY', 75)),
        })
        if not response or not response.get('success'):
            message = response.get('message') if isinstance(response, dict) else 'no response'
            raise Exception(f'60db TTS failed: {message}')
        # 60db returns json with base64-encoded audio rather than raw bytes
        return base64.b64decode(response['audio_base64'])


PROVIDERS: dict[str, type[TTSProvider]] = {
    'elevenlabs': ElevenLabsProvider,
    '60db': SixtyDBProvider,
}


def resolve_provider_name(provider: str | None = None) -> str:
    name = (provider or os.environ.get('TTS_PROVIDER') or 'elevenlabs').strip().lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown TTS provider '{name}'. Choose one of: {', '.join(PROVIDERS)}")
    return name


def get_provider(provider: str | None = None) -> TTSProvider:
    return PROVIDERS[resolve_provider_name(provider)]()
