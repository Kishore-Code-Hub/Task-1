from flask import Flask, render_template, request, redirect, url_for, flash
import hashlib
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
HASHES_FOLDER = 'hashes'

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HASHES_FOLDER, exist_ok=True)

def calculate_hash(filepath: str, algo: str = 'sha256') -> str:
    """Calculate the hash of a file using the given algorithm."""
    hash_func = hashlib.new(algo)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    
    if not file or not file.filename:
        flash("No file uploaded.")
        return redirect(url_for('index'))

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    current_hash = calculate_hash(filepath)
    hash_filename = filename + '.hash'
    hash_file_path = os.path.join(HASHES_FOLDER, hash_filename)

    if os.path.exists(hash_file_path):
        with open(hash_file_path, 'r') as f:
            original_hash = f.read().strip()

        if current_hash == original_hash:
            status = "✅ File is intact. No changes detected."
        else:
            status = "⚠️ File has been modified!"
    else:
        with open(hash_file_path, 'w') as f:
            f.write(current_hash)
        status = "✅ File uploaded and hash saved for future checks."

    return render_template('result.html', filename=filename, current_hash=current_hash, status=status)

if __name__ == '__main__':
    app.run(debug=True)
