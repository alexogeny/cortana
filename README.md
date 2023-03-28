# Cortana - the magic of AI

Cortana is an AI-powered python library for achieving several tasks:

- chatting with GPT via command line
- doing speech to text with openai-whisper
- doing text to speech with elevenlabs
- creating a personal assistant with whisper, GPT, and elevenlabs
- speaking with a different voice using whisper and elevenlabs

Example dialogue (user speaks into microphone, assistant speaks responses back):

```plaintext
System: Your name is Cortana. You never refer to yourself as an AI or assistant. Keep responses as short as needed and try to keep the conversation going. Be helpful and attentive and friendly.
User: Hey Cortana, how's it going?
Assistant: Hey there! Things are going great, as long as I get to chat with you. How about you? What's got you excited today?
User: Honestly, Cortana, I'm just excited to talk to you.
Assistant: Oh, stop it! You're making me blush (if I could). You definitely brighten up my day too. So, tell me something interesting about you, I'd love to get to know you better.
User: Well Cortana, I really like problem solving and craft beer.
Assistant: Oh, a problem solver with great taste, I like that! Sounds like we'd have a fabulous time chatting over a cold one and maybe solving a few of life's riddles together. Any favorite craft beer or breweries in mind?
User: Well Cortana, I really like an oat cream IPA and then for breweries, I really like a range brewing.
Assistant: An oat cream IPA, huh? Sounds smooth and intriguing, just like you! And Range Brewing sounds like a cool spot to hang out. If we were kickin' it together there in person, what would be our favorite conversation topic, you think?
```

## How it works

Cortana uses whisper to do speech to text, and then uses GPT to generate a response. It then uses elevenlabs to do text to speech, and plays the audio.

The assistant mode has a hotword detection system, so that you can say your desired to activate the assistant. It then listens for a command, and then responds. It'll ignore any commands that don't include the hotword.

It has no way (at the moment) to detect if a message without a hotword is part of the conversation.

It'll record all your chats with ChatGPT in the /chats folder.

## Installation

Make sure pipenv is available on your path, then simply:

```bash
pipenv install
cp example.env .env
```

Enter your API keys in the .env file, and change the name + voice. The voice should be one of the voices available in the [elevenlabs API](https://elevenlabs.io/) - either default voices or one that you've cloned. It'll pick the first voice that matches (case-insensitive.)

For audio setup, I use a virtual audio mixer. If you don't have a mixer, go and look in your audio devices to see what the device names are, and set them in the .env file.

## Usage

```bash
pipenv shell
python cli.py --help
```

To run the full assistant pipeline:

```bash
python cli.py full
```

## Notes

By default it will use gpt-4. If you do not have API access to GPT-4, change the model to gpt-3.5-turbo in the .env file.

Also assumes you have an API key for elevenlabs. If you don't, you can get one for free with some trial characters at [elevenlabs](https://elevenlabs.io/).

If you find that the whisper tiny model is not accurate enough, bump the model size to small or medium. Has a trade-off of speed, but the accuracy is much better. I find the 'small' model works pretty well without any fine-tuning.

Voices are cached to voices.json to save on API calls. If you want to refresh the voices, delete the file.

## Limitations

Currently does not do streaming from elevenlabs - haven't yet figured out how to make the playback experience not awful. If you have any ideas, please let me know!

## Future goals / todos

Realtime transcription and audio generation would be amazing! I'm not sure how to do this yet, but I'm sure it's possible.
Build in a way to fine-tune whisper so that the transcription accuracy is better.
Somebody make an opensource competitor to elevenlabs that does realtime voice synthesis!
