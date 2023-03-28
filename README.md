# Euterpe - the magic of music

Euterpe is an AI-powered python library for achieving several tasks:

- chatting with GPT via command line
- doing speech to text with openai-whisper
- doing text to speech with elevenlabs
- creating a personal assistant with whisper, GPT, and elevenlabs
- speaking with a different voice using whisper and elevenlabs

## Installation

Make sure pipenv is available on your path, then simply:

```bash
pipenv install
```

## Usage

```bash
pipenv shell
python cli.py --help
```

## Notes

By default it will use gpt-4. If you do not have API access to GPT-4, change the model to gpt-3.5-turbo in the .env file.

Also assumes you have an API key for elevenlabs. If you don't, you can get one for free with some trial characters at [elevenlabs](https://elevenlabs.io/).

## Limitations

Currently does not do streaming from elevenlabs - haven't yet figured out how to make the playback experience not awful. If you have any ideas, please let me know!

## Future goals / todos

Realtime transcription and audio generation would be amazing! I'm not sure how to do this yet, but I'm sure it's possible.
Build in a way to fine-tune whisper so that the transcription accuracy is better.
