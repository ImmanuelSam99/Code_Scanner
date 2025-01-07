
# QR Scanner App

This is a Flask-based QR Scanner application designed for mobile devices. It scans QR codes, barcodes, and alphanumeric text and stores the data in an Excel file. The app supports adding, updating, and deleting entries, with HTTPS support for secure access.

---

## Features

1. **QR Code, Barcode, and Text Scanning**
   - Supports scanning of QR codes, barcodes, and single-line alphanumeric text.
   - Automatically categorizes scanned input as 'QR', 'Barcode', or 'Text'.

2. **Text Highlighting and Selection**
   - Scanned text is highlighted in green.
   - Allows manual selection of the scanned text.

3. **Excel Integration**
   - Stores scanned data in an Excel file with the following columns:
     - Serial Number (SNO)
     - Code
     - Quantity
     - Type (QR, Barcode, or Text)

4. **Data Management**
   - Prompts user to update an entry if a duplicate is found.
   - Allows manual input of quantity for new entries.
   - Features delete and update functionality.

5. **Mobile-Friendly Interface**
   - Optimized for mobile devices.
   - Includes a camera boundary for focusing on single-line text.

6. **Secure Access**
   - Runs over HTTPS with SSL certificate support.

7. **File Download**
   - Allows downloading of the Excel file as a CSV from the index page.

---

## Prerequisites

1. **Python Libraries**
   - Flask
   - OpenCV
   - pandas
   - Tesseract OCR (`pytesseract`)

2. **External Tools**
   - [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

3. **SSL Certificates**
   - Place your SSL certificates in an `ssl` folder in the project directory.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-name/qr-scanner-app.git
   cd qr-scanner-app
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:
   - Refer to the [Tesseract OCR installation guide](https://github.com/tesseract-ocr/tesseract).

5. Place your SSL certificates in the `ssl` folder.

---

## Usage

1. Run the Flask app:
   ```bash
   flask run --host=0.0.0.0 --port=5000
   ```

2. Access the app on your mobile device using:
   ```
   https://<your-ip-address>:5000
   ```

3. Use the interface to scan QR codes, barcodes, or text.

4. Download the stored data in CSV format from the index page.

---

## File Structure

```
qr-scanner-app/
├── app.py             # Main application file
├── templates/         # HTML templates
├── static/            # CSS and JavaScript files
├── ssl/               # SSL certificates
├── utils/             # Utility scripts and logs
├── data/              # Directory for storing Excel files
├── requirements.txt   # Python dependencies
└── README.md          # Project documentation
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

---

## Contributing

Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.
