from flask import Flask, render_template, request, send_file, send_from_directory, redirect, url_for, flash
import pandas as pd
import numpy as np
import re
from collections import defaultdict
from pathlib import Path
import os
import io
import zipfile
from datetime import datetime
import shutil

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Define Canadian area codes by province/territory
PROVINCE_CODES = {
    'Alberta': ['403', '587', '780', '825'],
    'British_Columbia': ['236', '250', '604', '672', '778'],
    'Manitoba': ['204', '431'],
    'New_Brunswick': ['506'],
    'Newfoundland_and_Labrador': ['709', '782'],
    'Northwest_Territories': ['867'],
    'Nova_Scotia': ['782', '902'],
    'Ontario': ['249', '289', '343', '365', '416', '437', '519', '548', '613', '647', '705', '742', '905', '807'],
    'Prince_Edward_Island': ['782', '902'],
    'Quebec': ['418', '438', '450', '514', '579', '581', '819', '873'],
    'Saskatchewan': ['306', '639'],
    'Yukon': ['867'],
    'Nunavut': ['867']
}

def convert_to_integer(value):
    try:
        if isinstance(value, str) and ('e' in value.lower() or 'E' in value):
            return int(float(value))
        return int(value)
    except (ValueError, TypeError):
        return None

def get_province_from_area_code(area_code):
    provinces = []
    for province, codes in PROVINCE_CODES.items():
        if area_code in codes:
            provinces.append(province)
    return provinces

def is_valid_canadian_number(number):
    valid_area_codes = set()
    for codes in PROVINCE_CODES.values():
        valid_area_codes.update(codes)
    
    try:
        num_str = str(number)
        num_str = re.sub(r'\D', '', num_str)
        
        if len(num_str) != 11:
            return False, "incorrect_length", None
        
        if not num_str.startswith('1'):
            return False, "not_starting_with_1", None
        
        area_code = num_str[1:4]
        if area_code not in valid_area_codes:
            return False, "invalid_area_code", None
            
        return True, "valid", area_code
        
    except (ValueError, TypeError):
        return False, "invalid_format", None

def process_excel_file(file):
    # Create a unique output directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = Path(f"static/output_{timestamp}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stats = {
        'total_numbers': 0,
        'valid_numbers': 0,
        'invalid_numbers': 0,
        'failure_reasons': defaultdict(int),
        'province_counts': defaultdict(int),
        'timestamp': timestamp
    }
    
    province_numbers = defaultdict(list)
    
    # Read Excel file
    df = pd.read_excel(file)
    numbers = df.iloc[:, 0]
    stats['total_numbers'] = len(numbers)
    
    # Process numbers
    for num in numbers:
        converted_num = convert_to_integer(num)
        
        if converted_num is None:
            stats['failure_reasons']['non_numeric'] += 1
            continue
            
        is_valid, reason, area_code = is_valid_canadian_number(converted_num)
        if is_valid:
            stats['valid_numbers'] += 1
            provinces = get_province_from_area_code(area_code)
            for province in provinces:
                province_numbers[province].append(converted_num)
                stats['province_counts'][province] += 1
        else:
            stats['failure_reasons'][reason] += 1
    
    stats['invalid_numbers'] = stats['total_numbers'] - stats['valid_numbers']
    
    # Save province-specific files
    for province, numbers in province_numbers.items():
        province_df = pd.DataFrame(numbers, columns=['Phone_Numbers'])
        province_df['Phone_Numbers'] = province_df['Phone_Numbers'].astype(str)
        filename = output_dir / f"{province}_Numbers.xlsx"
        province_df.to_excel(filename, index=False)
    
    # Create ZIP file
    zip_path = output_dir / 'all_provinces.zip'
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for file in output_dir.glob('*_Numbers.xlsx'):
            zipf.write(file, file.name)
    
    return stats

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file uploaded')
            return redirect(request.url)
            
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
            
        if not file.filename.endswith('.xlsx'):
            flash('Please upload an Excel file (.xlsx)')
            return redirect(request.url)
        
        try:
            stats = process_excel_file(file)
            return redirect(url_for('results', timestamp=stats['timestamp']))
        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(request.url)
    
    return render_template('index.html')

@app.route('/results/<timestamp>')
def results(timestamp):
    output_dir = Path(f"static/output_{timestamp}")
    if not output_dir.exists():
        flash('Results not found')
        return redirect(url_for('index'))
    
    return render_template(
        'results.html',
        timestamp=timestamp,
        download_url=url_for('download_zip', timestamp=timestamp)
    )

@app.route('/download/<timestamp>')
def download_zip(timestamp):
    zip_path = f"static/output_{timestamp}/all_provinces.zip"
    return send_file(zip_path, as_attachment=True)

# Cleanup old files (run periodically)
def cleanup_old_files():
    base_dir = Path('static')
    for item in base_dir.glob('output_*'):
        if item.is_dir():
            # Remove directories older than 24 hours
            age = datetime.now() - datetime.fromtimestamp(item.stat().st_mtime)
            if age.days >= 1:
                shutil.rmtree(item)

if __name__ == '__main__':
    os.makedirs('static', exist_ok=True)
    app.run(debug=True)
