from pathlib import Path
from rapid_table import RapidTable, VisTable
from rapidocr_onnxruntime import RapidOCR

class TableProcessor:
    def __init__(self, model_path, save_dir):
        self.table_engine = RapidTable(model_path=model_path)
        self.ocr_engine = RapidOCR()
        self.viser = VisTable()
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def process_image(self, img_path):
        ocr_result, _ = self.ocr_engine(img_path)
        table_html_str, table_cell_bboxes, elapse = self.table_engine(img_path, ocr_result)
        return table_html_str, table_cell_bboxes

    def save_results(self, img_path, table_html_str, table_cell_bboxes):
        save_html_path = self.save_dir / f"{Path(img_path).stem}.html"
        save_drawed_path = self.save_dir / f"vis_{Path(img_path).name}"
        self.viser(img_path, table_html_str, save_html_path, table_cell_bboxes, save_drawed_path)
        print(table_html_str)

# 使用示例
if __name__ == "__main__":
    model_path = './model/ch_ppstructure_mobile_v2_SLANet.onnx'
    save_dir = "./inference_results/"
    img_path = './data/table-image.jpg'

    processor = TableProcessor(model_path, save_dir)
    table_html_str, table_cell_bboxes = processor.process_image(img_path)
    processor.save_results(img_path, table_html_str, table_cell_bboxes)