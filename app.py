import os
import uuid
import pandas as pd
import base64
import random
import string
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from urllib.parse import unquote, quote
import unicodedata
import cv2
import pytesseract

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_12345'
EXCEL_FILE = 'data/qr_data.xlsx'

if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=['Serial Number', 'Code', 'Quantity', 'Type'])
    df.to_excel(EXCEL_FILE, index=False)

def generate_serial_number():
    """Generate a unique and human-readable Serial Number."""
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return random_str

def preprocess_image(img):
    """Preprocess image for better OCR results.""" 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(threshold)
    return denoised

@app.route('/download_csv')
def download_csv():
    df = pd.read_excel(EXCEL_FILE)
    csv_filename = 'database.csv'
    df.to_csv(csv_filename, index=False)
    return send_file(csv_filename, as_attachment=True, download_name=csv_filename)

@app.route('/')
def index():
    df = pd.read_excel(EXCEL_FILE)
    return render_template('index.html', records=df.to_dict(orient='records'))

@app.route('/scan/<scan_type>')
def scan(scan_type):
    if scan_type not in ['qr', 'barcode', 'text']:
        return redirect(url_for('index'))
    return render_template(f'scan_{scan_type}.html', scan_type=scan_type)

@app.route('/process_text_scan', methods=["POST"])
def process_text_scan():
    """Process text scanning using Tesseract."""
    try:
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({"status": "error", "message": "No image data provided"}), 400
        image_data = data['image']
        if 'data:image' in image_data:
            image_data = image_data.split(',')[1]

        nparr = np.frombuffer(base64.b64decode(image_data), np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            return jsonify({"status": "error", "message": "Invalid image data"}), 400

        processed_img = preprocess_image(img)

        text = pytesseract.image_to_string(processed_img)
        text = text.strip()

        if not text:
            return jsonify({"status": "error", "message": "No text detected"}), 400

        return jsonify({
            "status": "success",
            "code": text  
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/process_scan/<scan_type>', methods=["POST"])
def process_scan(scan_type):
    """Handle scanning logic for QR code, barcode, or text."""
    try:
       
        if scan_type not in ['qr', 'barcode', 'text']:
            return jsonify({"status": "error", "message": "Invalid scan type"}), 400

        
        data = request.get_json()
        scanned_code = data.get('code', '').strip()

        if not scanned_code:
            return jsonify({"status": "error", "message": f"Invalid {scan_type} scanned"}), 400

        
        if scan_type != 'text':
            scanned_code = scanned_code.strip().lower()
        else:
            scanned_code = scanned_code.strip()

        
        df = pd.read_excel(EXCEL_FILE)

        
        required_columns = ['Serial Number', 'Code', 'Quantity', 'Type']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"status": "error", "message": "Database file is corrupted"}), 500

        
        if scan_type != 'text':
            df['Code'] = df['Code'].apply(lambda x: x.strip().lower() if isinstance(x, str) else x)
        else:
            df['Code'] = df['Code'].apply(lambda x: x.strip() if isinstance(x, str) else x)

        
        if scanned_code in df['Code'].values:
            existing_entry = df.loc[df['Code'] == scanned_code].iloc[0]
            flash(f"The {scan_type} '{scanned_code}' already exists. Redirecting to the update page.", 'info')
            return jsonify({
                "status": "exists",
                "redirect": url_for('update_page', code=quote(scanned_code)),  # Avoid double-quoting
                "quantity": int(existing_entry['Quantity'])
            })

        
        serial_number = generate_serial_number()
        new_entry = pd.DataFrame({
            'Serial Number': [serial_number],
            'Code': [scanned_code],
            'Type': [scan_type.capitalize()],
            'Quantity': [1]
        })
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        return jsonify({"status": "added", "serial_number": serial_number})

    except Exception as e:
        
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update', methods=["POST"])
def update_quantity():
    qr_code = request.form['qr_code']
    action = request.form['action']
    quantity = int(request.form['quantity']) if 'quantity' in request.form else None

    df = pd.read_excel(EXCEL_FILE)

    if qr_code in df['Code'].values:
        if action == "increment":
            df.loc[df['Code'] == qr_code, 'Quantity'] += 1
        elif action == "update" and quantity is not None:
            df.loc[df['Code'] == qr_code, 'Quantity'] = quantity

    df.to_excel(EXCEL_FILE, index=False)
    return redirect(url_for('index'))

@app.route('/delete/<path:code>', methods=["POST"])
def delete(code):
    
    code = unquote(code).strip()  
    
    
    df = pd.read_excel(EXCEL_FILE)

    
    df['Code'] = df['Code'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    
    mask = df['Code'].apply(lambda x: x == code if isinstance(x, str) else False)
    if mask.any():
        df = df[~mask]  
        df.to_excel(EXCEL_FILE, index=False)
        flash('Entry deleted successfully', 'success')
    else:
        flash('Code not found', 'danger')

    return redirect(url_for('index'))

@app.route('/update_page/<path:code>', methods=["GET", "POST"])
def update_page(code):
    
    code = unquote(code).strip()  
    
    
    df = pd.read_excel(EXCEL_FILE)

    
    df['Code'] = df['Code'].apply(lambda x: x.strip() if isinstance(x, str) else x)
    
    
    mask = df['Code'].apply(lambda x: x == code if isinstance(x, str) else False)
    if mask.any():
        entry = df[mask].iloc[0]
        return render_template('update.html', 
                             qr_code=entry['Code'],
                             quantity=entry['Quantity'],
                             code_type=entry['Type'])

    flash('Code not found', 'danger')
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))

