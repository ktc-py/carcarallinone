import io
from flask import Flask, render_template, request, send_file
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

@app.route('/')
def index():
    """提供前端網頁"""
    # Flask 會在 "templates" 資料夾中尋找 index.html
    return render_template('index.html')

@app.route('/generate-pdf', methods=['POST'])
def generate_pdf():
    """處理表單資料並生成 PDF"""
    license_plate = request.form['license_plate']
    english_name = request.form['english_name']
    id_number = request.form['id_number']

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    page_height = 792
    can.drawString(436, page_height - 70, license_plate)
    can.drawString(118, page_height - 144, english_name)
    can.drawString(435, page_height - 173, id_number)
    can.save()
    packet.seek(0)

    new_pdf = PdfReader(packet)
    
    # 這是修正後最關鍵的部分：
    # 我們使用 with open() 的安全寫法，並且模式是 "rb"
    with open("target.pdf", "rb") as f:
        existing_pdf = PdfReader(f)
        output = PdfWriter()
        page = existing_pdf.pages[0]
        page.merge_page(new_pdf.pages[0])
        output.add_page(page)

        output_stream = io.BytesIO()
        output.write(output_stream)
        output_stream.seek(0)

    return send_file(
        output_stream,
        as_attachment=True,
        download_name='generated_form.pdf',
        mimetype='application/pdf'
    )

# 部署到 Render 時，Gunicorn 會直接運行 app 物件，所以不需要下面這段
# 如果您想在本機測試，可以取消註解
# if __name__ == '__main__':
#     app.run(debug=True)