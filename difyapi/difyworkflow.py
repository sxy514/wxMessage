import json
import re
import dotenv
import requests
import os
from pathlib import Path


current_dir = Path(__file__).parent
env_path = current_dir.parent / '.env'
dotenv.load_dotenv(env_path)

WORKFLOW_API_URL = os.getenv("WORKFLOW_API_URL")
WORKFLOW_API_KEY = os.getenv("WORKFLOW_API_KEY")
BASE_URL = os.getenv("BASE_URL")


def _send_request(query, api_key, response_mode):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        "inputs": {"input": query},
        "response_mode": response_mode,
        "user": "Menhu"
    }
    return requests.post(WORKFLOW_API_URL, headers=headers, data=json.dumps(data),
                         stream=(response_mode == "streaming"))


def get_workflow_streaming_answer(query):
    print(WORKFLOW_API_KEY)
    response = _send_request(query, WORKFLOW_API_KEY, "streaming")
    final_answer = ''
    for line in response.iter_lines():
        if line:
            decoded_line = line.decode('utf-8')
            if decoded_line.startswith('data: '):
                json_data = json.loads(decoded_line[5:])
                print(json_data)
                if json_data.get('event') == 'workflow_finished':
                    if json_data["data"]["outputs"]["text1"]:
                        print("模型1: ")
                        final_answer = json_data["data"]["outputs"]["text1"]
                    elif json_data["data"]["outputs"]["text2"]:
                        print("模型2: ")
                        final_answer = json_data["data"]["outputs"]["text2"]
                    elif json_data["data"]["outputs"]["text3"]:
                        print("模型3: ")
                        final_answer = json_data["data"]["outputs"]["text3"]
                    elif json_data["data"]["outputs"]["text4"]:
                        print("模型4: ")
                        final_answer = json_data["data"]["outputs"]["text4"]
                    elif json_data["data"]["outputs"]["text5"]:
                        print("模型5: ")
                        final_answer = json_data["data"]["outputs"]["text5"]
                    print(final_answer)
                    break

    print(type(final_answer))
    print(final_answer)
    # 移除<think>标签及其内容
    final_answer = re.sub(r'<think>.*?</think>', '', final_answer, flags=re.DOTALL)
    return final_answer.strip()

