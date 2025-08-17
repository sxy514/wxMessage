import base64
import datetime
import os
import re
import subprocess
import time
from io import BytesIO
from PIL import Image
import queue
import threading

import pyautogui
import pyperclip
import win32clipboard
import win32con
import win32gui
import dotenv
from pywinauto import Application
import requests  # 用于HTTP请求
from flask import Flask, request, jsonify, abort
from werkzeug.utils import secure_filename

# 修改为你的远程服务器的实际地址
BASE_URL = "http://127.0.0.1:5000"
REMOTE_SERVER_URL = f"{BASE_URL}/process_message"

# 存储回复消息的列表
response_messages = []
# 存储接收的消息的队列
received_messages = queue.Queue()

# 初始化Flask应用
app = Flask(__name__)

# 创建一个锁来确保同一时间只有一个线程可以访问剪切板和屏幕资源
clipboard_lock = threading.Lock()

# 创建一个事件来通知线程停止
stop_event = threading.Event()
dotenv.load_dotenv()
X_API_KEY = os.environ.get("X_API_KEY")
HEADERS = {'X-API-Key': X_API_KEY}
print(X_API_KEY)


def check_api_key():
    # 从请求头中获取API Key
    api_key = request.headers.get('X-API-Key')
    # 验证API Key是否正确
    if api_key != X_API_KEY:
        abort(403)  # 如果API Key不正确，返回403 Forbidden


@app.route('/receive_message', methods=['POST'])
def receive_message():
    try:
        check_api_key()
        data = request.json

        if data:
            received_messages.put(data)  # 将整个JSON对象存入队列

        return jsonify({'status': 'success', 'messages': response_messages}), 200
    except Exception as e:
        print(f"接收消息时发生了一个意外的错误: {e}")
        return jsonify({'status': 'error', 'error': str(e)}), 500


def save_file_from_base64(data, filename):
    """将base64编码的文件保存到指定路径"""
    file_path = os.path.join("./img", filename)
    try:
        with open(file_path, "wb") as fh:
            fh.write(base64.b64decode(data))
        return filename
    except Exception as e:
        print(f"Error saving file: {e}")
        return None


def send_copy_file_to_clipboard(file_path):
    with clipboard_lock:
        # 使用PowerShell命令复制文件引用到剪切板
        powershell_command = f'Get-Item "{file_path}" | Set-Clipboard'
        subprocess.run(["powershell", "-Command", powershell_command])
        # 延迟一段时间以确保数据已复制
        time.sleep(1)

        # send
        pyautogui.moveTo(822, 620, duration=0.2)
        pyautogui.click()
        time.sleep(1)

        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)

        pyautogui.hotkey('Enter')
        time.sleep(1)


def open_menhu():
    app = Application("uia").start(
        r"D:\ProgramFile\WeChat\WeChat.exe")  # 打开程序，
    dlg = app["微信"]  # 选择窗口
    handle = win32gui.FindWindow(None, '微信')
    time.sleep(3)
    # 获取窗口的位置信息
    left, top, right, bottom = win32gui.GetWindowRect(handle)
    # 窗口长宽
    width = right - left
    height = bottom - top
    if width != 1024 or height != 600 or left > 306 or left < 304 or top > 100 or top < 98:
        win32gui.SetWindowPos(handle,
                              win32con.HWND_NOTOPMOST,  # 设置的窗口位置，最上面,置顶：HWND_TOPMOST,取消置顶：HWND_NOTOPMOST
                              305,  # x坐标
                              99,  # y坐标
                              1024,  # 窗口长度
                              600,  # 窗口宽度
                              win32con.SWP_SHOWWINDOW  # 显示窗口
                              )
    return left, top, width, height


def job(usermessage):
    if usermessage is not None:
        send_message_to_remote_server(usermessage)


def send_message(message):
    with clipboard_lock:
        find_chat("img/group.PNG")
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(date, message, "发送至群消息")
        pyperclip.copy(message)
        time.sleep(1)
        pyautogui.moveTo(822, 620, duration=0.2)
        pyautogui.click()
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.hotkey('Enter')
        time.sleep(1)


def find_chat(groupname):
    try:
        # 寻找群/人 的图片
        left0, top0, width0, height0 = pyautogui.locateOnScreen(groupname, confidence=0.8)
        # 寻找图片的中心
        center0 = pyautogui.center((left0, top0, width0, height0))
        pyautogui.click(center0)
        # 移动至信息的界面
        pyautogui.move(500, 0, duration=0.2)
        # 获取最新消息
        pyautogui.scroll(-2500)
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "找到了群聊")

    except pyautogui.ImageNotFoundException:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "未找到指定的群/人")
        return None
    except Exception as e:
        print(f"发生了一个意外的错误: {e}")
        return None


def find_center_click(img_name):
    try:
        left0, top0, width0, height0 = pyautogui.locateOnScreen(img_name, confidence=0.8)
        center0 = pyautogui.center((left0, top0, width0, height0))
        pyautogui.click(center0)
    except pyautogui.ImageNotFoundException:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "未找到指定的图片")
        return None


def message_to_clipboard(xuqiupath):
    with clipboard_lock:
        try:
            left0, top0, width0, height0 = pyautogui.locateOnScreen(xuqiupath, confidence=0.8)
            center0 = pyautogui.center((left0, top0, width0, height0))
            pyautogui.click(center0)
            pyautogui.click(center0, clicks=1, button='right')
            # 等待右键菜单弹出
            pyautogui.sleep(0.5)
            # 移动到“复制”选项的位置
            pyautogui.move(10, 10, duration=0)
            # 点击“复制”选项
            pyautogui.click()
            # pyautogui.sleep(1)
            # left0, top0, width0, height0 = pyautogui.locateOnScreen("img/copy.PNG", confidence=0.8)
            # center0 = pyautogui.center((left0, top0, width0, height0))
            # pyautogui.click(center0)
            # 从剪切板提取文本内容
            copied_text = pyperclip.paste()
            # clean文本内容
            cleaned_text = re.sub(r'AI', '', copied_text)

            # 删除刚才的消息内容
            pyautogui.click(center0, clicks=1, button='right')
            # pyautogui.sleep(1)
            # pyautogui.move(10, 230, duration=0.2)
            # pyautogui.click()
            left0, top0, width0, height0 = pyautogui.locateOnScreen("img/delete.PNG", confidence=0.8)
            center0 = pyautogui.center((left0, top0, width0, height0))
            pyautogui.click(center0)
            left0, top0, width0, height0 = pyautogui.locateOnScreen("img/clickDelete.PNG", confidence=0.8)
            center0 = pyautogui.center((left0, top0, width0, height0))
            pyautogui.click(center0)
            return cleaned_text
        except pyautogui.ImageNotFoundException:
            print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "未找到指定的消息")
        except Exception as e:
            print(f"发生了一个意外的错误: {e}")


def find_message(xuqiupath):
    try:
        rv = pyautogui.locateOnScreen(xuqiupath, confidence=0.6)
    except pyautogui.ImageNotFoundException:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "未找到指定的消息")
        return
    except Exception as e:
        print(f"发生了一个意外的错误: {e}")
        return
    if rv:
        job(message_to_clipboard(xuqiupath))


def send_image_to_clipboard(image_path):
    with clipboard_lock:
        try:
            # 打开图片
            image = Image.open(image_path)
            # 创建一个字节流
            output = BytesIO()
            # 将图片保存到字节流中，格式为BMP，因为剪切板通常接受BMP格式的图片
            image.save(output, "BMP")
            # 获取字节流数据
            data = output.getvalue()[14:]
            output.close()

            # 打开剪切板
            win32clipboard.OpenClipboard()
            # 清空剪切板
            win32clipboard.EmptyClipboard()
            # 设置剪切板的内容为图片数据
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            # 关闭剪切板
            win32clipboard.CloseClipboard()

            # 延迟一段时间以确保图片数据已复制
            time.sleep(1)

            # 点击输入框位置（请根据实际情况调整坐标）
            pyautogui.moveTo(822, 620, duration=0.2)
            pyautogui.click()
            time.sleep(1)

            # 使用快捷键粘贴图片
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(1)

            # 发送图片
            pyautogui.hotkey('Enter')
            time.sleep(1)

        except Exception as e:
            print(f"发生了一个意外的错误: {e}")


def send_message_to_remote_server(usermessage):
    try:
        # 发送消息到远程服务器
        response = requests.post(REMOTE_SERVER_URL, headers=HEADERS, data={'message': usermessage})
        if response.status_code == 200:
            response_json = response.json()
            print(response_json)
            if response_json['status'] == 'success':
                response_message = response_json['response_message']
                response_messages.append(response_message)
                print("消息已发送到远程服务器，并成功接收回复")
            else:
                print("远程服务器处理消息失败:", response_json['message'])
                send_message("远程服务处理消息失败，请检查原因")
        else:
            print("发送消息到远程服务器失败，状态码：", response.status_code)
            send_message("远程服务处理消息失败，请检查原因")
    except Exception as e:
        print(f"发生了一个意外的错误: {e}")
        send_message("远程服务处理消息失败，请检查原因")


def process_response_messages():
    if response_messages:
        rvmessage = response_messages.pop(0)  # 移除并获取第一个回复消息
        send_message(rvmessage)  # 发送回复消息到群聊


# 处理接收到的消息
def process_received_messages():
    while not stop_event.is_set() and not received_messages.empty():
        data = received_messages.get()  # 获取并移除队列中的第一个消息
        rvmessage = data.get('message')
        img_data = data.get('img')
        img_filename = data.get('img_filename', 'default.jpg')
        files_data = data.get('files', [])

        if rvmessage:
            print(rvmessage)
            send_message(rvmessage)  # 发送消息到群聊

        if img_data:
            saved_img_filename = save_file_from_base64(img_data, secure_filename(img_filename))
            print(f"接收到图片 {saved_img_filename}")
            send_copy_file_to_clipboard(f"img/{saved_img_filename}")

        for file_data in files_data:
            file_filename = file_data.get('filename', 'default.file')
            file_data_base64 = file_data.get('data', '')
            if file_data_base64:
                saved_file_filename = save_file_from_base64(file_data_base64, secure_filename(file_filename))
                print(f"接收到文件 {saved_file_filename}")
                send_copy_file_to_clipboard(f"img/{saved_file_filename}")
            else:
                response_messages.append(f'文件 {file_filename} 未接收到有效数据')


def run_flask_app():
    app.run(host='0.0.0.0', port=5001)


if __name__ == '__main__':
    open_menhu()
    find_chat('img/group.png')

    # 启动Flask应用
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    try:
        while not stop_event.is_set():
            message = message_to_clipboard('img/xuqiu2.png')
            if message:
                job(message)
            process_response_messages()  # 处理并发送AI回复消息
            process_received_messages()  # 处理并发送接收到的报警消息
            time.sleep(5)
    except KeyboardInterrupt:
        print("主程序终止中...")
        stop_event.set()
        shutdown_server()
        flask_thread.join()  # 等待Flask线程结束
        print("Flask线程已结束")
