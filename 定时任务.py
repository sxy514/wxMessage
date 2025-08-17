import base64
import os

import schedule
import time
import requests

from flaskServer import X_API_KEY

CLIENT_BASE_URL = "http://127.0.0.1:5001"


class DataChecker:
    def __init__(self, name, check_function, interval=10):
        self.name = name
        self.check_function = check_function
        self.interval = interval

    def check_data(self):
        print(f"正在检查数据: {self.name}")
        result = self.check_function()
        print(f"检查结果: {result}")


def check_aohs01_transferdata():
    # 打印时间
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    send_data_to_menhu("AOHS01搬送能力检测结果：25.0")

    # 模拟检测
    return 25.0


def check_pressure():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 模拟检测
    return 1.013


def check_humidity():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 模拟检测
    return 45.0


def check_light_intensity():
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # 模拟强度检测
    return 500.0


def add_checker(checker):
    schedule.every(checker.interval).seconds.do(checker.check_data)


def send_data_to_menhu(message):
    url = f"{CLIENT_BASE_URL}/receive_message"
    headers = {"X-API-Key": X_API_KEY}

    message = message
    response = requests.post(url, headers=headers, json={'message': message})
    if response.status_code == 200:
        print("数据发送成功")
    else:
        print("数据发送失败")


def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')

    print("文件转换为base64")
    return encoded_string


IMAGE_PATH = "downloaded_image.png"
FILE_PATH = "dailyreport.xlsx"


def send_file_to_menhu(message=None, image_path=None, file_paths=None):
    url = f"{CLIENT_BASE_URL}/receive_message"
    headers = {"X-API-Key": "AMHS001"}
    data = {}

    if message:
        data["message"] = message

    if image_path:
        data["img"] = file_to_base64(image_path)
        data["img_filename"] = os.path.basename(image_path)

    if file_paths:
        data["files"] = []
        for file_path in file_paths:
            file_data = {
                "filename": os.path.basename(file_path),
                "data": file_to_base64(file_path)
            }
            data["files"].append(file_data)

    print(data)
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        print("数据发送到门户成功")
    else:
        print("数据发送到门户失败")


# 使用示例
# send_file_to_menhu(message="这是第一条消息")
send_file_to_menhu(message="这是第二条消息", image_path="./img/chat_screenshot.png")
send_file_to_menhu(message="这是第三条消息", image_path="img/group.PNG",
                   file_paths=["dailyreport.xlsx", "./img/chat_screenshot.png"])


def main():
    temperature_checker = DataChecker("AOHS01搬送能力", check_aohs01_transferdata, interval=20)
    # pressure_checker = DataChecker("设备报警数据", check_pressure, interval=10)
    # humidity_checker = DataChecker("搬送命令分析", check_humidity, interval=10)
    # light_intensity_checker = DataChecker("数据", check_light_intensity, interval=10)

    add_checker(temperature_checker)
    # add_checker(pressure_checker)
    # add_checker(humidity_checker)
    # add_checker(light_intensity_checker)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
