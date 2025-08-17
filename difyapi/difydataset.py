import json
import os
import dotenv
import requests
from pathlib import Path


current_dir = Path(__file__).parent
env_path = current_dir.parent / '.env'
dotenv.load_dotenv(env_path)

DATASET_API_KEY = os.getenv('DATASET_API_KEY')
BASE_URL = os.getenv('BASE_URL')
DATASET_ID = os.getenv('DATASET_ID')
DOCUMENT_ID = os.getenv('DOCUMENT_ID')
SEGMENT_ID = os.getenv('SEGMENT_ID')


def get_all_datasets_id(api_key, page=1, limit=20):
    url = f'{BASE_URL}/v1/datasets'
    params = {
        'page': page,
        'limit': limit
    }
    headers = {
        'Authorization': 'Bearer {api_key}'.format(api_key=api_key),
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        print(f"\n获取数据集列表成功. Page: {page}, Limit: {limit}")
        datasets = response.json().get('data', [])
        for dataset in datasets:
            print(f"ID: {dataset['id']}, Name: {dataset['name']}")
        return response.json()

    else:
        return {'error': response.status_code, 'message': response.text}


get_all_datasets_id(DATASET_API_KEY)


def from_dataset_get_documents_list(api_key, dataset_id, page=1, limit=20):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    params = {
        'page': page,
        'limit': limit
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        print(f"\n获取数据集内的文档列表成功. 知识库ID: {dataset_id}")
        data = response.json()
        for document in data.get('data', []):
            print(f"Document ID: {document['id']}, Name: {document['name']}")
        return data
    else:
        print(f"查找文档失败. Status code: {response.status_code}, Error: {response.text}")
        return None


from_dataset_get_documents_list(DATASET_API_KEY, DATASET_ID)


def get_all_segments(api_key, dataset_id, document_id):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}/segments'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        response_data = response.json()
        print(f"\n从数据集 {dataset_id} 内的文档 {document_id} 的所有段落信息：")
        for segment in response_data['data']:
            print(f"Segment ID: {segment['id']}")
            print(f"Position: {segment['position']}")
            print(f"Document ID: {segment['document_id']}")
            print(f"Content: {segment['content']}")
            print(f"Answer: {segment['answer']}")
            print(f"Keywords: {segment['keywords']}")
            print(f"Status: {segment['status']}")
            print(f"Created At: {segment['created_at']}")
            print(f"Indexing At: {segment['indexing_at']}")
            print(f"Completed At: {segment['completed_at']}")
            print("-" * 40)
    else:
        print(f"Error: {response.status_code} - {response.text}")


# 获取segments的示例
# get_all_segments(
#     api_key=DATASET_API_KEY,
#     dataset_id=DATASET_ID,
#     document_id=DOCUMENT_ID
# )


def upload_text_to_create_document(api_key, dataset_id, filename, file_text, indexing_technique="high_quality",
                                   process_rule=None):
    if process_rule is None:
        process_rule = {"mode": "automatic"}
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/document/create-by-text'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': filename,
        'text': file_text,
        'indexing_technique': indexing_technique,
        'process_rule': process_rule
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("使用text创建文档成功")
        return response.json()
    else:
        print(f"文档创建失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None


# 上传函数还未做重复上传限制


def upload_file_to_create_document(dataset_id, api_key, file_path):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/document/create-by-file'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    data = {
        'data': '{"indexing_technique":"high_quality","process_rule":{"rules":{"pre_processing_rules":[{'
                '"id":"remove_extra_spaces","enabled":true},{"id":"remove_urls_emails","enabled":true}],'
                '"segmentation":{"separator":"###","max_tokens":500}},"mode":"custom"}}',
        'type': 'text/plain'
    }
    files = {
        'file': open(file_path, 'rb')
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    files['file'].close()
    if response.status_code == 200:
        response_data = response.json()
        document_id = response_data['document']['id']
        document_name = response_data['document']['name']
        batch_id = response_data['batch']

        print(f"\n上传的文档为 Document ID: {document_id}")
        print(f"文件: {document_name},已上传到知识库ID: {dataset_id}")
        print(f"上传文档的批处理号为 Batch ID: {batch_id}")
        return response_data
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None


# upload_file_to_create_document('ae54efd5-a8dd-4c8d-ab08-f6ff4a209137', API_KEY,
#                                'E:/Downloads/注意力就是你所需的一切.pdf')


def update_text_to_cover_document(api_key, dataset_id, document_id, new_name, new_text):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}/update-by-text'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'name': new_name,
        'text': new_text
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"文档更新成功, 文档ID: {document_id}")
        return response.json()
    else:
        print(f"文档更新失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")
        return None


def update_file_to_cover_document(api_key, dataset_id, document_id, file_path):
    import os
    file_name = os.path.basename(file_path)

    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}/update-by-file'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    data_json = f'''
    {{
        "name": "{file_name}",
        "indexing_technique": "high_quality",
        "process_rule": {{
            "rules": {{
                "pre_processing_rules": [
                    {{"id": "remove_extra_spaces", "enabled": true}},
                    {{"id": "remove_urls_emails", "enabled": true}}
                ],
                "segmentation": {{
                    "separator": "###",
                    "max_tokens": 500
                }}
            }},
            "mode": "custom"
        }}
    }}
    '''

    data = {'data': data_json}
    files = {'file': open(file_path, 'rb')}

    response = requests.post(url, headers=headers, data=data, files=files)
    files['file'].close()

    if response.status_code == 200:
        print(f"\n覆盖文档更新成功, 文档ID: {document_id} ,文件名称: {file_name}")
        return response.json()
    else:
        print(f"覆盖文档更新失败，状态码: {response.status_code}")
        print(f"错误信息: {response.text}")


def create_dataset(api_key, name):
    url = f'{BASE_URL}/v1/datasets'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    data = {
        'name': name,
        'permission': 'only_me'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("数据集创建成功:", response.json())
    else:
        print("创建数据集失败:", response.status_code, response.text)


def delete_dataset(api_key, dataset_id):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }
    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f'\n知识库 {dataset_id} 删除成功。')
    else:
        print(f'未能成功删除知识库,收到状态码: {response.status_code}, 响应内容: {response.text}')


def get_indexing_status(api_key, dataset_id, batch):
    """
    获取文档批次索引状态并打印详细信息

    参数：
    api_key: 认证用的API密钥
    dataset_id: 数据集ID
    batch: 文档批次号

    返回：
    包含状态信息的字典（同时会打印格式化信息）
    """
    from datetime import datetime
    url = f"{BASE_URL}/v1/datasets/{dataset_id}/documents/{batch}/indexing-status"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查HTTP错误

        data = response.json()

        # 提取并打印信息
        for item in data.get("data", []):
            print(f"\n批处理编号 {batch} 的索引状态信息：")
            print(f"状态: {item.get('indexing_status', '未知')}")
            print(f"进度: {item.get('completed_segments', 0)}/{item.get('total_segments', 0)} "
                  f"({(item['completed_segments'] / item['total_segments']) * 100:.1f}%)")

            # 时间戳转换函数
            def format_time(ts):
                return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S') if ts else "N/A"

            print(f"处理开始时间: {format_time(item.get('processing_started_at'))}")
            print(f"解析完成时间: {format_time(item.get('parsing_completed_at'))}")
            print(f"清洗完成时间: {format_time(item.get('cleaning_completed_at'))}")
            print(f"分割完成时间: {format_time(item.get('splitting_completed_at'))}")
            print(f"最终完成时间: {format_time(item.get('completed_at'))}")
            print(f"错误信息: {item.get('error') or '无'}")
            print("-" * 40)

        return data

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        return None
    except ValueError:
        print("响应解析失败")
        return None


def from_dataset_delete_documents(api_key, dataset_id, document_id):
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}'
    headers = {
        'Authorization': f'Bearer {api_key}'
    }

    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功

        # 解析响应
        response_data = response.json()
        result = response_data.get('result')

        if result == 'success':
            print(f"\n知识库 {dataset_id} 内的文档 {document_id} 删除成功。")
        else:
            print(f"文档{document_id} 删除失败，响应结果为：{result}")
    except Exception as err:
        print(f"错误发生: {err}")


def add_segment_to_document(dataset_id, document_id, api_key, segments):
    """
       创建文档段落并验证响应结果

       :param dataset_id: 数据集ID
       :param document_id: 文档ID
       :param api_key: API密钥
       :param segments: 要创建的段落列表，当知识库为Q&A格式时才能传递answer内容，否则仅能存储content,格式如下：
           [{"content": "文本内容", "answer": "答案", "keywords": ["关键词1"]}]
       :return: 操作成功返回True，失败返回False
       """
    url = f'{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}/segments'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        # 发送POST请求
        response = requests.post(
            url,
            headers=headers,
            data=json.dumps({"segments": segments})
        )

        # 打印原始响应信息（调试用）
        print(f"响应状态码: {response.status_code}")
        print("完整响应:", response.text)

        # 判断HTTP状态码
        if response.status_code != 200:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            return False

        # 解析JSON响应
        response_data = response.json()

        # 检查响应结构
        if 'data' not in response_data or not isinstance(response_data['data'], list):
            print("响应结构异常，缺少data字段")
            return False

        # 验证每个段落的创建状态
        all_success = True
        for segment in response_data['data']:
            print(f"\n创建的segment ID为: {segment.get('id', '无')}")
            print(f"状态: {segment.get('status', '无状态信息')}")

            if segment.get('status') != 'completed' or segment.get('error'):
                all_success = False
                print(f"创建失败，错误信息: {segment.get('error', '未知错误')}")

        # 最终结果判断
        if all_success:
            print(f"在数据集 {dataset_id} 内的文档 {document_id} 中新增的段落创建成功！")

            return True

        print("存在创建失败的段落")
        return False

    except requests.exceptions.RequestException as e:
        print(f"网络请求异常: {str(e)}")
        return False
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
        return False


# 创建测试段落
# test_segments = [{
#     "content": "百度百科是什么？",
#     "answer":  "百度百科已经收录了超2860万个词条",
#     "keywords": ["百度百科", "百度百科是什么？"]
# }]

# add_segment_to_document('ae54efd5-a8dd-4c8d-ab08-f6ff4a209137', '4ca71626-1468-4dc0-920e-ab24561d2461', API_KEY,
#                         test_segments)


def update_segment(api_key, dataset_id, document_id, segment_id, content, answer, keywords):
    """
    更新指定文档片段的详细信息

    参数:
    api_key: 认证token
    dataset_id: 数据集ID
    document_id: 文档ID
    segment_id: 片段ID
    content: 更新内容
    answer: 关联答案,仅在知识库为Q&A格式时有效
    keywords: 关键词列表
    """
    url = f"{BASE_URL}/v1/datasets/{dataset_id}/documents/{document_id}/segments/{segment_id}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "segment": {
            "content": content,
            "answer": answer,
            "keywords": keywords,
            "enabled": True
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # 检查HTTP错误

        result = response.json()
        if result['data']['status'] == 'completed':
            print(f"\nSegment ID: {result['data']['id']} 更新成功！")
            print(f"Position: {result['data']['position']}")
            print(f"Content: {result['data']['content']}")
            print(f"Answer: {result['data']['answer']}")
            print(f"Keywords: {', '.join(result['data']['keywords'])}")
            print(f"Enabled: {result['data']['enabled']}")
            print(f"Status: {result['data']['status']}")
            return True
        else:
            print(f"Segment {segment_id} update failed.")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP错误: {http_err}")
    except Exception as err:
        print(f"其他错误: {err}")
    return False

# update_segment(
#     api_key=API_KEY,
#     dataset_id="ae54efd5-a8dd-4c8d-ab08-f6ff4a209137",
#     document_id="4ca71626-1468-4dc0-920e-ab24561d2461",
#     segment_id="476afe02-f629-417b-8bf1-a37c01a3febe",
#     content="更新后asdasdA",
#     answer="asdasd",
#     keywords=[""]
# )
