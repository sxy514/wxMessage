import requests
import base64
import os

# 定义文件路径变量
IMAGE_PATH = "./img/downloaded_image.png"
FILE_PATH = "./img/dailyreport.xlsx"


# 定义函数来读取文件并将其转换为base64编码
def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode('utf-8')

    print(encoded_string)
    return encoded_string


# 定义API的URL
url = "http://127.0.0.1:5001/receive_message"

headers = {"X-API-Key": "AMHS001"}

# 定义要发送的数据
data = {
    "message": "这是新报警一个消息",
    "img": file_to_base64(IMAGE_PATH),  # 图片的base64编码
    "img_filename": os.path.basename(IMAGE_PATH),  # 图片的文件名
    "files": [
        {
            "filename": os.path.basename(FILE_PATH),  # PDF文件的文件名
            "data": file_to_base64(FILE_PATH)  # PDF文件的base64编码
        },
        # {
        #     "filename": os.path.basename(FILE_PATH),  # Excel文件的文件名
        #     "data": file_to_base64(FILE_PATH)  # Excel文件的base64编码
        # }
    ]
}


print(data)
# 发送POST请求
response = requests.post(url, headers=headers, json=data)

# 打印响应
print(response.json())
