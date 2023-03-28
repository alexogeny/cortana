"""
Module for interacting with chatgpt api
"""
import os
import requests
CHAT_COMPLETION = "chat/completions"

def build_auth_header():
    return {
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
        "OpenAI-Organization": os.environ.get('OPENAI_ORG_ID'),
    }

def make_api_request(method, url, data=None):
    headers = build_auth_header()
    url = f"https://{os.environ.get('OPENAI_API_URL')}{url}"
    print(url)
    response = requests.request(method, url, headers=headers, json=data)
    return response


def get_chat_completion(prompt, max_tokens=90, temperature=1.1, stop=["\n", " Human:", " AI:"]):
    response = make_api_request('POST', CHAT_COMPLETION, data={
        "messages": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stop": stop,
        "stream": False,
        "model": os.environ.get("OPENAI_CHATGPT_MODEL")
    })
    # print(response)
    resp = response.json()
    # print(resp)
    return resp['choices'][0]['message']['content']


def append_user_input_to_message_list(message_list, user_input):
    message_list.append({"role": "user", "content": user_input})
    return message_list


def append_bot_response_to_message_list(message_list, bot_response):
    message_list.append({"role": "assistant", "content": bot_response})
    return message_list

def get_chatbot_response(message_list):
    prompt = message_list
    bot_response = get_chat_completion(prompt)
    message_list = append_bot_response_to_message_list(message_list, bot_response)
    return message_list


def create_message_list_with_prompt(message_list = []):
    if not message_list or len(message_list) == 0:
        message_list.append({
            "role": "system",
            "content": os.environ.get(
                "OPENAI_CHATGPT_SYSTEM_MESSAGE", "You are a helpful personal assistant named {VOICE_ASSISTANT_HOTWORD}."
            ).format(
                VOICE_ASSISTANT_HOTWORD=os.environ.get("VOICE_ASSISTANT_HOTWORD", "Assistant")
            )
        })
    return message_list



def chat_loop():
    message_list = create_message_list_with_prompt()
    while True:
        user_input = input("You: ")
        message_list = append_user_input_to_message_list(message_list, user_input)
        message_list = get_chatbot_response(message_list)
        print(f"Bot: {message_list[-1]['content']}")


def pluggable_chat_loop(message_list, user_input):
    message_list = append_user_input_to_message_list(message_list, user_input)
    message_list = get_chatbot_response(message_list)
    return message_list
