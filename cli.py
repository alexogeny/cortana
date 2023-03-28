"""
The CLI module for the project.
"""

import click

from cortana.app import full_pipeline, clone_pipeline
from cortana.stt import stt_loop
from cortana.tts import tts_loop
from cortana.cgpt import chat_loop


@click.group()
def cli():
    pass

@cli.command()
def tts() -> None:
    click.echo('Text to speech')
    tts_loop()

@cli.command()
def stt() -> None:
    click.echo('Speech to text')
    stt_loop()


@cli.command()
def chat_gpt() -> None:
    click.echo('chat gpt')
    chat_loop()

@cli.command()
@click.option('--with-tts/--no-tts', default=True, help='Include text-to-speech (TTS) in full mode')
def full(with_tts: bool) -> None:
    click.echo('Full mode')
    full_pipeline(with_tts=with_tts)

@cli.command()
def clone() -> None:
    click.echo('Clone mode')
    clone_pipeline()

if __name__ == '__main__':
    cli()
