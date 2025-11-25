import io
import os
from flask import Flask, render_template, request, send_file
from pypdf import PdfWriter, PdfReader
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
    
    # Render 部署常見錯誤檢查：確認 PDF 檔案真的存在
    if not os.path.exists(pdf_path):
        return f"錯誤：找不到範本檔案 '{pdf_template_filename}'。請確認檔案已上傳至 GitHub。", 500

    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    page_height = 792 # Letter 紙張高度 (792pt)

    # 根據不同的範本，讀取不同的資料並使用不同的座標
    if pdf_template_filename == 'target.pdf':
        # --- 1. 從網頁表單接收資料 (對應 index.html 的 name) ---
        VehicleRegistrationMark = request.form.get('VehicleRegistrationMark', '')
        Date = request.form.get('Date', '')
        EngName = request.form.get('EngName', '')
        ChiName = request.form.get('ChiName', '')
        HKID = request.form.get('HKID', '')
        HKID2 = request.form.get('HKID2', '')
        company_contact = request.form.get('company_contact', '')
        
        flat = request.form.get('flat', '')
        floor = request.form.get('floor', '')
        blk = request.form.get('blk', '')
        building = request.form.get('building', '')
        street = request.form.get('street', '')
        district = request.form.get('district', '')
        
        # 處理勾選框：如果有勾選，設為 'X'，否則為空字串
        hk = 'X' if request.form.get('hk') else ''
        kl = 'X' if request.form.get('kl') else ''
        nt = 'X' if request.form.get('nt') else ''
        
        registration_class = request.form.get('registration_class', '')
        ChassisOrVin = request.form.get('ChassisOrVin', '')
        C_A = 'X' if request.form.get('C_A') else ''
        
        # --- 2. 寫入 PDF (使用你測量的座標) ---
        # 如果需要支援中文，請在此處設置字型 (需有字型檔)
        # can.setFont("MsYahei", 10) 

        can.drawString(409, page_height - 67, VehicleRegistrationMark)
        can.drawString(340, page_height - 735, Date)
        
        can.drawString(112, page_height - 134, EngName)
        can.drawString(125, page_height - 161, ChiName)
        can.drawString(412, page_height - 161, HKID)
        can.drawString(531, page_height - 164, HKID2)
        can.drawString(386, page_height - 187, company_contact)
        
        can.drawString(25, page_height - 261, flat)
        can.drawString(97, page_height - 261, floor)
        can.drawString(213, page_height - 261, blk)
        can.drawString(25, page_height - 285, building)
        can.drawString(27, page_height - 311, street)
        can.drawString(25, page_height - 335, district)
        
        can.drawString(276, page_height - 337, hk)
        can.drawString(354, page_height - 337, kl)
        can.drawString(420, page_height - 337, nt)
        
        can.drawString(47, page_height - 530, registration_class)
        can.drawString(125, page_height - 552, ChassisOrVin)
        can.drawString(28, page_height - 606, C_A)


    elif pdf_template_filename == 'target2.pdf':
        # 範本 2 的變數讀取
        chassis_no = request.form.get('chassis_no_2', '')
        engine_no = request.form.get('engine_no_2', '')
        reg_mark = request.form.get('reg_mark_2', '')
        owner_name = request.form.get('owner_name_2', '')
        scrap_date = request.form.get('scrap_date_2', '')
        
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

if __name__ == '__main__':
    app.run(debug=True)
