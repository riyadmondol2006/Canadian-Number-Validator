
# Canadian Number Validator

**Canadian Number Validator** is a Python-based utility with a web interface to validate phone numbers stored in an Excel file. The tool allows you to upload an Excel file through a user-friendly web interface, processes the numbers, and provides validation results.

---

## Features
- Web-based interface for uploading Excel files and viewing results.
- Validates phone numbers for proper Canadian formats (e.g., +1-XXX-XXX-XXXX or 1-XXX-XXX-XXXX).
- Displays validation results, including valid and invalid numbers, directly in the web UI.
- Allows downloading a detailed report after validation.

---

## Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Supported Excel formats: `.xlsx`, `.xls`

---

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/riyadmondol2006/canadian-number-validator.git
   cd canadian-number-validator
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Start the Web Interface**:  
   Run the script to start the web server:
   ```bash
   python phone-validator-webapp.py
   ```

2. **Access the Web UI**:  
   Open your browser and go to:
   ```
   http://localhost:5000
   ```

3. **Upload and Validate**:
   - Upload your Excel file containing phone numbers.
   - View validation results directly in the interface.
   - Download a detailed report (`validation_report.xlsx`).

---

## Directory Structure
```
canadian-number-validator/
    ├── phone-validator-webapp.py   # Starts the web server and handles validation logic
    ├── requirements.txt            # Dependencies list
    ├── README.md                   # Documentation
    ├── templates/                  # HTML templates for the web UI
    ├── static/                     # Static assets (CSS, JS, images)
    ├── utils.py                    # Helper functions
    ├── example.xlsx                # Example input file
    ├── validation_report.xlsx      # Example output report (generated dynamically)
```

---

## Contributing
Contributions are welcome! Feel free to:
1. Fork the repository.
2. Create a branch for your feature or fix.
3. Submit a pull request.

---

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
