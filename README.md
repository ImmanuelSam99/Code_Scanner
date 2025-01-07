# QR Scanner Web Application

This project is a Flask-based web application designed to scan QR codes, barcodes, and text using a camera. The scanned data is stored in an Excel file, allowing for easy management, updates, and exports. The application is optimized for mobile devices and supports HTTPS.

---

## Features

1. **Scan Support**:
   - QR Codes
   - Barcodes
   - Alphanumeric text using PaddleOCR

2. **Data Management**:
   - Stores scanned data in an Excel file with columns:
     - `Serial Number`
     - `Code`
     - `Quantity`
     - `Type` (QR, Barcode, or Text)
   - Automatically assigns a serial number to new entries.

3. **Update and Delete**:
   - If a scanned code matches an existing entry, the app prompts the user to update the entry.
   - Entries can also be deleted as needed.

4. **Mobile Optimization**:
   - Responsive design for mobile devices.
   - HTTPS support for secure connections.

5. **Excel Export**:
   - Users can download the scanned data in CSV format.

6. **Camera Features**:
   - Green highlight over detected text.
   - Select text within the camera boundary.

---

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment tool (optional but recommended)

### Dependencies
Install the required dependencies using pip:
```bash
pip install -r requirements.txt
```
The `requirements.txt` file includes:
- Flask
- pandas
- openpyxl
- PaddleOCR

### SSL Setup
Ensure your SSL certificates (`cert.pem` and `key.pem`) are placed in the `ssl/` folder.

### Excel File
Create an initial Excel file (`data.xlsx`) with the following headers:
- `Serial Number`
- `Code`
- `Quantity`
- `Type`

---

## Usage

### Run the Application
Start the Flask app locally:
```bash
python app.py
```

### Access the Application
Open your browser and navigate to:
```
https://localhost:5000
```

---

## File Structure
```
.
├── app.py                # Main application file
├── templates/            # HTML templates
│   ├── index.html        # Main dashboard
│   ├── update.html       # Update entry page
├── static/               # Static assets (CSS, JS)
├── ssl/                  # SSL certificates
│   ├── cert.pem          # SSL certificate
│   ├── key.pem           # SSL private key
├── data.xlsx             # Excel file to store scanned data
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## API Endpoints

### `/` (Index Page)
- Displays the dashboard.
- Allows downloading data in CSV format.

### `/process_scan/<scan_type>` (POST)
- Handles scanning for `qr`, `barcode`, or `text`.
- Adds a new entry or redirects to update if the code already exists.

### `/update/<code>`
- Update an existing entry.

---

## Configuration

- **Excel File Location**: The file `data.xlsx` is the default storage for scanned data. Ensure it's in the root directory.
- **HTTPS**: Place SSL certificates in the `ssl/` directory to enable secure connections.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature/bug fix.
3. Commit your changes.
4. Submit a pull request.

---


---

## Acknowledgments
- [Flask](https://flask.palletsprojects.com/) for the web framework.
- [Pandas](https://pandas.pydata.org/) for data manipulation.
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) for text detection and recognition.
