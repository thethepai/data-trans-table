from pathlib import Path
import os
from rapid_table import RapidTable
from rapid_table import RapidTable, VisTable
from rapidocr_onnxruntime import RapidOCR

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
print(script_dir)

table_engine = RapidTable()
ocr_engine = RapidOCR()
viser = VisTable()

img_path = './data/table-image.jpg'

ocr_result, _ = ocr_engine(img_path)
table_html_str, table_cell_bboxes, elapse = table_engine(img_path, ocr_result)

save_dir = Path("./inference_results/")
save_dir.mkdir(parents=True, exist_ok=True)

save_html_path = save_dir / f"{Path(img_path).stem}.html"
save_drawed_path = save_dir / f"vis_{Path(img_path).name}"

viser(img_path, table_html_str, save_html_path, table_cell_bboxes, save_drawed_path)

print(table_html_str)