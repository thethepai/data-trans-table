import json
import re
import os
from typing import Dict, List
from markdownify import markdownify as md
from rapidocr_onnxruntime import RapidOCR
from rapid_table import RapidTable

class MarkdownFileHandler:
    @staticmethod
    def read_markdown_file(file_path: str) -> str:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    @staticmethod
    def write_markdown_file(file_path: str, content: str):
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

class JsonFileHandler:
    @staticmethod
    def read_json_file(file_path: str) -> List[Dict]:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

class OCRProcessor:
    def __init__(self, ocr_engine, table_engine):
        self.ocr_engine = ocr_engine
        self.table_engine = table_engine

    def perform_ocr(self, img_path: str) -> str:
        ocr_result, _ = self.ocr_engine(img_path)
        table_html_str, table_cell_bboxes, elapse = self.table_engine(img_path, ocr_result)
        print(table_html_str)
        return table_html_str

    def convert_html_to_markdown(self, html_content: str) -> str:
        return md(html_content)

class MarkdownUpdater:
    @staticmethod
    def replace_image_with_ocr_content(markdown_content: str, image_path: str, ocr_content: str) -> str:
        image_pattern = f"!\\[.*?\\]\\({re.escape(image_path)}\\)"
        return re.sub(image_pattern, ocr_content, markdown_content)

class MainProcessor:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.ocr_processor = OCRProcessor(RapidOCR(), RapidTable(model_path='./model/ch_ppstructure_mobile_v2_SLANet.onnx'))

    def find_markdown_file(self) -> str:
        auto_folder = os.path.join(self.base_path, 'auto')
        for file in os.listdir(auto_folder):
            if file.endswith('.md'):
                return os.path.join(auto_folder, file)
        return None

    def process(self):
        markdown_file_path = self.find_markdown_file()
        if not markdown_file_path:
            print(f"错误：在 {os.path.join(self.base_path, 'auto')} 中未找到 Markdown 文件")
            return

        json_filename = "middle.json"
        json_file_path = os.path.join(self.base_path, "auto", json_filename)

        if not os.path.exists(json_file_path):
            print(f"错误：无法找到JSON文件: {json_file_path}")
            return

        markdown_content = MarkdownFileHandler.read_markdown_file(markdown_file_path)
        json_data = JsonFileHandler.read_json_file(json_file_path)
        json_data_tables = [a['tables'] for a in json_data['pdf_info']]
        json_data_tables = [a[0] for a in json_data_tables if len(a) > 0]
        json_data_tables = [block for a in json_data_tables for block in a['blocks']]
        json_data_tables = [a["lines"][0]['spans'][0] for a in json_data_tables if len(a['lines']) > 0]
        print(json_data_tables)

        total_items = sum(1 for item in json_data_tables if item['type'] == 'table' and 'image_path' in item)
        ocr_count = 0

        for item in json_data_tables:
            if item['type'] == 'table' and 'image_path' in item:
                img_path = os.path.join(self.base_path, 'auto/images', item['image_path'])
                if os.path.exists(img_path):
                    ocr_count += 1
                    table_html_str = self.ocr_processor.perform_ocr(img_path)
                    ocr_content = md(table_html_str)
                    markdown_content = MarkdownUpdater.replace_image_with_ocr_content(markdown_content, "images/" + item['image_path'], ocr_content)
                    print(f"OCR 进度: {ocr_count}/{total_items}")
                else:
                    print(f"警告：图片文件不存在 {img_path}")

        MarkdownFileHandler.write_markdown_file(markdown_file_path.replace(".md", "_table.md"), markdown_content)
        print(f"处理完成，已更新 {markdown_file_path} 文件。")

if __name__ == "__main__":
    base_path = "./data/pdf2"
    processor = MainProcessor(base_path)
    processor.process()