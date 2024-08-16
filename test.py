import json
import re
import os
import sys
from typing import Dict, List
from markdownify import markdownify as md
from rapidocr_onnxruntime import RapidOCR
from rapid_table import RapidTable

table_engine = RapidTable()
ocr_engine = RapidOCR()

def read_markdown_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_markdown_file(file_path: str, content: str):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def read_json_file(file_path: str) -> List[Dict]:
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def perform_ocr(img_path: str) -> str:
    ocr_result, _ = ocr_engine(img_path)
    table_html_str, table_cell_bboxes, elapse = table_engine(img_path, ocr_result)
    return md(table_html_str)

def replace_image_with_ocr_content(markdown_content: str, image_path: str, ocr_content: str) -> str:
    # 这里假设图片在Markdown中的格式是 ![alt text](image_path)
    image_pattern = f"!\\[.*?\\]\\({re.escape(image_path)}\\)"
    return re.sub(image_pattern, ocr_content, markdown_content)

def find_markdown_file(base_path: str) -> str:
    auto_folder = os.path.join(base_path, 'auto')
    for file in os.listdir(auto_folder):
        if file.endswith('.md'):
            return os.path.join(auto_folder, file)
    return None

def main(base_path: str):
    # 查找Markdown文件
    markdown_file_path = find_markdown_file(base_path)
    if not markdown_file_path:
        print(f"错误：在 {os.path.join(base_path, 'auto')} 中未找到 Markdown 文件")
        return

    # 构建JSON文件路径
    json_filename="middle.json"
    json_file_path = os.path.join(base_path, "auto", json_filename)

    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误：无法找到JSON文件: {json_file_path}")
        return

    # 读取Markdown文件
    markdown_content = read_markdown_file(markdown_file_path)

    # 读取JSON文件
    json_data = read_json_file(json_file_path)
    json_data_tables=[a['tables'] for a in json_data['pdf_info']]
    json_data_tables=[a[0] for a in json_data_tables if len(a)>0]
    json_data_tables=[block for a in json_data_tables for block in a['blocks']]
    json_data_tables=[a["lines"][0]['spans'][0] for a in json_data_tables if len(a['lines'])>0]
    print(json_data_tables)
    # 计算需要OCR处理的项目数量
    total_items = sum(1 for item in json_data_tables if item['type'] == 'table' and 'image_path' in item)

    # 处理JSON数据
    ocr_count = 0

    # 处理JSON数据
    for item in json_data_tables:
        if item['type'] == 'table' and 'image_path' in item:
            img_path = os.path.join(base_path, 'auto/images', item['image_path'])
            if os.path.exists(img_path):
                ocr_count += 1
                ocr_content = perform_ocr(img_path)
                markdown_content = replace_image_with_ocr_content(markdown_content, "images/"+item['image_path'], ocr_content)
                print(f"OCR 进度: {ocr_count}/{total_items}")
            else:
                print(f"警告：图片文件不存在 {img_path}")

    # 保存更改后的Markdown文件
    write_markdown_file(markdown_file_path.replace(".md","_table.md"), markdown_content)
    print(f"处理完成，已更新 {markdown_file_path} 文件。")


if __name__ == "__main__":

    base_path="./data/pdf2"
    main(base_path)

    #运行后会生成新的md文件，文件名为原文件名_table.md