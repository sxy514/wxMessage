import os
import dotenv
from flask import Flask, request, jsonify, send_from_directory, request, abort

from difyapi.difyworkflow import get_workflow_streaming_answer

dotenv.load_dotenv()
app = Flask(__name__)

X_API_KEY = os.getenv('X_API_KEY')

# 设置文件和图片的存储路径
file_folder = './img'
image_folder = './img'

# 确保目录存在
os.makedirs(file_folder, exist_ok=True)
os.makedirs(image_folder, exist_ok=True)


def check_api_key():
    # 从请求头中获取API Key
    api_key = request.headers.get('X-API-Key')
    if api_key != X_API_KEY:
        abort(403)  # 如果API Key不正确，返回403 Forbidden


# 存储处理后的回复消息的列表
response_messages = []


def handle_message(user_message):
    # 这里可以添加你的消息处理逻辑
    # 例如，简单的消息回复,在这里将信息发送到dify
    if user_message is not None:
        # 当用户问题等于查询日报时
        if '查询日报' in user_message:
            # 调用日报查询API
            aire = "当前的PM进度为：100%。"
            return aire
        else:
            aire = get_workflow_streaming_answer(user_message)
            return aire


@app.route('/process_message', methods=['POST'])
def process_message():
    check_api_key()
    try:
        # 从请求中获取用户消息
        user_message = request.form['message']
        print(f"接收到的消息: {user_message}")

        # 调用消息处理函数
        processed_message = handle_message(user_message)

        # 将处理后的回复消息存储在列表中
        response_messages.append(processed_message)
        print(f"处理后的回复消息: {processed_message}")

        # 返回成功状态和回复的消息
        return jsonify({'status': 'success', 'response_message': processed_message}), 200
    except Exception as e:
        print(f"发生了一个意外的错误: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/get_response', methods=['GET'])
def get_response():
    check_api_key()
    try:
        if response_messages:
            response_message = response_messages.pop(0)  # 移除并获取第一个回复消息
            print(f"发送给客户端的回复消息: {response_message}")
            return jsonify({'status': 'success', 'response_message': response_message}), 200
        else:
            return jsonify({'status': 'no_response', 'message': "没有可用的回复消息"}), 204
    except Exception as e:
        print(f"发生了一个意外的错误: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# 下载文件
@app.route('/download_file/<filename>')
def download_file(filename):
    check_api_key()  # 调用API Key验证函数
    # 检查文件是否存在
    file_path = os.path.join(file_folder, filename)
    if not os.path.exists(file_path):
        return '文件不存在', 404
    # 发送文件
    return send_from_directory(file_folder, filename, as_attachment=True)


# 下载图片
@app.route('/download_image/<filename>')
def download_image(filename):
    check_api_key()  # 调用API Key验证函数
    # 检查图片是否存在
    image_path = os.path.join(image_folder, filename)
    if not os.path.exists(image_path):
        return '图片不存在', 404
    # 发送图片
    return send_from_directory(image_folder, filename, as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

