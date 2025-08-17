import json
import re
import os
import dotenv
import requests

from pathlib import Path


current_dir = Path(__file__).parent
env_path = current_dir.parent / '.env'
dotenv.load_dotenv(env_path)

BASE_URL = os.getenv("BASE_URL")
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")
AGENT_API_KEY = os.getenv("AGENT_API_KEY")


def _send_request(query, api_key, response_mode):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        "inputs": {"text": query},
        "query": query,
        "response_mode": response_mode,
        "user": "Menhu"
    }
    return requests.post(API_URL, headers=headers, data=json.dumps(data), stream=(response_mode == "streaming"))


def _parse_response(response, response_mode):
    try:
        if response_mode == "blocking":
            response_data = response.json()
            return response_data['answer']
        elif response_mode == "streaming":
            final_answer = ''
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        message = decoded_line[5:]
                        if message == '[DONE]':
                            break
                        json_data = json.loads(message)
                        answer_content = json_data.get('answer', '')
                        final_answer += answer_content
            return final_answer
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error: {e}"


def send_message_to_dify(query):
    response = _send_request(query, API_KEY, "blocking")
    return _parse_response(response, "blocking")


def send_message_to_dify_streaming(query):
    response = _send_request(query, API_KEY, "streaming")
    return _parse_response(response, "streaming")


def get_agent_streaming_answer(query):
    response = _send_request(query, AGENT_API_KEY, "streaming")
    final_answer = ''
    has_image = False  # 添加一个标志来判断是否有图片
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_data = json.loads(decoded_line[5:])
                    if json_data.get('event') == 'agent_message':
                        final_answer += json_data.get('answer', '')
                    elif json_data.get('event') == 'message_file':
                        file_url = json_data.get('url')
                        full_file_url = f"{BASE_URL}/{file_url}"
                        if file_url:
                            download_image(full_file_url)
                            has_image = True  # 检测到图片事件时设置标志为True
                    elif json_data.get('event') == 'message_end':
                        break
    except (json.JSONDecodeError, KeyError) as e:
        return f"Error: {e}", has_image  # 返回错误信息和标志
        # 移除<think>标签及其内容
    final_answer = re.sub(r'<think>.*?</think>', '', final_answer, flags=re.DOTALL)
    return final_answer.strip(), has_image  # 返回最终答案和标志


def download_image(url):
    try:
        image_response = requests.get(url, stream=True)
        image_response.raise_for_status()
        with open("downloaded_image.png", 'wb') as f:
            for chunk in image_response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("图片已成功下载为 downloaded_image.png")
    except Exception as e:
        print(f"下载图片时出错: {e}")

