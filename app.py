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
        # --- 1. 接收表單資料 (對應 index.html 的 name 屬性) ---
        VehicleRegistrationMark = request.form.get('VehicleRegistrationMark', '')
        EngName = request.form.get('EngName', '')
        ChiName = request.form.get('ChiName', '')
        HKID = request.form.get('HKID', '')
        HKID2 = request.form.get('HKID2', '') # 可能是商業登記號碼部分
        company_contact = request.form.get('company_contact', '')
        
        # 地址部分
        flat = request.form.get('flat', '')
        floor = request.form.get('floor', '')
        blk = request.form.get('blk', '')
        building = request.form.get('building', '')
        street = request.form.get('street', '')
        district = request.form.get('district', '')
        
        # 地區勾選 (如果網頁傳來的是 'on' 或 'true'，則填寫 'X' 或打勾符號，否則留空)
        hk = 'X' if request.form.get('hk') else ''
        kl = 'X' if request.form.get('kl') else ''
        nt = 'X' if request.form.get('nt') else ''
        
        # 車輛詳情
        registration_class = request.form.get('registration_class', '')
        ChassisOrVin = request.form.get('ChassisOrVin', '')
        
        # 原因勾選
        C_A = 'X' if request.form.get('C_A') else '' # 假設這是 "拆毀" 的選項
        
        Date = request.form.get('Date', '')

        # --- 2. 寫入 PDF (使用你的坐標) ---
        # 為了美觀，可以設置字型 (ReportLab 默認不支援中文，若需中文需註冊字型，這裡先用默認)
        # can.setFont("Helvetica", 10) 

        can.drawString(409, page_height - 67, VehicleRegistrationMark)
        can.drawString(112, page_height - 134, EngName)
        can.drawString(125, page_height - 161, ChiName) # 注意：若輸入中文，需配置中文字型，否則會亂碼
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
        can.drawString(340, page_height - 735, Date)


    elif pdf_template_filename == 'target2.pdf':
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
