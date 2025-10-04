import io
import os
from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    # 獲取使用者選擇的範本檔案
    pdf_template_filename = request.form.get('pdf_template')

    allowed_templates = ["target.pdf", "target2.pdf"]
    if not pdf_template_filename or pdf_template_filename not in allowed_templates:
        return "Invalid template selected", 400

    pdf_path = os.path.join(BASE_DIR, pdf_template_filename)

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    page_height = 792 # Letter 紙張高度

    # 根據不同的範本，讀取不同的資料並使用不同的座標
    if pdf_template_filename == 'target.pdf':
        # 使用 .get('reg_mark_1', '') 的安全方式讀取範本 1 的資料
        reg_mark = request.form.get('reg_mark_1', '')
        owner_name = request.form.get('owner_name_1', '')
        id_number = request.form.get('id_number_1', '')
        
        # 使用範本 1 的座標
        can.drawString(436, page_height - 70, reg_mark)
        can.drawString(118, page_height - 144, owner_name)
        can.drawString(435, page_height - 173, id_number)

    elif pdf_template_filename == 'target2.pdf':
        # 使用 .get('chassis_no_2', '') 的安全方式讀取範本 2 的資料
        chassis_no = request.form.get('chassis_no_2', '')
        engine_no = request.form.get('engine_no_2', '')
        reg_mark = request.form.get('reg_mark_2', '')
        owner_name = request.form.get('owner_name_2', '')
        scrap_date = request.form.get('scrap_date_2', '')
        
        # 使用範本 2 的座標
        can.drawString(249, page_height - 194, chassis_no)
        can.drawString(249, page_height - 220, engine_no)
        can.drawString(249, page_height - 245, reg_mark)
        can.drawString(249, page_height - 275, owner_name)
        can.drawString(275, page_height - 355, scrap_date)

    can.save()
    packet.seek(0)
    new_pdf_layer = PdfReader(packet)

    with open(pdf_path, "rb") as f:
        existing_pdf = PdfReader(f)
        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf_layer.pages[0])
        output.add_page(page)

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

    return send_file(
        output_stream,
        as_attachment=True,
        download_name=f'generated_{os.path.splitext(pdf_template_filename)[0]}.pdf',
        mimetype='application/pdf'
    )

# 部署到 Render 時，Gunicorn 會直接運行 app 物件
# 在本機測試時可以取消下面這段的註解
# if __name__ == '__main__':
#    app.run(debug=True)