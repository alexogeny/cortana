"""
Module for interacting with chatgpt api
"""
import os
from typing import List, Literal, NoReturn, TypedDict
CHAT_COMPLETION = "chat/completions"
from euterpe.api import make_api_request, ApiType


class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

MessageList = List[Message]


def get_chat_completion(prompt: list[Message], max_tokens: int=90, temperature: float=1.1, stop: list[str]=["\n", " Human:", " AI:"]) -> str:
    response = make_api_request('POST', ApiType.OPENAI, CHAT_COMPLETION, data={
        "messages": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": stop,
        "stream": False,
        "model": os.environ.get("OPENAI_CHATGPT_MODEL")
    })
    if not response:
        raise Exception("No response from chatgpt api")

    return response.get('choices', [{}])[0].get('message', {}).get('content', None)


def append_user_input_to_message_list(message_list: MessageList, user_input: str) -> List[Message]:
    message_list.append({"role": "user", "content": user_input})
    return message_list


def append_bot_response_to_message_list(message_list: MessageList, bot_response: str) -> List[Message]:
    message_list.append({"role": "assistant", "content": bot_response})
    return message_list

def get_chatbot_response(message_list: MessageList) -> List[Message]:
    prompt = message_list
    bot_response = get_chat_completion(prompt)
    message_list = append_bot_response_to_message_list(message_list, bot_response)
    return message_list


def create_chat_gpt_prompt():
    name = os.environ.get('ASSISTANT_NAME', 'Assistant')
    user_name = os.environ.get('ASSISTANT_USER_NAME', 'User')
    humor = os.environ.get('ASSISTANT_HUMOR', 'friendly')
    personality = os.environ.get('ASSISTANT_PERSONALITY', 'kind')
    role = os.environ.get('ASSISTANT_ROLE', 'assistant')
    age = os.environ.get('ASSISTANT_AGE', '35')
    topic = os.environ.get('ASSISTANT_TOPIC_FOCUS', 'general')
    return ''.join((
        f"You are {name}, {user_name}'s {age} year old {role}. ",
        f"Your personality is {personality} and your humor is {humor}. ",
        f"Your main interests are {topic}.",
        f"You never refer to yourself as an AI, assistant, or bot.",
    ))

def create_message_list_with_prompt(message_list: MessageList = []) -> List[Message]:
    if not message_list or len(message_list) == 0:
        prompt = create_chat_gpt_prompt()
        message_list.append({
            "role": "system",
            "content": prompt
        })
    return message_list



def chat_loop() -> NoReturn:
    message_list = create_message_list_with_prompt()
    while True:
        user_input = input("You: ")
        message_list = append_user_input_to_message_list(message_list, user_input)
        message_list = get_chatbot_response(message_list)
        print(f"Bot: {message_list[-1]['content']}")


def pluggable_chat_loop(message_list: MessageList, user_input: str) -> List[Message]:
    message_list = append_user_input_to_message_list(message_list, user_input)
    message_list = get_chatbot_response(message_list)
    return message_list
