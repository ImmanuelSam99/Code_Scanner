import os
import uuid
import pandas as pd
import base64
import random
import string
import numpy as np
import pytz
from datetime import datetime
from fuzzywuzzy import process, fuzz
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file
from urllib.parse import unquote, quote
import cv2
import pytesseract

app = Flask(__name__)
app.secret_key = '12345678'
oman_tz = pytz.timezone("Asia/Muscat")

EXCEL_FILE = 'data/qr_data.xlsx'
SKU_FILE = 'data/sku.xlsx'
BACKUP_FOLDER = "data/backup"

if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=['Serial Number', 'Code', 'Quantity', 'Type', 'Material', 'Description', 'Added By'])
    df.to_excel(EXCEL_FILE, index=False)

sku_df = pd.read_excel('data/sku.xlsx')

def load_sku_file():
    global sku_df
    if os.path.exists(SKU_FILE):
        sku_df = pd.read_excel(SKU_FILE)
    else:
        sku_df = pd.DataFrame(columns=['code', 'Material', 'description'])

load_sku_file()

def generate_serial_number():
    """
    Generate the next sequential serial number.
    """
    df = pd.read_excel(EXCEL_FILE)
    if df.empty:
        return 1
    else:
        return df['Serial Number'].max() + 1
    




def find_best_match(text, choices):
    best_match, score = process.extractOne(text, choices, scorer=fuzz.ratio)
    return best_match if score > 99 else best_match

def preprocess_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    denoised = cv2.fastNlMeansDenoising(threshold)
    return denoised

def clean_text(text):
    cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text)
    return cleaned_text

@app.route('/download_csv')
def download_csv():
    df = pd.read_excel(EXCEL_FILE)
    csv_filename = 'database.csv'
    df.to_csv(csv_filename, index=False)
    return send_file(csv_filename, as_attachment=True, download_name=csv_filename)

@app.route('/')
def index():
    user = request.args.get('user', '').strip()  
    df = pd.read_excel(EXCEL_FILE)
    
    if user:
        df = df[df['Added By'].str.strip() == user]
    
    return render_template('index.html', records=df.to_dict(orient='records'), user=user)

@app.route('/scan/<scan_type>')
def scan(scan_type):
    if scan_type not in ['qr', 'barcode', 'text']:
        return redirect(url_for('index'))
    
    user = request.args.get('user', '').strip()
    
    return render_template(f'scan_{scan_type}.html', scan_type=scan_type, user=user)

@app.route('/scans')
def get_scans_by_user():
    user = request.args.get('user', '').strip() 
    df = pd.read_excel(EXCEL_FILE)
    
    if user:
        df = df[df['Added By'].str.strip() == user]
    
    df = df.fillna('')
    
    result = df.to_dict(orient='records')
    return jsonify(result)

@app.route('/process_text_scan', methods=["POST"])
def process_text_scan():
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
        text = pytesseract.image_to_string(processed_img).strip()

        if not text:
            return jsonify({"status": "error", "message": "No text detected"}), 400

        cleaned_text = clean_text(text)

        # Dictionary matching with SKU file
        if sku_df is not None and not sku_df.empty:
            choices = sku_df['Code'].astype(str).tolist()
            corrected_text = find_best_match(cleaned_text, choices)

            match = sku_df[sku_df['Code'] == corrected_text]
            if not match.empty:
                material = match.iloc[0]['Material']
                description = match.iloc[0]['Description']
            else:
                material, description = None, None
        else:
            corrected_text, material, description = cleaned_text, None, None

        return jsonify({
            "status": "success",
            "code": corrected_text,
            "material": material,
            "description": description
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/check_code_exists', methods=["POST"])
def check_code_exists():
    try:
        data = request.get_json()
        scanned_code = data.get('code', '').strip()
        
        if not scanned_code:
            return jsonify({"exists": False, "message": "No code provided"}), 400
            
        df = pd.read_excel(EXCEL_FILE)
        
        if scanned_code in df['Code'].values:
            return jsonify({
                "exists": True,
                "redirect": url_for('update_page', code=quote(scanned_code))
            })
        else:
            return jsonify({"exists": False})
            
    except Exception as e:
        return jsonify({"exists": False, "message": str(e)}), 500

@app.route('/process_scan/<scan_type>', methods=["POST"])
def process_scan(scan_type):
    try:
        if scan_type not in ['qr', 'barcode', 'text']:
            return jsonify({"status": "error", "message": "Invalid scan type"}), 400

        data = request.get_json()
        scanned_code = data.get('code', '').strip()
        quantity = int(data.get('quantity', 1))
        user = data.get('user', 'Unknown')
        material = data.get('material')
        description = data.get('description')

        if not scanned_code:
            return jsonify({"status": "error", "message": f"Invalid {scan_type} scanned"}), 400

        # Determine the record type based on scan_type
        if scan_type == 'barcode':
            record_type = 'Barcode'
        elif scan_type == 'qr':
            record_type = 'QR Code'
        else:
            record_type = 'Text'

        # Get material and description from SKU if available
        if sku_df is not None and not sku_df.empty:
            match = sku_df[sku_df['Code'] == scanned_code]
            if not match.empty:
                material = match.iloc[0]['Material']
                description = match.iloc[0]['Description']

        df = pd.read_excel(EXCEL_FILE)

        # Check if code exists (case insensitive)
        existing_entry = df[df['Code'].str.strip().str.lower() == scanned_code.lower()]
        if not existing_entry.empty:
            existing_entry = existing_entry.iloc[0]
            return jsonify({
                "status": "exists",
                "redirect": url_for('update_page', code=quote(scanned_code)),
                "quantity": int(existing_entry['Quantity']),
                "material": material,
                "description": description,
                "Added By": user
            })

        serial_number = generate_serial_number()

        new_entry = pd.DataFrame({
            'Serial Number': [serial_number],
            'Code': [scanned_code],
            'Material': [material],
            'Quantity': [quantity],
            'Type': [record_type],  # This now uses the correct type
            'Description': [description],
            'Added By': [user],
        })

        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_excel(EXCEL_FILE, index=False)

        return jsonify({
            "status": "added",
            "serial_number": int(serial_number),
            "material": material,
            "description": description,
            "type": record_type  # Return the type for confirmation
        })
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
    try:
        code = unquote(code).strip()

        df = pd.read_excel(EXCEL_FILE)

        df['Code'] = df['Code'].astype(str).str.strip()

        mask = df['Code'] == code

        if mask.any():
            df = df[~mask]

            df['Serial Number'] = range(1, len(df) + 1)

            df.to_excel(EXCEL_FILE, index=False)

            flash('Entry deleted successfully', 'success')
        else:
            flash('Code not found', 'danger')

    except Exception as e:
        flash(f'Error deleting entry: {str(e)}', 'danger')

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
                             code_type=entry['Type'],
                             material=entry['Material'],
                             description=entry['Description'])
    flash('Code not found', 'danger')
    return redirect(url_for('index'))

@app.route('/delete_all', methods=["POST"])
def delete_all():
    try:
        os.makedirs(BACKUP_FOLDER, exist_ok=True)    
        df = pd.read_excel(EXCEL_FILE)

        if df.empty:
            flash("No data to back up. File is already empty.", "info")
            return redirect(url_for('index'))
        timestamp = datetime.now(oman_tz).strftime("%Y-%m-%d_%H-%M-%S")
        backup_file = os.path.join(BACKUP_FOLDER, f"backup_{timestamp}.xlsx")
        df.to_excel(backup_file, index=False)
        df = df[0:0]
        df.to_excel(EXCEL_FILE, index=False)

        flash(f"Backup saved as {backup_file}. All entries deleted.", "success")
        return redirect(url_for('index'))

    except Exception as e:
        flash(f"Error deleting data: {str(e)}", "danger")
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True, ssl_context=('ssl/cert.pem', 'ssl/key.pem'))